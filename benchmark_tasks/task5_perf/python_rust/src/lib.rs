use pyo3::prelude::*;
use rayon::prelude::*;

fn matrix_multiply(a: &[Vec<f64>], b: &[Vec<f64>]) -> Vec<Vec<f64>> {
    let rows_a = a.len();
    let cols_a = a[0].len();
    let rows_b = b.len();
    let cols_b = b[0].len();

    if cols_a != rows_b {
        panic!("Incompatible matrix dimensions");
    }

    let mut result = vec![vec![0.0; cols_b]; rows_a];

    result.par_iter_mut().enumerate().for_each(|(i, row)| {
        for j in 0..cols_b {
            let mut sum = 0.0;
            for k in 0..cols_a {
                sum += a[i][k] * b[k][j];
            }
            row[j] = sum;
        }
    });

    result
}

fn matrix_transpose(matrix: &[Vec<f64>]) -> Vec<Vec<f64>> {
    let rows = matrix.len();
    let cols = matrix[0].len();
    let mut result = vec![vec![0.0; rows]; cols];

    for i in 0..rows {
        for j in 0..cols {
            result[j][i] = matrix[i][j];
        }
    }

    result
}


#[pyfunction]
fn compute_heavy(n: i32) -> PyResult<f64> {
    let n = n as usize;
    

    let a: Vec<Vec<f64>> = (0..n)
        .map(|i| (0..n).map(|j| (i + j) as f64).collect())
        .collect();
    
    let b: Vec<Vec<f64>> = (0..n)
        .map(|i| (0..n).map(|j| (i * j + 1) as f64).collect())
        .collect();


    let product = matrix_multiply(&a, &b);


    let transposed = matrix_transpose(&product);


    let total: f64 = transposed.iter().flatten().sum();

    Ok(total)
}

#[pymodule]
fn matrix_ops_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_heavy, m)?)?;
    Ok(())
}
