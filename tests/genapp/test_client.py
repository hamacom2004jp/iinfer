
from iinfer.app import app
from pathlib import Path
from unittest.mock import patch
import iinfer
import os
import pytest
import time
import subprocess


@pytest.fixture(scope='module', autouse=True)
def fixture_server():
    python = Path(iinfer.__file__).parent.parent / '.venv' / 'Scripts' / 'python.exe'
    cmd = f"{python} -m iinfer -m server -c start --svname server1".split(' ')
    proc1 = subprocess.Popen(cmd)
    cmd = f"{python} -m iinfer -m server -c start --svname server2".split(' ')
    proc2 = subprocess.Popen(cmd)
    cmd = f"{python} -m iinfer -m server -c start --svname server3".split(' ')
    proc3 = subprocess.Popen(cmd)
    time.sleep(15)
    yield
    cmd = f"{python} -m iinfer -m server -c stop --svname server3 --timeout 15".split(' ')
    subprocess.run(cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server2 --timeout 15".split(' ')
    subprocess.run(cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server1 --timeout 15".split(' ')
    subprocess.run(cmd)


@pytest.mark.run(order=0)
def test_0_client_deploy_lnsightface(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://drive.google.com/file/d/1pKIusApEfoHKDjeBTXYB3yOQ0EtTonNE/view?usp=sharing",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "insightface_det",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=1)
def test_1_client_deploy_upernet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210526_192015-ee2fff1c.pth",
           "--model_img_width",
           "512",
           "--model_img_height",
           "512",
           "--predict_type",
           "mmseg_seg_SwinUpernet",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=2)
def test_2_client_deploy_effnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://github.com/onnx/models/blob/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11-qdq.onnx",
           "--model_img_width",
           "224",
           "--model_img_height",
           "224",
           "--predict_type",
           "onnx_cls_EfficientNet_Lite4",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=3)
def test_3_client_deploy_swin(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_small_224_b16x64_300e_imagenet_20210615_110219-7f9d988b.pth",
           "--model_img_width",
           "384",
           "--model_img_height",
           "384",
           "--predict_type",
           "mmpretrain_cls_swin",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=4)
def test_4_client_deploy_san(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/san/san-vit-b16_20230906-fd0a7684.pth",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmseg_seg_San",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=5)
def test_5_client_deploy_yolo3(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx",
           "--model_img_width",
           "416",
           "--model_img_height",
           "416",
           "--predict_type",
           "onnx_det_YoloV3",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=6)
def test_6_client_deploy_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmdet_det_YoloX",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=7)
def test_7_client_deploy_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "redis",
           "--port",
           "6380",
           "--password",
           "password2",
           "--svname",
           "serverX",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.XXX.pth",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmdet_det_YoloY",
           "--label_file",
           "iinfer/extensions/label_coco.ttt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.XXX",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.XXX",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()


@pytest.mark.run(order=8)
def test_8_client_deploy_custom(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "Custom",
           "--custom_predict_py",
           "iinfer/tools/datas/libs/mmdet_det_YoloX2.py",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60",
           "--output_json",
           "pred.json"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=9)
def test_9_client_deploy_custom(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "Custom",
           "--custom_predict_py",
           "iinfer/tools/datas/libs/mmdet_det_YoloX2.py",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.XXX",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.XXX",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60",
           "--output_json",
           "pred.json"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()


@pytest.mark.run(order=10)
def test_10_client_deploy_pspnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy",
           "--host",
           "localhost",
           "--port",
           "6379",
           "--password",
           "password",
           "--svname",
           "server",
           "--name",
           "yolox",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r18b-d8_512x1024_80k_cityscapes/pspnet_r18b-d8_512x1024_80k_cityscapes_20201226_063116-26928a60.pth",
           "--model_img_width",
           "512",
           "--model_img_height",
           "512",
           "--predict_type",
           "mmseg_seg_PSPNet",
           "--label_file",
           "iinfer/extensions/label_cityscapes.txt",
           "--before_injection_conf",
           "iinfer/extensions/injection/before_gray_injection.json",
           "--before_injection_py",
           "iinfer/extensions/injection/before_grayimg_injection2.py",
           "--after_injection_conf",
           "iinfer/tools/datas/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/after_det_filter_injection2.py",
           "--overwrite",
           "--retry_count",
           "3",
           "--retry_interval",
           "5",
           "--timeout",
           "60"]
          
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

