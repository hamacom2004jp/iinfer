from iinfer.app import common
from iinfer.app import predict, injection
from pathlib import Path
from PIL import Image
import base64
import os
import numpy as np


def test_01_01_load_config():
    logger, _ = common.load_config("client")
    assert logger.name == 'client'
    logger, _ = common.load_config("gui")
    assert logger.name == 'gui'
    logger, _ = common.load_config("postprocess")
    assert logger.name == 'postprocess'
    logger, _ = common.load_config("server")
    assert logger.name == 'server'
    logger, _ = common.load_config("redis")
    assert logger.name == 'redis'
    logger, _ = common.load_config("install")
    assert logger.name == 'install'

def test_02_01_saveopt_loadopt():
    p = Path("test_02_01_saveopt_loadopt.json")
    common.saveopt(dict(test=Path("test")), p)
    d = common.loadopt(p)
    assert d["test"] == "test"
    os.remove(p)

def test_03_01_getopt():
    opt_base = dict(test1="base", test2="base2")
    opt_args = dict(test1="args")
    ret = common.getopt(opt_base, 'test1', preval=opt_args, defval="defval", withset=False)
    assert ret == "args"
    ret = common.getopt(opt_base, 'test2', preval=opt_args, defval="defval", withset=False)
    assert ret == "defval"
    ret = common.getopt(opt_base, 'test3', preval=opt_args, defval="defval", withset=False)
    assert ret == "defval"
    ret = common.getopt(opt_base, 'test1', preval=None, defval="defval", withset=False)
    assert ret == "base"
    ret = common.getopt(opt_base, 'test2', preval=None, defval="defval", withset=False)
    assert ret == "base2"
    ret = common.getopt(opt_base, 'test3', preval=None, defval="defval", withset=False)
    assert ret == "defval"
    ret = common.getopt(opt_base, 'test3', preval=opt_args, defval="defval", withset=True)
    assert opt_base["test3"] == "defval"

def test_04_01_mkdirs():
    dir_path1 = Path("test_dir")
    dir_path2 = dir_path1 / "test_04_01_mkdirs"
    common.mkdirs(dir_path2)
    assert os.path.exists(dir_path2)
    assert os.path.isdir(dir_path2)
    common.rmdirs(dir_path1)
    assert not os.path.exists(dir_path2)
    assert not os.path.exists(dir_path1)

def test_05_01_load_custom_predict():
    custom_predict_py = Path("iinfer/app/predicts/onnx_det_YoloX.py")
    logger, _ = common.load_config("server")
    result = common.load_custom_predict(custom_predict_py, logger)
    assert result is not None
    assert isinstance(result, predict.Predict)

def test_06_01_load_predict():
    logger, _ = common.load_config("server")
    result = common.load_predict('onnx_det_YoloX', logger)
    assert result is not None
    assert isinstance(result, predict.Predict)

def test_07_01_download_file():
    url = "https://example.com/image.jpg"
    save_path = Path("image.jpg")
    res = common.download_file(url, save_path)
    assert os.path.exists(res)
    assert os.path.isfile(res)
    assert os.path.getsize(res) > 0
    os.remove(res)

def test_08_01_npyfile2npy():
    temp_file = Path("temp.npy")
    np.save(temp_file, np.array([1, 2, 3]))
    result = common.npyfile2npy(temp_file)
    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, np.array([1, 2, 3]))
    os.remove(temp_file)

def test_09_01_npybytes2npy():
    temp_file = Path("temp.npy")
    np.save(temp_file, np.array([1, 2, 3]))
    with open(temp_file, "rb") as f:
        npy_bytes = f.read()
        result = common.npybytes2npy(npy_bytes)
    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, np.array([1, 2, 3]))
    os.remove(temp_file)

def test_10_01_npy2b64str():
    arr = np.array([1, 2, 3])
    result = common.npy2b64str(arr)
    assert isinstance(result, str)
    assert result == base64.b64encode(arr.tobytes()).decode('utf-8')

def test_11_01_npy2img():
    arr = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    img = common.npy2img(arr)
    assert isinstance(img, Image.Image)
    assert img.size == (3, 3)
    assert np.array_equal(np.array(img), arr)

def test_12_01_b64str2bytes():
    b64str = "SGVsbG8gd29ybGQ="
    result = common.b64str2bytes(b64str)
    assert isinstance(result, bytes)
    assert result == base64.b64decode(b64str.encode('utf-8'))

def test_13_01_b64str2npy():
    b64str = "AAECAw=="
    result = common.b64str2npy(b64str)
    expected = np.array([0, 1, 2, 3])
    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, expected)

def test_14_01_npy2imgfile():
    arr = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    output_image_file = Path("output.jpg")
    result = common.npy2imgfile(arr, output_image_file, image_type="jpeg")
    assert isinstance(result, bytes)
    assert output_image_file.exists()
    os.remove(output_image_file)

def test_15_01_bgr2rgb():
    arr = np.array([[0, 0, 255], [0, 255, 0], [255, 0, 0]], dtype=np.uint8)
    result = common.bgr2rgb(arr)
    expected = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)
    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, expected)

def test_16_01_imgbytes2npy():
    img_path = Path("tests") / 'dog.jpg'
    img = Image.open(img_path)
    with open(img_path, "rb") as f:
        img_bytes = f.read()
        result = common.imgbytes2npy(img_bytes)
    assert isinstance(result, np.ndarray)
    assert np.array_equal(np.array(result), np.array(img))

def test_17_01_imgfile2npy():
    img_path = Path("tests") / 'dog.jpg'
    img = Image.open(img_path)
    result = common.imgfile2npy(img_path)
    assert isinstance(result, np.ndarray)
    assert np.array_equal(np.array(result), np.array(img))

def test_18_01_img2npy():
    img = Image.new('RGB', (100, 100), color='red')
    npy = common.img2npy(img)
    assert isinstance(npy, np.ndarray)
    assert npy.shape == (100, 100, 3)
    assert np.array_equal(npy, np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8))

def test_19_01_img2byte():
    img = Image.new('RGB', (100, 100), color='red')
    result = common.img2byte(img)
    assert isinstance(result, bytes)
    assert len(result) > 0

def test_20_01_str2b64str():
    s = "Hello, World!"
    result = common.str2b64str(s)
    expected = "SGVsbG8sIFdvcmxkIQ=="
    assert result == expected

def test_21_01_b64str2str():
    b64str = "SGVsbG8sIFdvcmxkIQ=="
    result = common.b64str2str(b64str)
    expected = "Hello, World!"
    assert result == expected

def test_22_01_draw_boxes():
    image = Image.new('RGB', (100, 100), color='white')
    boxes = [[0.1, 0.1, 0.9, 0.9]]
    scores = [0.9]
    classes = [0]
    ids = ['XXXXXXXX']
    labels = ['AAAAAAA']
    colors = [(255, 0, 0)]
    result, out_labels = common.draw_boxes(image, boxes, scores, classes, ids=ids, labels=labels, colors=colors)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    assert out_labels[0] == labels[0]

def test_23_01_load_before_injections():
    logger, _ = common.load_config("server")
    injection_py = Path("extensions/injection/before_grayimg_injection.py")
    result = common.load_before_injections([injection_py], None, logger)
    assert result is not None
    assert isinstance(result[0], injection.BeforeInjection)

def test_24_01_load_after_injections():
    logger, _ = common.load_config("server")
    injection_py = Path("extensions/injection/after_csv_injection.py")
    result = common.load_after_injections([injection_py], None, logger)
    assert result is not None
    assert isinstance(result[0], injection.AfterInjection)
