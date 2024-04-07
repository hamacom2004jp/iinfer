# FILEPATH: /c:/Users/hama/OneDrive/デスクトップ/devenv/iinfer/tests/app/postprocesses/test_httpreq.py

from iinfer.app.postprocesses.httpreq import Httpreq
from PIL import Image
from unittest.mock import Mock
import pytest
import logging
import numpy as np
import requests_mock

def test_post_text():
    """
    このテストコードは、HttpReqクラスのpost_textメソッドが期待通りに動作することを確認します。
    """
    # テスト用の res_str を作成
    res_str = "テストテキスト"

    # HttpReq インスタンスを作成
    http = Httpreq(logging.getLogger(), "test_file.jpg")
    http.create_session("http://outputs_url", "http://output_image_url", "http://outputs_text_url")
    with requests_mock.Mocker() as m:
        m.post('http://outputs_url', text='期待する結果')
        m.post('http://output_image_url', text='期待する結果')
        m.post('http://outputs_text_url', text='期待する結果')

        # post_text メソッドを呼び出す
        result = http.post_text("http://outputs_text_url", res_str)

        # 結果を検証する
        assert result == {'success': '期待する結果'}

def test_post_json():
    """
    このテストコードは、HttpReqクラスのpost_jsonメソッドが期待通りに動作することを確認します。
    """
    # HttpReq インスタンスを作成
    http = Httpreq(logging.getLogger(), "test_file.jpg")
    http.create_session("http://outputs_url", "http://output_image_url", "http://outputs_text_url")
    with requests_mock.Mocker() as m:
        m.post('http://outputs_url', text='期待する結果')
        m.post('http://output_image_url', text='期待する結果')
        m.post('http://outputs_text_url', text='期待する結果')

        # テスト用の res_json を作成
        res_json = {"res_key": "res_value"}
        # テスト用の res_img を作成
        res_img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))

        # post_json メソッドを呼び出す
        result = http.post_json("http://outputs_text_url", res_json, res_img)

        # 結果を検証する
        assert result == {'success': '期待する結果'}

def test_post_img():
    """
    このテストコードは、HttpReqクラスのpost_imgメソッドが期待通りに動作することを確認します。
    """
    # HttpReq インスタンスを作成
    http = Httpreq(logging.getLogger(), "test_file.jpg")
    http.create_session("http://outputs_url", "http://output_image_url", "http://outputs_text_url")
    with requests_mock.Mocker() as m:
        m.post('http://outputs_url', text='期待する結果')
        m.post('http://output_image_url', text='期待する結果')
        m.post('http://outputs_text_url', text='期待する結果')

        # テスト用の res_json を作成
        res_json = {"res_key": "res_value"}
        # テスト用の res_img を作成
        res_img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))

        # post_img メソッドを呼び出す
        result = http.post_img("http://outputs_text_url", res_json, res_img)

        # 結果を検証する
        assert result == {'success': '期待する結果'}
