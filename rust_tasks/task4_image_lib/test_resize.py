import pytest
import image_resize
from PIL import Image
import os

@pytest.mark.parametrize("src_w, src_h, dst_w, dst_h", [
    (4, 4, 8, 8), (2, 2, 1, 1), (10, 10, 10, 10)
])
def test_resize_dimensions(src_w, src_h, dst_w, dst_h):
    data = [255] * (src_w * src_h * 4)
    resizer = image_resize.ImageResizer(src_w, src_h, data)
    new_w, new_h, new_data = resizer.resize(dst_w, dst_h)
    assert new_w == dst_w and new_h == dst_h
    assert len(new_data) == dst_w * dst_h * 4

def test_resize_data_integrity():
    data = [255, 255, 255, 255] * 1
    resizer = image_resize.ImageResizer(1, 1, data)
    _, _, new_data = resizer.resize(1, 1)
    assert list(new_data[:4]) == [255, 255, 255, 255]

def test_resize_invalid_input():
    resizer = image_resize.ImageResizer(2, 2, [0]*16)
    with pytest.raises(ValueError):
        resizer.resize(0, 5)

def test_load_image(tmp_path):
    path = tmp_path / "load_test.png"
    Image.new('RGBA', (32, 32), color='red').save(path)
    
    resizer = image_resize.load_image(str(path))
    assert resizer.width == 32
    assert resizer.height == 32

def test_resize_image_file(tmp_path):
    path = tmp_path / "file_test.png"
    Image.new('RGBA', (100, 100), color='green').save(path)
    
    w, h, data = image_resize.resize_image_file(str(path), 20, 20)
    assert w == 20 and h == 20
    assert len(data) == 20 * 20 * 4

def test_file_errors():
    with pytest.raises(Exception):
        image_resize.load_image("non_existent_file.png")

def test_visual_debug_and_save():
    input_filename = "debug_input.png"
    output_filename = "debug_output.png"

    img = Image.new('RGB', (100, 100))
    for x in range(100):
        for y in range(100):
            img.putpixel((x, y), (x * 2 % 256, y * 2 % 256, 128))
    img.save(input_filename)

    w, h, data = image_resize.resize_image_file(input_filename, 50, 50)
    
    img_out = Image.frombytes('RGBA', (w, h), bytes(data))
    img_out.save(output_filename)

    assert os.path.exists(output_filename)