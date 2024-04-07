from iinfer.app.commons import convert
from iinfer.app.injections.after_seg_filter_injection import AfterSegFilterInjection
from typing import Dict, Any
from PIL import Image
from unittest.mock import Mock
import numpy as np


def test_action():
    # AfterSegFilterInjection クラスのインスタンスを作成します。
    # コンストラクタの config パラメータには、post_json メソッドのコメントを参照して必要なパラメータを指定します。
    injection = AfterSegFilterInjection(config=dict(classes=[1], logits_th=[0.5]), logger=Mock())

    # テスト用の入力データを定義します
    reskey = "test_reskey"
    name = "test_name"
    outputs: Dict[str, Any] = {
        'success': {
            'output_sem_seg': convert.npy2b64str(np.ones((1, 100, 100), dtype=np.int8)),
            'output_sem_seg_shape': [1, 100, 100],
            'output_sem_seg_dtype': 'int8',
            'output_seg_logits': convert.npy2b64str(np.ones((3, 100, 100), dtype=np.float16)),
            'output_seg_logits_shape': [3, 100, 100],
            'output_seg_logits_dtype': 'float16',
            'output_catalog': ['label1', 'label2', 'label3'],
            'output_classes': [1],
            'output_labels': ['label1'],
            'output_palette': [[255,1,1], [2,255,2], [3,3,255]]
        }
    }
    output_image = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
    session = {}

    # action メソッドをテストします。
    result = injection.action(reskey, name, outputs, output_image, session)

    # 得られた結果が期待通りであることを確認します。
    assert 'success' in result
    assert 'output_boxes' in result['success']
    assert 'output_boxes_classes' in result['success']
    assert 'output_rounds' in result['success']
    assert 'output_rbboxes' in result['success']
    assert 'output_sem_seg' not in result['success']
    assert 'output_sem_seg_shape' not in result['success']
    assert 'output_sem_seg_dtype' not in result['success']