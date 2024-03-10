from iinfer.app.commons import convert
from io import BytesIO
from pathlib import Path
from PIL import Image
from unittest.mock import patch
import base64
import numpy as np
import os


def test_npyfile2npy():
    # Create a sample numpy array and save it to a .npy file
    np_array = np.array([1, 2, 3])
    np.save('test.npy', np_array)

    # Call the function
    loaded_array = convert.npyfile2npy('test.npy')

    # Check if the loaded array is correct
    assert np.array_equal(loaded_array, np_array)

    # Clean up
    os.remove('test.npy')

def test_npybytes2npy():
    # Create a sample numpy array and save it to a bytes object
    np_array = np.array([1, 2, 3])
    npy_bytes = BytesIO()
    np.save(npy_bytes, np_array)
    npy_bytes = npy_bytes.getvalue()

    # Call the function
    loaded_array = convert.npybytes2npy(npy_bytes)

    # Check if the loaded array is correct
    assert np.array_equal(loaded_array, np_array)

def test_npy2b64str():
    # Create a sample numpy array
    np_array = np.array([1, 2, 3])

    # Call the function
    encoded_str = convert.npy2b64str(np_array)

    # Check if the encoded string is correct
    expected_str = base64.b64encode(np_array.tobytes()).decode('utf-8')
    assert encoded_str == expected_str

def test_npy2img():
    # Create a sample numpy array
    np_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    # Call the function
    result_image = convert.npy2img(np_array)

    # Check if the result is an instance of Image.Image
    assert isinstance(result_image, Image.Image)

    # Check if the image data is correct
    assert np.array_equal(np.array(result_image), np_array)

def test_b64str2bytes():
    # Create a sample bytes object and encode it to a base64 string
    bytes_obj = b'sample bytes'
    b64str = base64.b64encode(bytes_obj).decode('utf-8')

    # Call the function
    decoded_bytes = convert.b64str2bytes(b64str)

    # Check if the decoded bytes are correct
    assert decoded_bytes == bytes_obj

def test_b64str2npy():
    # Call the function with shape
    np_array = np.array([[1, 2, 3], [4, 5, 6]])
    b64str = base64.b64encode(np_array.tobytes()).decode('utf-8')
    decoded_array = convert.b64str2npy(b64str, shape=(2, 3), dtype=np_array.dtype)
    # Check if the decoded array is correct
    assert np.array_equal(decoded_array, np_array)

def test_npy2imgfile():
    # Create a sample numpy array
    np_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    # Call the function without output_image_file
    img_byte = convert.npy2imgfile(np_array)
    # Check if the returned bytes are correct
    expected_image = Image.fromarray(np_array)
    expected_img_byte = convert.img2byte(expected_image, format='jpeg')
    assert img_byte == expected_img_byte

    # Call the function with output_image_file
    output_image_file = Path('test_image.jpeg')
    img_byte = convert.npy2imgfile(np_array, output_image_file=output_image_file)
    # Check if the returned bytes are correct
    assert img_byte == expected_img_byte
    # Check if the file was created and its content is correct
    with open(output_image_file, 'rb') as f:
        saved_img_byte = f.read()
    assert saved_img_byte == expected_img_byte

    # Clean up
    output_image_file.unlink()

def test_bytes2b64str():
    """
    このテストは、まずテスト用のバイト列を定義します。
    次に、bytes2b64str関数を使用してバイト列をBase64エンコードします。
    最後に、Base64エンコードされた文字列が正しいことを確認します。
    """
    # Create a sample bytes object
    bytes_obj = b'sample bytes'

    # Call the function
    b64str = convert.bytes2b64str(bytes_obj)

    # Check if the encoded string is correct
    expected_b64str = base64.b64encode(bytes_obj).decode('utf-8')
    assert b64str == expected_b64str

