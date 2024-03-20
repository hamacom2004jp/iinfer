import pytest
from unittest.mock import Mock, patch
from PIL import Image
from iinfer.app.postprocesses.httpreq import Httpreq
from iinfer.app.postprocesses import convert

def test_post_img():
    """
    このテストコードは、Httpreqクラスのpost_imgメソッドが期待通りに動作することを確認します。
    """
    # Httpreq インスタンスを作成
    httpreq = Httpreq()

    # テスト用の画像を作成
    output_image = Image.new('RGB', (60, 30), color = 'red')

    # テスト用の result を作成
    result = {"key": "value"}

    # テスト用の img_session を作成
    mock_session = Mock()
    img_session = (mock_session, "http://testsite.com")

    # fileup_name を設定
    httpreq.fileup_name = "test_file"

    # post メソッドが 200 を返すように設定
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = convert.img2byte(output_image, "JPEG")
    mock_session.post.return_value = mock_response

    # post_img メソッドを実行
    returned_image = httpreq.post_img(img_session, result, output_image)

    # post メソッドが期待通りに呼び出されたことを確認
    mock_session.post.assert_called_once_with(img_session[1], files={"test_file": convert.img2byte(output_image, "JPEG")}, verify=False)

    # 期待する画像が返されたことを確認
    assert returned_image == output_image

    # fileup_name が None の場合に Exception がスローされることを確認
    httpreq.fileup_name = None
    with pytest.raises(Exception, match="fileup_name is empty."):
        httpreq.post_img(img_session, result, output_image)

    # post メソッドが 200 以外を返す場合に Exception がスローされることを確認
    httpreq.fileup_name = "test_file"
    mock_response.status_code = 404
    with pytest.raises(Exception, match="Failed to postprocess. status_code=404."):
        httpreq.post_img(img_session, result, output_image)
