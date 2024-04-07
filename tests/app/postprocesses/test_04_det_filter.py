from PIL import Image
from iinfer.app.postprocesses.det_filter import DetFilter
import pytest
import logging

def test_post_json():
    """
    このテストでは、DetFilterクラスのpost_jsonメソッドが正しく動作するかを検証します。
    具体的には、
    output_scoresがscore_th以上、
    output_boxesで表される領域の幅と高さがそれぞれwidth_thとheight_th以上、
    output_classesとoutput_labelsが指定したクラスとラベルに含まれているかを確認します。
    """
    # テスト用のデータを作成
    json_session = None
    outputs = {
        'success': {
            'output_boxes': [[0, 0, 20, 20], [30, 30, 40, 40], [50, 50, 55, 55]],
            'output_scores': [0.6, 0.7, 0.4],
            'output_classes': [0, 1, 2],
            'output_labels': ['label1', 'label2', 'label3'],
            'output_tracks': [1, 2, 3]
        }
    }
    output_image = Image.new('RGB', (100, 100))

    # DetFilterクラスのインスタンスを作成
    det_filter = DetFilter(logging.getLogger(), score_th=0.5, width_th=10, height_th=10, classes=[0, 1, 2], labels=['label1', 'label2', 'label3'])

    # post_jsonメソッドをテスト
    result = det_filter.post_json(json_session, outputs, output_image)

    # 結果を検証
    assert result['output_boxes'] == [[0, 0, 20, 20], [30, 30, 40, 40]]
    assert result['output_scores'] == [0.6, 0.7]
    assert result['output_classes'] == [0, 1]
    assert result['output_labels'] == ['label1', 'label2']
    assert result['output_tracks'] == [1, 2]
