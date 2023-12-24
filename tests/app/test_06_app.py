from iinfer.app import app
from pathlib import Path
from unittest.mock import patch
import json
import os
import pytest
import time
import threading

wsl_name = 'Ubuntu_docker-20.04'
wsl_user = 'ubuntu'
HOME_DIR = os.path.expanduser("~")
data = Path(HOME_DIR) / ".iinfer"
activate = [str(Path('.venv') / "Scripts" / "python.exe"), '-m', 'iinfer']

@pytest.mark.run(order=1)
def test_01_01_version(capfd):
    cmd = f"iinfer --version".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()

@pytest.mark.run(order=2)
def _test_02_01_redis_docker_run(capfd):
    cmd = f"iinfer -m redis -c docker_run --wsl_name {wsl_name} --wsl_user {wsl_user}".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()

@pytest.mark.run(order=3)
def _test_03_01_server_start(capfd):
    cmd = f"iinfer -m server -c start".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)

@pytest.mark.run(order=4)
def test_04_01_client_deploy(capfd):
    cmd = f"iinfer -m client -c deploy -n onnx_det_YoloX_Lite --model_img_width 416 --model_img_width 416 --overwrite " \
          f"--model_file models/yolox_nano.onnx " \
          f"--label_file iinfer/datasets/label_coco.txt " \
          f"--predict_type onnx_det_YoloX_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_02_client_deploy(capfd):
    cmd = f"iinfer -m client -c deploy -n mmdet_det_YoloX_Lite --model_img_width 416 --model_img_width 416 --overwrite " \
          f"--model_file models/yolox_tiny_8x8_300e_coco_20211124_171234-b4047906.pth " \
          f"--model_conf_file models/yolox_tiny_8xb8-300e_coco.py " \
          f"--model_conf_file models/yolox_s_8xb8-300e_coco.py " \
          f"--model_conf_file models/yolox_tta.py " \
          f"--label_file iinfer/datasets/label_coco.txt " \
          f"--predict_type mmdet_det_YoloX_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_03_client_deploy(capfd):
    cmd = f"iinfer -m client -c deploy -n onnx_cls_EfficientNet_Lite4 --model_img_width 224 --model_img_width 224 --overwrite " \
          f"--model_file models/efficientnet-lite4-11-qdq.onnx " \
          f"--predict_type onnx_cls_EfficientNet_Lite4".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_04_client_deploy(capfd):
    cmd = f"iinfer -m client -c deploy -n mmpretrain_cls_swin_Lite --model_img_width 224 --model_img_width 224 --overwrite " \
          f"--model_file models/swin_tiny_224_b16x64_300e_imagenet_20210616_090925-66df6be6.pth " \
          f"--model_conf_file models/swin-tiny_16xb64_in1k.py " \
          f"--predict_type mmpretrain_cls_swin_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=5)
def test_05_01_client_deploy_list(capfd):
    cmd = f"iinfer -m client -c deploy_list".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_01_client_start(capfd):
    cmd = f"iinfer -m client -c start -n onnx_det_YoloX_Lite --use_track".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_02_client_start(capfd):
    cmd = f"iinfer -m client -c start -n mmdet_det_YoloX_Lite --use_track".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_03_client_start(capfd):
    cmd = f"iinfer -m client -c start -n onnx_cls_EfficientNet_Lite4".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_04_client_start(capfd):
    cmd = f"iinfer -m client -c start -n mmpretrain_cls_swin_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=7)
def test_07_01_client_predict_type_list(capfd):
    cmd = f"iinfer -m client -c predict_type_list".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)

@pytest.mark.run(order=8)
def test_08_01_client_capture(capfd):
    cmd = f"iinfer -m client -c capture --capture_count 1 --output_preview".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            assert len(out) > 0
            assert len(out.split(',')) >= 4
            print(out.split(',')[1:])

@pytest.mark.run(order=9)
def test_09_01_client_predict(capfd):
    cmd = f"iinfer -m client -c predict -n onnx_det_YoloX_Lite --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            with open('onnx_det_YoloX_Lite.json', 'w', encoding='utf-8') as f:
                f.write(out)
            result = json.loads(out)
            assert 'success' in result.keys()
            del result["output_image"]
            print(result)

@pytest.mark.run(order=9)
def test_09_02_client_predict(capfd):
    cmd = f"iinfer -m client -c predict -n mmdet_det_YoloX_Lite --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            with open('mmdet_det_YoloX_Lite.json', 'w', encoding='utf-8') as f:
                f.write(out)
            result = json.loads(out)
            assert 'success' in result.keys()
            del result["output_image"]
            print(result)