def test_bgr2rgb():
    """
    このテストでは、bgr2rgb関数が正しく動作することを確認します。
    まず、サンプルのBGR numpy配列を作成します。
    次に、関数を呼び出し、変換された配列が正しいことを確認します。
    """
    # Create a sample BGR numpy array
    bgr_array = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]]])  # Blue, Green, Red

    # Call the function
    rgb_array = convert.bgr2rgb(bgr_array)

    # Check if the converted array is correct
    expected_rgb_array = np.array([[[0, 0, 255], [0, 255, 0], [255, 0, 0]]])  # Red, Green, Blue
    assert np.array_equal(rgb_array, expected_rgb_array)

def test_imgfile2npy():
    """
    このテストでは、imgfile2npy関数が正しく動作することを確認します。
    まず、サンプルの画像ファイルを作成します。
    次に、関数を呼び出し、変換された配列が正しいことを確認します。
    最後に、テストで作成した画像ファイルを削除します。
    """
    # Create a sample image file
    img = Image.new('RGB', (60, 30), color = (73, 109, 137))
    img_path = Path('test_image.png')
    img.save(img_path)

    # Call the function
    np_array = convert.imgfile2npy(img_path)

    # Check if the converted array is correct
    expected_np_array = np.array(img)
    assert np.array_equal(np_array, expected_np_array)

    # Clean up
    img_path.unlink()

def test_img2npy():
    """
    このテストでは、img2npy関数が正しく動作することを確認します。
    まず、サンプルの画像を作成します。
    次に、関数を呼び出し、変換された配列が正しいことを確認します。
    これをデータ型指定ありとなしの2つのケースで行います。
    """
    # Create a sample image
    img = Image.new('RGB', (60, 30), color = (73, 109, 137))

    # Call the function
    np_array = convert.img2npy(img)

    # Check if the converted array is correct
    expected_np_array = np.array(img)
    assert np.array_equal(np_array, expected_np_array)

    # Call the function with dtype
    np_array = convert.img2npy(img, dtype='float32')

    # Check if the converted array is correct
    expected_np_array = np.array(img, dtype='float32')
    assert np.array_equal(np_array, expected_np_array)

def test_img2byte():
    """
    このテストはまず、numpyとPILを使用してランダムな画像を作成します。
    次に、img2byte関数を使用して画像をバイトに変換します。
    出力が実際にバイトであることを確認します。
    次に、バイトから画像を作成し、この画像が元の画像と同じであることを確認します。
    """
    # PILを使用してテスト画像を作成します
    img = Image.fromarray(np.uint8(np.random.rand(100, 100, 3) * 255))

    # あなたの関数を使用して画像をバイトに変換します
    img_bytes = convert.img2byte(img, format='png')

    # 出力が実際にバイトであることを確認します
    assert isinstance(img_bytes, bytes)

    # バイトから画像を作成します
    img_from_bytes = Image.open(BytesIO(img_bytes))

    # バイトから作成した画像が元の画像と同じであることを確認します
    assert np.allclose(np.array(img), np.array(img_from_bytes))

def test_str2b64str():
    """
    このテストは、まずテスト用の文字列を定義します。
    次に、str2b64str関数を使用して文字列をBase64エンコードします。
    最後に、Base64エンコードされた文字列が正しいことを確認します。
    """
    # テスト用の文字列を定義します
    test_str = "テスト文字列"

    # str2b64str関数を使用して文字列をBase64エンコードします
    encoded_str = convert.str2b64str(test_str)

    # Base64エンコードされた文字列が正しいことを確認します
    assert encoded_str == base64.b64encode(test_str.encode()).decode('utf-8')

def test_b64str2str():
    """
    このテストは、まずテスト用の文字列を定義します。
    次に、その文字列をBase64エンコードします。
    その後、b64str2str関数を使用してBase64エンコードされた文字列をデコードします。
    最後に、デコードされた文字列が元の文字列と一致することを確認します。
    """
    # テスト用の文字列を定義します
    test_str = "テスト文字列"

    # 文字列をBase64エンコードします
    b64str = base64.b64encode(test_str.encode()).decode('utf-8')

    # b64str2str関数を使用してBase64エンコードされた文字列をデコードします
    decoded_str = convert.b64str2str(b64str)

    # デコードされた文字列が元の文字列と一致することを確認します
    assert decoded_str == test_str

