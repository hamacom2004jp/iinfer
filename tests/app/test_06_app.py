from iinfer.app import app
from pathlib import Path
from unittest.mock import patch
import iinfer
import json
import os
import pytest
import time
import threading
import subprocess

wsl_name = 'Ubuntu_docker-20.04'
wsl_user = 'ubuntu'
HOME_DIR = os.path.expanduser("~")
data = Path(HOME_DIR) / ".iinfer"
activate = [str(Path('.venv') / "Scripts" / "python.exe"), '-m', 'iinfer']

@pytest.fixture(scope='module', autouse=True)
def fixture_server():
    python = Path(iinfer.__file__).parent.parent / '.venv' / 'Scripts' / 'python.exe'
    #cmd = f"-m redis -c docker_run --wsl_name {wsl_name} --wsl_user {wsl_user}".split(' ')
    #threading.Thread(target=app.main, args=(cmd,)).start()
    #time.sleep(15)
    cmd = f"{python} -m iinfer -m server -c start --svname server1".split(' ')
    proc1 = subprocess.Popen(cmd)
    #threading.Thread(target=app.main, args=(cmd,)).start()
    cmd = f"{python} -m iinfer -m server -c start --svname server2".split(' ')
    proc2 = subprocess.Popen(cmd)
    #threading.Thread(target=app.main, args=(cmd,)).start()
    cmd = f"{python} -m iinfer -m server -c start --svname server3".split(' ')
    proc3 = subprocess.Popen(cmd)
    #threading.Thread(target=app.main, args=(cmd,)).start()
    time.sleep(15)
    yield
    cmd = f"{python} -m iinfer -m server -c stop --svname server3 --timeout 15".split(' ')
    subprocess.run(cmd)
    #app.main(args_list=cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server2 --timeout 15".split(' ')
    subprocess.run(cmd)
    #app.main(args_list=cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server1 --timeout 15".split(' ')
    subprocess.run(cmd)
    #app.main(args_list=cmd)
    #cmd = f"-m redis -c docker_stop --wsl_name {wsl_name} --wsl_user {wsl_user}".split(' ')
    #app.main(args_list=cmd)

@pytest.mark.run(order=1)
def test_01_01_version(capfd):
    cmd = f"--version".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()

@pytest.mark.run(order=4)
def test_04_01_client_deploy(capfd):
    cmd = f"-m client -c deploy --svname server1 -n onnx_det_YoloX_Lite --model_img_width 416 --model_img_width 416 --overwrite " \
          f"--model_file models/yolox_nano.onnx " \
          f"--label_file iinfer/datasets/label_coco.txt " \
          f"--predict_type onnx_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_02_client_deploy(capfd):
    cmd = f"-m client -c deploy --svname server2 -n mmdet_det_YoloX_Lite --model_img_width 416 --model_img_width 416 --overwrite " \
          f"--model_file models/yolox_tiny_8x8_300e_coco_20211124_171234-b4047906.pth " \
          f"--model_conf_file models/yolox_tiny_8xb8-300e_coco.py " \
          f"--model_conf_file models/yolox_s_8xb8-300e_coco.py " \
          f"--model_conf_file models/yolox_tta.py " \
          f"--label_file iinfer/datasets/label_coco.txt " \
          f"--predict_type mmdet_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_03_client_deploy(capfd):
    cmd = f"-m client -c deploy --svname server1 -n onnx_cls_EfficientNet_Lite4 --model_img_width 224 --model_img_width 224 --overwrite " \
          f"--model_file models/efficientnet-lite4-11-qdq.onnx " \
          f"--predict_type onnx_cls_EfficientNet_Lite4".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=4)
def test_04_04_client_deploy(capfd):
    cmd = f"-m client -c deploy --svname server3 -n mmpretrain_cls_swin_Lite --model_img_width 224 --model_img_width 224 --overwrite " \
          f"--model_file models/swin_tiny_224_b16x64_300e_imagenet_20210616_090925-66df6be6.pth " \
          f"--model_conf_file models/swin-tiny_16xb64_in1k.py " \
          f"--predict_type mmpretrain_cls_swin_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=5)