@pytest.mark.run(order=9)
def test_09_03_client_predict(capfd):
    cmd = f"iinfer -m client -c predict -n onnx_cls_EfficientNet_Lite4 --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            with open('onnx_cls_EfficientNet_Lite4.json', 'w', encoding='utf-8') as f:
                f.write(out)
            result = json.loads(out)
            assert 'success' in result.keys()
            del result["output_image"]
            print(result)

@pytest.mark.run(order=9)
def test_09_04_client_predict(capfd):
    cmd = f"iinfer -m client -c predict -n mmpretrain_cls_swin_Lite --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            with open('mmpretrain_cls_swin_Lite.json', 'w', encoding='utf-8') as f:
                f.write(out)
            result = json.loads(out)
            assert 'success' in result.keys()
            del result["output_image"]
            print(result)

@pytest.mark.run(order=10)
def test_10_01_postprocess_det_filter(capfd):
    cmd = f"iinfer -m postprocess -c det_filter -i onnx_det_YoloX_Lite.json --output_preview " \
          f"--score_th 0.01 --width_th 1 --height_th 1".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=10)
def test_10_02_postprocess_det_filter(capfd):
    cmd = f"iinfer -m postprocess -c det_filter -i mmdet_det_YoloX_Lite.json --output_preview " \
          f"--score_th 0.01 --width_th 1 --height_th 1".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=10)
def _test_10_03_postprocess_det_filter(capfd):
    cmd = f"iinfer -m postprocess -c det_filter -i onnx_cls_EfficientNet_Lite4.json --output_preview " \
          f"--score_th 0.01".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=10)
def _test_10_04_postprocess_det_filter(capfd):
    cmd = f"iinfer -m postprocess -c det_filter -i mmpretrain_cls_swin_Lite.json --output_preview " \
          f"--score_th 0.01".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=11)
def test_11_01_postprocess_csv(capfd):
    cmd = f"iinfer -m postprocess -c csv -i onnx_det_YoloX_Lite.json".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            result = json.loads(out)
            assert 'success' in result.keys()
            print(result['success'])
            assert result['success'].startswith('output_boxes')

@pytest.mark.run(order=11)
def test_11_02_postprocess_csv(capfd):
    cmd = f"iinfer -m postprocess -c csv -i mmdet_det_YoloX_Lite.json".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            result = json.loads(out)
            assert 'success' in result.keys()
            print(result['success'])
            assert result['success'].startswith('output_boxes')

@pytest.mark.run(order=11)
def test_11_03_postprocess_csv(capfd):
    cmd = f"iinfer -m postprocess -c csv -i onnx_cls_EfficientNet_Lite4.json".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            result = json.loads(out)
            assert 'success' in result.keys()
            print(result['success'])
            assert result['success'].startswith('output_scores')

@pytest.mark.run(order=11)
def test_11_04_postprocess_csv(capfd):
    cmd = f"iinfer -m postprocess -c csv -i mmpretrain_cls_swin_Lite.json".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            result = json.loads(out)
            assert 'success' in result.keys()
            print(result['success'])
            assert result['success'].startswith('output_scores')

@pytest.mark.run(order=13)
def test_13_01_client_stop(capfd):
    cmd = f"iinfer -m client -c stop -n onnx_det_YoloX_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=13)
def test_13_02_client_stop(capfd):
    cmd = f"iinfer -m client -c stop -n mmdet_det_YoloX_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=13)
def test_13_03_client_stop(capfd):
    cmd = f"iinfer -m client -c stop -n onnx_cls_EfficientNet_Lite4".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

@pytest.mark.run(order=13)
def test_13_04_client_stop(capfd):
    cmd = f"iinfer -m client -c stop -n mmpretrain_cls_swin_Lite".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()
            out, err = capfd.readouterr()
            print(out)
            result = json.loads(out)
            assert 'success' in result.keys()

#@pytest.mark.run(order=90)
def _test_90_01_server_stop(capfd):
    cmd = f"iinfer -m server -c stop".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()

#@pytest.mark.run(order=91)
def _test_91_01_redis_docker_stop(capfd):
    cmd = f"iinfer -m redis -c docker_stop --wsl_name {wsl_name} --wsl_user {wsl_user}".split(' ')
    with patch('sys.argv', cmd):
        with patch('builtins.exit', return_value=[0]):
            app.main()

