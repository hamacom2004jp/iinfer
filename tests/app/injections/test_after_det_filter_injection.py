from iinfer.app.injections.after_det_filter_injection import AfterDetFilterInjection
from PIL import Image
from unittest.mock import Mock
import numpy as np

def test_after_det_filter_injection_action():
    """
    このテストは、まずAfterDetFilterInjectionのインスタンスを作成します。
    次に、テスト用の入力データを定義します。
    その後、actionメソッドを実行し、結果を確認します。最後に、スコアが0.8以上の結果のみが残ることを確認します。
    """
    # AfterDetFilterInjection インスタンスを作成します
    injection = AfterDetFilterInjection(dict(score_th=0.8), Mock())

    # テスト用の入力データを定義します
    reskey = "test_reskey"
    name = "test_name"
    outputs = {
        "success": {
            "output_scores": [0.9, 0.1, 0.8],
            "output_classes": [1, 2, 3],
            "output_boxes": [[0, 0, 50, 50], [0, 0, 10, 10], [0, 0, 40, 40]],
            "output_labels": ["label1", "label2", "label3"],
            "output_tracks": [1, 2, 3]
        }
    }
    output_image = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    session = {}

    # action メソッドを実行します
    result_outputs, result_image = injection.action(reskey, name, outputs, output_image, session)

    # 結果を確認します
    assert "success" in result_outputs
    assert "output_scores" in result_outputs["success"]
    assert "output_classes" in result_outputs["success"]
    assert "output_boxes" in result_outputs["success"]
    assert "output_labels" in result_outputs["success"]
    assert "output_tracks" in result_outputs["success"]

    # スコアが 0.8 以上の結果のみが残ることを確認します
    assert result_outputs["success"]["output_scores"] == [0.9, 0.8]
    assert result_outputs["success"]["output_classes"] == [1, 3]
    assert result_outputs["success"]["output_boxes"] == [[0, 0, 50, 50], [0, 0, 40, 40]]
    assert result_outputs["success"]["output_labels"] == ["label1", "label3"]
    assert result_outputs["success"]["output_tracks"] == [1, 3]
    assert result_outputs["injection_success"] == ["filterd"]