def test_05_01_client_deploy_list(capfd):
    cmd = f"-m client -c deploy_list --svname server1".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_01_client_start(capfd):
    cmd = f"-m client -c start --svname server1 -n onnx_det_YoloX_Lite --use_track".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_02_client_start(capfd):
    cmd = f"-m client -c start --svname server2 -n mmdet_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_03_client_start(capfd):
    cmd = f"-m client -c start --svname server1 -n onnx_cls_EfficientNet_Lite4".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=6)
def test_06_04_client_start(capfd):
    cmd = f"-m client -c start --svname server3 -n mmpretrain_cls_swin_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=7)
def test_07_01_client_predict_type_list(capfd):
    cmd = f"-m client -c predict_type_list".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert len(result) > 0

@pytest.mark.run(order=8)
def test_08_01_client_capture(capfd):
    cmd = f"-m client -c capture --capture_count 4 --capture_fps 2 --output_preview".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert len(result.split(',')) >= 5
    print(out)
    with open('cap.csv', 'w', encoding='utf-8') as f:
        f.write(out)

@pytest.mark.run(order=9)
def test_09_01_client_predict(capfd):
    cmd = f"-m client -c predict --svname server1 -n onnx_det_YoloX_Lite --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    with open('onnx_det_YoloX_Lite.json', 'w', encoding='utf-8') as f:
        f.write(out)
    assert 'success' in result.keys()
    del result["output_image"]
    print(result)

@pytest.mark.run(order=9)
def test_09_02_client_predict(capfd):
    cmd = f"-m client -c predict --svname server2 -n mmdet_det_YoloX_Lite --output_preview " \
          f"-i cap.csv --image_type capture".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    with open('mmdet_det_YoloX_Lite.json', 'w', encoding='utf-8') as f:
        f.write(out)
    assert 'success' in result[0].keys()
    del result["output_image"]
    print(result)

@pytest.mark.run(order=9)
def test_09_03_client_predict(capfd):
    cmd = f"-m client -c predict --svname server1 -n onnx_cls_EfficientNet_Lite4 --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    with open('onnx_cls_EfficientNet_Lite4.json', 'w', encoding='utf-8') as f:
        f.write(out)
    assert 'success' in result.keys()
    del result["output_image"]
    print(result)

@pytest.mark.run(order=9)
def test_09_04_client_predict(capfd):
    cmd = f"-m client -c predict --svname server3 -n mmpretrain_cls_swin_Lite --output_preview " \
          f"-i tests/dog.jpg --image_type jpeg".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    with open('mmpretrain_cls_swin_Lite.json', 'w', encoding='utf-8') as f:
        f.write(out)
    assert 'success' in result.keys()
    del result["output_image"]
    print(result)

@pytest.mark.run(order=10)
def test_10_01_postprocess_det_filter(capfd):
    cmd = f"-m postprocess -c det_filter -i onnx_det_YoloX_Lite.json --output_preview " \
          f"--score_th 0.01 --width_th 1 --height_th 1".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=10)
def test_10_02_postprocess_det_filter(capfd):
    cmd = f"-m postprocess -c det_filter -i mmdet_det_YoloX_Lite.json --output_preview " \
          f"--score_th 0.01 --width_th 1 --height_th 1".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=10)
def _test_10_03_postprocess_det_filter(capfd):
    cmd = f"-m postprocess -c det_filter -i onnx_cls_EfficientNet_Lite4.json --output_preview " \
          f"--score_th 0.01".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=10)
def _test_10_04_postprocess_det_filter(capfd):
    cmd = f"-m postprocess -c det_filter -i mmpretrain_cls_swin_Lite.json --output_preview " \
          f"--score_th 0.01".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=11)
