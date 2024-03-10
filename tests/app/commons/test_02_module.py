from iinfer.app.commons import module
from iinfer.app.injection import BeforeInjection, AfterInjection
from iinfer.app.predict import Predict
import logging
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

def test_load_custom_predict():
    """
    このテストは、まずテスト用のロガーとカスタム予測クラスを作成します。
    次に、importlib.util.spec_from_file_location、importlib.util.module_from_spec、importlib.util.module_from_spec.loader.exec_module、inspect.getmembersの各関数をモック化します。
    最後に、load_custom_predict関数を呼び出し、返されたオブジェクトがカスタム予測クラスのインスタンスであることを確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用のカスタム予測クラスを作成します
    class CustomPredict(Predict):
        def __init__(self, logger):
            super().__init__(logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.CustomPredict = CustomPredict

    # importlib.util.spec_from_file_locationとimportlib.util.module_from_specのモックを作成します
    with patch('importlib.util.spec_from_file_location', return_value=Mock()), \
         patch('importlib.util.module_from_spec', return_value=mock_module), \
         patch('importlib.util.module_from_spec.loader.exec_module'), \
         patch('inspect.getmembers', return_value=[('CustomPredict', CustomPredict)]):
        
        # load_custom_predict関数を呼び出します
        result = module.load_custom_predict(Path('custom_predict.py'), logger)

        # 返されたオブジェクトがCustomPredictクラスのインスタンスであることを確認します
        assert isinstance(result, CustomPredict)

def test_load_predict():
    """
    このテストは、まずテスト用のロガーと予測クラスを作成します。
    次に、importlib.import_moduleとinspect.getmembersの各関数をモック化します。
    最後に、load_predict関数を呼び出し、返されたオブジェクトが予測クラスのインスタンスであることを確認します。
    また、予測クラスが見つからない場合に例外が発生することも確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用の予測クラスを作成します
    class TestPredict(Predict):
        def __init__(self, logger):
            super().__init__(logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.TestPredict = TestPredict

    # importlib.import_moduleとinspect.getmembersのモックを作成します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[('TestPredict', TestPredict)]):
        
        # load_predict関数を呼び出します
        result = module.load_predict('test', logger)

        # 返されたオブジェクトがTestPredictクラスのインスタンスであることを確認します
        assert isinstance(result, TestPredict)

    mock_module = Mock()
    # 予測クラスが見つからない場合に例外が発生することを確認します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[]):
        with pytest.raises(BaseException) as e:
            module.load_predict('test', logger)
        assert str(e.value) == "Predict class not found.(test)"

def test_load_before_injection_type():
    """
    このテストは、まずテスト用のロガーと前処理クラスを作成します。
    次に、importlib.import_moduleとinspect.getmembersの各関数をモック化します。
    最後に、load_before_injection_type関数を呼び出し、返されたオブジェクトが前処理クラスのインスタンスであることを確認します。
    また、前処理クラスが見つからない場合に例外が発生することも確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用の前処理クラスを作成します
    class TestBeforeInjection(BeforeInjection):
        def __init__(self, config, logger):
            super().__init__(config, logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.TestBeforeInjection = TestBeforeInjection

    # importlib.import_moduleとinspect.getmembersのモックを作成します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[('TestBeforeInjection', TestBeforeInjection)]):
        
        # load_before_injection_type関数を呼び出します
        result = module.load_before_injection_type(['test'], {}, logger)

        # 返されたオブジェクトがTestBeforeInjectionクラスのインスタンスであることを確認します
        assert isinstance(result[0], TestBeforeInjection)

    mock_module = Mock()
    # 前処理クラスが見つからない場合に例外が発生することを確認します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[]):
        with pytest.raises(BaseException) as e:
            module.load_before_injection_type(['test'], {}, logger)
        assert str(e.value) == "BeforeInjection class not found.(['test'])"

def test_load_after_injection_type():
    """
    このテストは、まずテスト用のロガーと後処理クラスを作成します。
    次に、importlib.import_moduleとinspect.getmembersの各関数をモック化します。
    最後に、load_after_injection_type関数を呼び出し、返されたオブジェクトが後処理クラスのインスタンスであることを確認します。
    また、後処理クラスが見つからない場合に例外が発生することも確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用の後処理クラスを作成します
    class TestAfterInjection(AfterInjection):
        def __init__(self, config, logger):
            super().__init__(config, logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.TestAfterInjection = TestAfterInjection

    # importlib.import_moduleとinspect.getmembersのモックを作成します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[('TestAfterInjection', TestAfterInjection)]):
        
        # load_after_injection_type関数を呼び出します
        result = module.load_after_injection_type(['test'], {}, logger)

        # 返されたオブジェクトがTestAfterInjectionクラスのインスタンスであることを確認します
        assert isinstance(result[0], TestAfterInjection)

    mock_module = Mock()
    # 後処理クラスが見つからない場合に例外が発生することを確認します
    with patch('importlib.import_module', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[]):
        with pytest.raises(BaseException) as e:
            module.load_after_injection_type(['test'], {}, logger)
        assert str(e.value) == "AfterInjection class not found.(['test'])"

def test_load_before_injections():
    """
    このテストは、まずテスト用のロガーと前処理クラスを作成します。
    次に、importlib.util.spec_from_file_location、importlib.util.module_from_spec、inspect.getmembersの各関数をモック化します。
    最後に、load_before_injections関数を呼び出し、返されたオブジェクトが前処理クラスのインスタンスであることを確認します。
    また、前処理クラスが見つからない場合も確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用の前処理クラスを作成します
    class TestBeforeInjection(BeforeInjection):
        def __init__(self, config, logger):
            super().__init__(config, logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.TestBeforeInjection = TestBeforeInjection

    # importlib.util.spec_from_file_locationとimportlib.util.module_from_specとinspect.getmembersのモックを作成します
    with patch('importlib.util.spec_from_file_location', return_value=Mock()), \
         patch('importlib.util.module_from_spec', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[('TestBeforeInjection', TestBeforeInjection)]):
        
        # load_before_injections関数を呼び出します
        result = module.load_before_injections([Path('test.py')], {}, logger)

        # 返されたオブジェクトがTestBeforeInjectionクラスのインスタンスであることを確認します
        assert isinstance(result[0], TestBeforeInjection)

    mock_module = Mock()
    # 前処理クラスが見つからない場合を確認します
    with patch('importlib.util.spec_from_file_location', return_value=Mock()), \
         patch('importlib.util.module_from_spec', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[]):
        # load_before_injections関数を呼び出します
        result = module.load_before_injections([Path('test.py')], {}, logger)
        # 返されたオブジェクトが空であることを確認します
        assert result == []

def test_load_after_injections():
    """
    このテストは、まずテスト用のロガーと後処理クラスを作成します。
    次に、importlib.util.spec_from_file_location、importlib.util.module_from_spec、inspect.getmembersの各関数をモック化します。
    最後に、load_after_injections関数を呼び出し、返されたオブジェクトが後処理クラスのインスタンスであることを確認します。
    また、後処理クラスが見つからない場合に例外が発生することも確認します。
    """
    # テスト用のロガーを作成します
    logger = logging.getLogger('test')

    # テスト用の後処理クラスを作成します
    class TestAfterInjection(AfterInjection):
        def __init__(self, config, logger):
            super().__init__(config, logger)

    # モックオブジェクトを作成します
    mock_module = Mock()
    mock_module.TestAfterInjection = TestAfterInjection

    # importlib.util.spec_from_file_locationとimportlib.util.module_from_specとinspect.getmembersのモックを作成します
    with patch('importlib.util.spec_from_file_location', return_value=Mock()), \
         patch('importlib.util.module_from_spec', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[('TestAfterInjection', TestAfterInjection)]):
        
        # load_after_injections関数を呼び出します
        result = module.load_after_injections([Path('test.py')], {}, logger)

        # 返されたオブジェクトがTestAfterInjectionクラスのインスタンスであることを確認します
        assert isinstance(result[0], TestAfterInjection)

    mock_module = Mock()
    # 後処理クラスが見つからない場合に例外が発生することを確認します
    with patch('importlib.util.spec_from_file_location', return_value=Mock()), \
         patch('importlib.util.module_from_spec', return_value=mock_module), \
         patch('inspect.getmembers', return_value=[]):
        # load_after_injections関数を呼び出します
        result = module.load_after_injections([Path('test.py')], {}, logger)
        # 返されたオブジェクトが空であることを確認します
        assert result == []



