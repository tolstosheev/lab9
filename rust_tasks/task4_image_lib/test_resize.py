import numpy as np
from PIL import Image
import image_resize


def test_resize_from_raw_data():
    width, height = 4, 4
    data = []
    for y in range(height):
        for x in range(width):
            r = int(255 * x / (width - 1)) 
            g = int(255 * y / (height - 1))  
            b = 128  
            a = 255 
            data.extend([r, g, b, a])
    
    resizer = image_resize.ImageResizer(width, height, data)
    
    new_w, new_h, new_data = resizer.resize(8, 8)
    assert new_w == 8 and new_h == 8
    assert len(new_data) == 8 * 8 * 4
    
    new_w, new_h, new_data = resizer.resize(2, 2)
    assert new_w == 2 and new_h == 2
    assert len(new_data) == 2 * 2 * 4


def test_resize_image_file():
    test_img = Image.new('RGB', (100, 100), color='red')
    for x in range(100):
        for y in range(100):
            test_img.putpixel((x, y), (x * 2 % 256, y * 2 % 256, 128))
    test_img.save('test_input.png')
    
    w, h, data = image_resize.resize_image_file('test_input.png', 50, 50)
    assert w == 50 and h == 50
    
    result_img = Image.frombytes('RGBA', (w, h), bytes(data))
    result_img.save('test_output.png')


def test_load_image():
    test_img = Image.new('RGB', (64, 64), color='blue')
    test_img.save('test_load.png')
    
    resizer = image_resize.load_image('test_load.png')

    w, h, data = resizer.resize(32, 32)
    assert w == 32 and h == 32


def test_performance():
    import time

    width, height = 1000, 1000
    data = [255] * (width * height * 4)
    
    resizer = image_resize.ImageResizer(width, height, data)
    
    start = time.perf_counter()
    for _ in range(10):
        resizer.resize(500, 500)
    elapsed = time.perf_counter() - start