def test_11_01_postprocess_det_jadge(capfd):
    cmd = f"-m postprocess -c det_jadge -i onnx_det_YoloX_Lite.json --output_preview " \
          f"--ok_score_th 0.9 --ok_labels dog --ok_labels person " \
          f"--ng_score_th 0.8 --ng_labels truck --ng_labels bicycle " \
          f"--ext_score_th 0.3 --ext_labels car --ext_labels pottedplant".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=11)
def test_11_02_postprocess_det_jadge(capfd):
    cmd = f"-m postprocess -c det_jadge -i mmdet_det_YoloX_Lite.json --output_preview " \
          f"--ok_score_th 0.3 --ok_classes 16 --ok_classes 0 " \
          f"--ng_score_th 0.8 --ng_classes 7 --ng_classes 1 " \
          f"--ext_score_th 0.3 --ext_labels 2 --ext_labels pottedplant".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=11)
def test_11_03_postprocess_cls_jadge(capfd):
    cmd = f"-m postprocess -c cls_jadge -i onnx_cls_EfficientNet_Lite4.json --output_preview " \
          f"--ok_score_th 0.8 --ok_classes 249 --ok_classes 235 " \
          f"--ng_score_th 0.2 --ng_classes 250 " \
          f"--ext_score_th 0.1 --ext_classes 248".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=11)
def test_11_04_postprocess_cls_jadge(capfd):
    cmd = f"-m postprocess -c cls_jadge -i mmpretrain_cls_swin_Lite.json --output_preview " \
          f"--ok_score_th 0.8 --ok_classes 249 --ok_classes 235 " \
          f"--ng_score_th 0.2 --ng_classes 250 " \
          f"--ext_score_th 0.1 --ext_classes 248".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()
    print(result['success'])

@pytest.mark.run(order=12)
def test_12_01_postprocess_csv(capfd):
    cmd = f"-m postprocess -c csv -i onnx_det_YoloX_Lite.json " \
          f"--out_headers output_scores --out_headers output_labels".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()
    print(result['success'])

@pytest.mark.run(order=12)
def test_12_02_postprocess_csv(capfd):
    cmd = f"-m postprocess -c csv -i mmdet_det_YoloX_Lite.json " \
          f"--out_headers output_scores --out_headers output_labels".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()
    print(result['success'])

@pytest.mark.run(order=12)
def test_12_03_postprocess_csv(capfd):
    cmd = f"-m postprocess -c csv -i onnx_cls_EfficientNet_Lite4.json " \
          f"--out_headers output_scores --out_headers output_labels".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()
    print(result['success'])

@pytest.mark.run(order=12)
def test_12_04_postprocess_csv(capfd):
    cmd = f"-m postprocess -c csv -i mmpretrain_cls_swin_Lite.json " \
          f"--out_headers output_scores --out_headers output_labels".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()
    print(result['success'])

@pytest.mark.run(order=14)
def test_14_01_client_stop(capfd):
    cmd = f"-m client -c stop --svname server1 -n onnx_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=14)
def test_14_02_client_stop(capfd):
    cmd = f"-m client -c stop --svname server2 -n mmdet_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=14)
def test_14_03_client_stop(capfd):
    cmd = f"-m client -c stop --svname server1 -n onnx_cls_EfficientNet_Lite4".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=14)
def test_14_04_client_stop(capfd):
    cmd = f"-m client -c stop --svname server3 -n mmpretrain_cls_swin_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=15)
def test_15_01_client_undeploy(capfd):
    cmd = f"-m client -c undeploy --svname server1 -n onnx_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=15)
def test_15_02_client_undeploy(capfd):
    cmd = f"-m client -c undeploy --svname server2 -n mmdet_det_YoloX_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=15)
def test_15_03_client_undeploy(capfd):
    cmd = f"-m client -c undeploy --svname server1 -n onnx_cls_EfficientNet_Lite4".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

@pytest.mark.run(order=15)
def test_15_04_client_undeploy(capfd):
    cmd = f"-m client -c undeploy --svname server3 -n mmpretrain_cls_swin_Lite".split(' ')
    _, result = app.main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

