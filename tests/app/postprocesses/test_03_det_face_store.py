import pytest
from PIL import Image
import numpy as np
from iinfer.app.postprocesses.det_face_store import DetFaceStore
import logging

# DetFaceStoreクラスのpost_jsonメソッドのテスト
def test_post_json():
    # テスト用のデータを作成
    json_session = None
    outputs = {
        'success': {
            'output_boxes': [[0, 0, 10, 10]],
            'output_embeddings': [np.array([1, 2, 3])],
            'output_embedding_dtypes': ['float32'],
            'output_embedding_shapes': [(3,)],
            'output_scores': [0.7],
        }
    }
    output_image = Image.new('RGB', (20, 20))

    # face_thresholdパラメータを0.6に設定してDetFaceStoreクラスのインスタンスを作成
    det_face_store = DetFaceStore(logging.getLogger(), face_threshold=0.6)

    # post_jsonメソッドを呼び出し、結果を検証
    result = det_face_store.post_json(json_session, outputs, output_image)
    assert len(result) == 1
    assert result[0]['face_embedding'].tolist() == [1, 2, 3]
    assert result[0]['face_embedding_dtype'] == 'float32'
    assert result[0]['face_embedding_shape'] == (3,)
    assert result[0]['face_image_type'] == det_face_store.image_type
    assert result[0]['face_image_shape'] == (10, 10, 3)
    assert result[0]['face_score'] == 0.7
    assert result[0]['face_box'] == [0, 0, 10, 10]

# DetFaceStoreクラスのpost_jsonメソッドのテスト（'success'キーがない場合のエラーをテスト）
def test_post_json_no_success():
    # 'success' キーがない場合のエラーをテスト
    det_face_store = DetFaceStore(logging.getLogger())
    with pytest.raises(Exception, match='Invalid outputs. outputs\[\'success\'\] must be dict.'):
        det_face_store.post_json(None, {}, None)
