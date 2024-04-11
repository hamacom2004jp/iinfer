from iinfer.app.commons import convert
from iinfer.app.injections.after_seg_bbox_injection import AfterSegBBoxInjection
from typing import Dict, Any
from PIL import Image
from unittest.mock import Mock
import numpy as np


def test_action():
    # AfterSegBBoxInjection クラスのインスタンスを作成します。
    # コンストラクタの config パラメータには、post_json メソッドのコメントを参照して必要なパラメータを指定します。
    injection = AfterSegBBoxInjection(config=dict(), logger=Mock())

    # テスト用の入力データを定義します
    reskey = "test_reskey"
    name = "test_name"
    outputs: Dict[str, Any] = {
        'success': {
            'output_sem_seg': convert.npy2b64str(np.ones((1, 100, 100), dtype=np.int8)),
            'output_sem_seg_shape': [1, 100, 100],
            'output_sem_seg_dtype': 'int8',
            'output_classes': [1],
            'output_labels': ['label1'],
            'output_palette': [[255,1,1], [2,255,2], [3,3,255]]
        }
    }
    output_image = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    session = {}

    # action メソッドをテストします。
    result_outputs, result_image = injection.action(reskey, name, outputs, output_image, session)

    # 得られた結果が期待通りであることを確認します。
    assert 'success' in result_outputs
    assert 'output_boxes' in result_outputs['success']
    assert 'output_boxes_classes' in result_outputs['success']
    assert 'output_boxes_labels' in result_outputs['success']
    assert 'output_rbboxes' in result_outputs['success']
    assert 'output_rbboxes_rounds' in result_outputs['success']
