use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rayon::prelude::*;

#[pyclass]
struct ImageResizer {
    width: u32,
    height: u32,
    data: Vec<u8>,
}

#[pymethods]
impl ImageResizer {
    #[new]
    fn new(width: u32, height: u32, data: Vec<u8>) -> PyResult<Self> {
        if data.len() != (width * height * 4) as usize {
            return Err(PyValueError::new_err(
                "Data length must be width * height * 4 (RGBA format)"
            ));
        }
        Ok(ImageResizer { width, height, data })
    }

    fn resize(&self, new_width: u32, new_height: u32) -> PyResult<(u32, u32, Vec<u8>)> {
        if new_width == 0 || new_height == 0 {
            return Err(PyValueError::new_err(
                "New dimensions must be greater than 0"
            ));
        }

        let old_width = self.width;
        let old_height = self.height;
        let old_data = &self.data;

        let x_ratio = old_width as f32 / new_width as f32;
        let y_ratio = old_height as f32 / new_height as f32;

        let new_size = (new_width * new_height * 4) as usize;
        let mut new_data: Vec<u8> = vec![0; new_size];

        new_data
            .par_chunks_mut((new_width * 4) as usize)
            .enumerate()
            .for_each(|(y, row)| {
                let src_y = ((y as f32) * y_ratio) as u32;
                let src_y = src_y.min(old_height - 1);
                let src_row_offset = (src_y * old_width * 4) as usize;

                for x in 0..new_width as usize {
                    let src_x = ((x as f32) * x_ratio) as u32;
                    let src_x = src_x.min(old_width - 1);
                    let src_offset = src_row_offset + (src_x * 4) as usize;
                    let dst_offset = x * 4;

                    row[dst_offset] = old_data[src_offset];
                    row[dst_offset + 1] = old_data[src_offset + 1];
                    row[dst_offset + 2] = old_data[src_offset + 2];
                    row[dst_offset + 3] = old_data[src_offset + 3];
                }
            });

        Ok((new_width, new_height, new_data))
    }

    #[getter]
    fn width(&self) -> u32 {
        self.width
    }

    #[getter]
    fn height(&self) -> u32 {
        self.height
    }

    #[getter]
    fn data(&self) -> Vec<u8> {
        self.data.clone()
    }
}

#[pyfunction]
fn resize_image_file(input_path: &str, new_width: u32, new_height: u32) -> PyResult<(u32, u32, Vec<u8>)> {
    let img = image::open(input_path)
        .map_err(|e| PyValueError::new_err(format!("Failed to open image: {}", e)))?
        .to_rgba8();

    let (width, height) = img.dimensions();
    let data = img.to_vec();

    let resizer = ImageResizer::new(width, height, data)?;
    resizer.resize(new_width, new_height)
}

#[pyfunction]
fn load_image(path: &str) -> PyResult<ImageResizer> {
    let img = image::open(path)
        .map_err(|e| PyValueError::new_err(format!("Failed to open image: {}", e)))?
        .to_rgba8();

    let (width, height) = img.dimensions();
    let data = img.to_vec();

    ImageResizer::new(width, height, data)
}

#[pymodule]
fn image_resize(m: &Bound<'_, PyModule>) -> PyResult<()> { 
    m.add_class::<ImageResizer>()?;
    m.add_function(wrap_pyfunction!(resize_image_file, m)?)?;
    m.add_function(wrap_pyfunction!(load_image, m)?)?;
    Ok(())
}