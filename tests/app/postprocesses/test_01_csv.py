from iinfer.app.postprocesses.csv import Csv
from PIL import Image
import pytest
import logging

def test_post():
    """
    このテストケースは、post_json関数が期待通りに動作するかを確認します。
    それぞれのテストケースは、異なるタイプのoutputsを使用しています。
    また、出力ヘッダーが見つからない場合のエラーもテストしています。
    """

    # テストケース1: outputsが'success'キーを持つリストの場合
    csv = Csv(logging.getLogger())
    outputs = {'success': [{'key1': 'value1', 'key2': 'value2'}, {'key1': 'value3', 'key2': 'value4'}]}
    result, result_image = csv.post(outputs, Image.new('RGB', (60, 30)))
    result = result.replace('\r', '')  # Windowsで実行した場合は改行コードが\r\nになるため、\rを削除
    assert result == 'key1,key2\nvalue1,value2\nvalue3,value4'

    # テストケース2: outputsが'success'キーを持つ辞書の場合
    csv = Csv(logging.getLogger())
    outputs = {'success': {'key1': 'value1', 'key2': 'value2'}}
    result, result_image = csv.post(outputs, Image.new('RGB', (60, 30)))
    result = result.replace('\r', '')  # Windowsで実行した場合は改行コードが\r\nになるため、\rを削除
    assert result == 'key1,key2\nvalue1,value2'

    # テストケース3: outputsがリストの場合
    csv = Csv(logging.getLogger())
    outputs = [{'key1': 'value1', 'key2': 'value2'}, {'key1': 'value3', 'key2': 'value4'}]
    result, result_image = csv.post(outputs, Image.new('RGB', (60, 30)))
    result = result.replace('\r', '')  # Windowsで実行した場合は改行コードが\r\nになるため、\rを削除
    assert result == 'key1,key2\nvalue1,value2\nvalue3,value4'

    # テストケース4: outputsが辞書の場合
    csv = Csv(logging.getLogger())
    outputs = {'key1': 'value1', 'key2': 'value2'}
    result, result_image = csv.post(outputs, Image.new('RGB', (60, 30)))
    result = result.replace('\r', '')  # Windowsで実行した場合は改行コードが\r\nになるため、\rを削除
    assert result == 'key1,key2\nvalue1,value2'

    # テストケース5: outputsが'success'キーを持つ辞書で、out_headersが設定されている場合
    csv = Csv(logging.getLogger(), out_headers=['key1'])
    outputs = {'success': {'key1': 'value1', 'key2': 'value2'}}
    result, result_image = csv.post(outputs, Image.new('RGB', (60, 30)))
    result = result.replace('\r', '')  # Windowsで実行した場合は改行コードが\r\nになるため、\rを削除
    assert result == 'key1\nvalue1'

    # テストケース6: outputsが'success'キーを持つ辞書で、out_headersが設定されていて、一部のヘッダーが見つからない場合
    csv = Csv(logging.getLogger(), out_headers=['key1', 'key3'])
    outputs = {'success': {'key1': 'value1', 'key2': 'value2'}}
    with pytest.raises(Exception) as e:
        csv.post(outputs, Image.new('RGB', (60, 30)))
    assert str(e.value) == "notfound headers: ['key3']"
