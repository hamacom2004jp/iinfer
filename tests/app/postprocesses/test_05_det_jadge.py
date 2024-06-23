import pytest
from PIL import Image
from iinfer.app.postprocesses.det_jadge import DetJadge
import logging


def test_post():
    # DetJadgeクラスのコンストラクタに渡すパラメータ
    ok_score_th = 0.5
    ok_classes = [1, 2]
    ok_labels = ['label1', 'label2']
    ng_score_th = 0.4
    ng_classes = [3, 4]
    ng_labels = ['label3', 'label4']
    ext_score_th = 0.6
    ext_classes = [5, 6]
    ext_labels = ['label5', 'label6']

    json_session = None
    # post_jsonメソッドに渡すパラメータ
    json_data = {
        'success': {
            'output_boxes': [[0, 0, 20, 20], [30, 30, 40, 40], [50, 50, 55, 55]],
            'output_scores': [0.6, 0.7, 0.4],
            'output_classes': [0, 1, 2],
            'output_labels': ['label1', 'label2', 'label3'],
            'output_tracks': [1, 2, 3]
        }
    }
    output_image = Image.new('RGB', (100, 100))

    # DetJadgeクラスのインスタンスを作成
    det_jadge = DetJadge(
        logging.getLogger(),
        ok_score_th=ok_score_th,
        ok_classes=ok_classes,
        ok_labels=ok_labels,
        ng_score_th=ng_score_th,
        ng_classes=ng_classes,
        ng_labels=ng_labels,
        ext_score_th=ext_score_th,
        ext_classes=ext_classes,
        ext_labels=ext_labels
    )

    # post_jsonメソッドを呼び出し、結果を取得
    result, result_image = det_jadge.post(json_data, output_image)

    # 結果を検証
    assert result['success']['output_jadge_score'] == [0.7, 0.4, 0.0]
    assert result['success']['output_jadge_label'] == ['ok', 'ng', 'gray']
    assert result['success']['output_jadge'] == 'ng'
