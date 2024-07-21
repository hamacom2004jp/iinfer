from iinfer.app import common
from pathlib import Path
from PIL import Image
from unittest.mock import patch
import json
import os
import numpy as np
import logging


def test_load_config():
    logger, _ = common.load_config("client", debug=True)
    assert logger.name == 'client'
    logger, _ = common.load_config("gui", debug=True)
    assert logger.name == 'gui'
    logger, _ = common.load_config("postprocess", debug=True)
    assert logger.name == 'postprocess'
    logger, _ = common.load_config("server", debug=True)
    assert logger.name == 'server'
    logger, _ = common.load_config("redis", debug=True)
    assert logger.name == 'redis'
    logger, _ = common.load_config("install", debug=True)
    assert logger.name == 'install'

def test_default_json_enc():
    # Test with Path object
    path = Path('test_path')
    assert common.default_json_enc(path) == 'test_path'

    # Test with numpy array
    np_array = np.array([1, 2, 3])
    assert common.default_json_enc(np_array) == [1, 2, 3]

    # Test with numpy float32
    #np_float32 = np.float32(1.23)
    #assert common.default_json_enc(np_float32) == 1.23

    # Test with numpy int64
    np_int64 = np.int64(123)
    assert common.default_json_enc(np_int64) == 123

    # Test with numpy int32
    np_int32 = np.int32(123)
    assert common.default_json_enc(np_int32) == 123

    # Test with numpy intc
    np_intc = np.intc(123)
    assert common.default_json_enc(np_intc) == 123

    # Test with unsupported type
    unsupported = set([1, 2, 3])
    try:
        common.default_json_enc(unsupported)
    except TypeError as e:
        assert str(e) == "Type <class 'set'> not serializable"

def test_saveopt():
    # Test with valid input
    opt = {'key': 'value'}
    opt_path = Path('test_saveopt.json')
    common.saveopt(opt, opt_path)

    # Check if the file was created
    assert opt_path.is_file()

    # Check if the content of the file is correct
    with open(opt_path, 'r') as f:
        saved_opt = json.load(f)
    assert saved_opt == opt

    # Clean up
    opt_path.unlink()

    # Test with None path
    common.saveopt(opt, None)

def test_loadopt():
    # Test with valid input
    opt = {'key': 'value'}
    opt_path = Path('test_loadopt.json')
    with open(opt_path, 'w') as f:
        json.dump(opt, f)

    loaded_opt = common.loadopt(str(opt_path))
    assert loaded_opt == opt

    # Clean up
    opt_path.unlink()

    # Test with None path
    assert common.loadopt(None) == {}

    # Test with non-existing path
    assert common.loadopt('non_existing_path.json') == {}

def test_getopt():
    # Test with valid input
    opt_base = dict(test1="base", test2="base2")
    opt_args = dict(test1="args")

    # Test with preval
    ret = common.getopt(opt_base, 'test1', preval=opt_args, defval="defval", withset=False)
    assert ret == "args"

    # Test with base value
    ret = common.getopt(opt_base, 'test2', preval=opt_args, defval="defval", withset=False)
    assert ret == "base2"

    # Test with default value
    ret = common.getopt(opt_base, 'test3', preval=opt_args, defval="defval", withset=False)
    assert ret == "defval"

    # Test with withset
    ret = common.getopt(opt_base, 'test3', preval=opt_args, defval="defval", withset=True)
    assert opt_base["test3"] == "defval"

def test_mkdirs():
    # Test with valid input
    dir_path = Path('test_dir')
    common.mkdirs(dir_path)

    # Check if the directory was created
    assert dir_path.is_dir()

    # Clean up
    dir_path.rmdir()

    # Test with existing directory
    dir_path.mkdir()
    try:
        common.mkdirs(dir_path)
    except BaseException as e:
        assert str(e) == f"Don't make diredtory.({str(dir_path)})"

    # Clean up
    dir_path.rmdir()

def test_print_format():
    # Test with format=True and list data
    data = {'success': [{'key1': 'value1', 'key2': 'value2'}]}
    txt = common.print_format(data, format=True, tm=0.0, stdout=False)
    assert '| key1   | key2   |\n|--------|--------|\n| value1 | value2 |' == txt

    # Test with format=True and dict data
    data = {'success': {'key1': 'value1', 'key2': 'value2'}}
    txt = common.print_format(data, format=True, tm=0.0, stdout=False)
    assert '| key1   | key2   |\n|--------|--------|\n| value1 | value2 |' == txt

    # Test with format=True and list data
    data = [{'key1': 'value1', 'key2': 'value2'}]
    txt = common.print_format(data, format=True, tm=0.0, stdout=False)
    assert '| key1   | key2   |\n|--------|--------|\n| value1 | value2 |' == txt

    # Test with format=True and dict data
    data = {'key1': 'value1', 'key2': 'value2'}
    txt = common.print_format(data, format=True, tm=0.0, stdout=False)
    assert '| key1   | key2   |\n|--------|--------|\n| value1 | value2 |' == txt

    # Test with format=False and dict data
    data = {'key1': 'value1', 'key2': 'value2'}
    txt = common.print_format(data, format=False, tm=0.0, stdout=False)
    assert json.loads(txt) == data

    # Test with output_json
    output_json = 'test_output.json'
    common.print_format(data, format=False, tm=0.0, output_json=output_json, stdout=False)
    with open(output_json, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == data

    # Clean up
    os.remove(output_json)

@patch('requests.get')
def test_download_file(mock_get):
    # Mock the response from requests.get
    mock_response = mock_get.return_value
    mock_response.content = b'Test content'

    # Test with valid input
    url = 'http://test.com/test.txt'
    save_path = Path('test.txt')
    result_path = common.download_file(url, save_path)

    # Check if the file was created
    assert result_path.is_file()

    # Check if the content of the file is correct
    with open(result_path, 'r') as f:
        content = f.read()
    assert content == 'Test content'

    # Clean up
    os.remove(result_path)

""" デバックだと成功するが、pytestだとエラーになる
@patch('subprocess.run')
def test_cmd(mock_run):
    # Mock the response from subprocess.run
    mock_response = mock_run.return_value
    mock_response.stdout = b'Test'
    mock_response.returncode = 0

    # Test with valid input
    command = ['echo', 'Test']
    returncode, output = common.cmd(command, logging.getLogger())

    # Check if the function returns the correct output
    assert output == 'Test'
    assert returncode == 0
"""

def test_draw_boxes():
    # Create a sample image
    image = Image.new('RGB', (100, 100), color = (73, 109, 137))

    # Define the bounding boxes, scores, and classes
    boxes = [[10, 10, 50, 50], [60, 60, 80, 80]]
    scores = [0.9, 0.75]
    classes = [0, 1]
    ids = ['id1', 'id2']
    labels = ['label1', 'label2']
    colors = [(255, 0, 0), (0, 255, 0)]

    # Call the function
    result_image, result_labels = common.draw_boxes(image, boxes, scores, classes, ids=ids, labels=labels, colors=colors)

    # Check the labels
    assert result_labels == labels

    # Check the image
    # Note: This is a simple check. In a real test, you might want to check the specific pixels.
    assert isinstance(result_image, Image.Image)
