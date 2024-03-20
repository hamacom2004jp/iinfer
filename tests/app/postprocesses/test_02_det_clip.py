import pytest
from PIL import Image
import numpy as np
from iinfer.app.postprocesses.det_clip import DetClip
from pathlib import Path
import logging

def test_post_json():
    # DetClip インスタンスを作成
    det_clip = DetClip(logging.getLogger())

    # テスト用のデータを作成
    json_session = None
    outputs = {
        'success': {
            'output_boxes': [[10, 10, 20, 20]]
        },
        'output_image_name': 'test_image.jpg'
    }
    output_image = Image.new('RGB', (100, 100))

    # post_json メソッドをテスト
    result = det_clip.post_json(json_session, outputs, output_image)

    # 結果を検証
    assert isinstance(result, str)
    assert len(result.split('\n')) == 2  # 1つのボックスと終端の空行

def test_post_json_no_success():
    # DetClip インスタンスを作成
    det_clip = DetClip(logging.getLogger())

    # 'success' キーがない場合のエラーをテスト
    with pytest.raises(Exception, match='Invalid outputs. outputs\[\'success\'\] must be dict.'):
        det_clip.post_json(None, {}, None)

def test_post_json_no_output_boxes():
    # DetClip インスタンスを作成
    det_clip = DetClip(logging.getLogger())

    # 'output_boxes' キーがない場合のエラーをテスト
    with pytest.raises(Exception, match='Invalid outputs. outputs\[\'success\'\]\[\'output_boxes\'\] must be set.'):
        det_clip.post_json(None, {'success': {}}, None)

def test_post_json_no_output_image():
    # DetClip インスタンスを作成
    det_clip = DetClip(logging.getLogger())

    # 'output_image' キーがない場合のエラーをテスト
    with pytest.raises(Exception, match='Invalid outputs. outputs\[\'success\'\]\[\'output_image\'\] and outputs\[\'success\'\]\[\'output_image_shape\'\] and outputs\[\'success\'\]\[\'output_image_name\'\] must be set.'):
        det_clip.post_json(None, {'success': {'output_boxes': [[10, 10, 20, 20]]}}, None)
