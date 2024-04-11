from iinfer.app.injections.after_csv_injection import AfterCSVInjection
from PIL import Image
from unittest.mock import Mock, patch
import numpy as np

def test_action():
    """
    このテストは、まずテスト用のAfterCSVInjectionインスタンスと引数を作成します。
    次に、csv.post_jsonメソッドをモック化します。
    最後に、actionメソッドを呼び出し、返された結果が正しいことを確認します。
    """
    # テスト用のAfterCSVInjectionインスタンスを作成します
    after_csv_injection = AfterCSVInjection({}, Mock())

    # テスト用の引数を作成します
    reskey = 'test_reskey'
    name = 'test_name'
    outputs = {'success': 'test_success'}
    output_image = Image.fromarray(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))
    session = {'session': 'test_session'}

    # actionメソッドを呼び出します
    result_outputs, result_image = after_csv_injection.action(reskey, name, outputs, output_image, session)

    # 返された結果が正しいことを確認します
    assert result_outputs == {'success': 'test_success', 'injection_success': ['test_success']}
    assert result_image == output_image
