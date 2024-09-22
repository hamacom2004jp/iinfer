
from iinfer.app import app
from pathlib import Path
from unittest.mock import patch
import iinfer
import os
import pytest
import time
import shutil
import subprocess
import sys


@pytest.fixture(scope='module', autouse=True)
def fixture_server():
    python = Path(iinfer.__file__).parent.parent / '.venv' / 'Scripts' / 'python.exe'
    cmd = f"{python} -m iinfer -m server -c start --svname server".split(' ')
    proc1 = subprocess.Popen(cmd)
    #cmd = f"{python} -m iinfer -m server -c start --svname server1".split(' ')
    #proc2 = subprocess.Popen(cmd)
    #cmd = f"{python} -m iinfer -m server -c start --svname server2".split(' ')
    #proc3 = subprocess.Popen(cmd)
    shutil.rmtree("mmdetection", ignore_errors=True)
    shutil.rmtree("mmpretrain", ignore_errors=True)
    shutil.rmtree("mmsegmentation", ignore_errors=True)
    time.sleep(15)
    yield
    #cmd = f"{python} -m iinfer -m server -c stop --svname server2 --timeout 15".split(' ')
    #subprocess.run(cmd)
    #cmd = f"{python} -m iinfer -m server -c stop --svname server1 --timeout 15".split(' ')
    #subprocess.run(cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server --timeout 15".split(' ')
    subprocess.run(cmd)


@pytest.mark.run(order=0)
def test_0_client_read_dir_capture(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "read_dir",
           "--glob_str",
           "tests/*.jpg",
           "--read_input_type",
           "capture",
           "--image_type",
           "capture",
           "--root_dir",
           ".",
           "--polling",
           "--polling_count",
           "2",
           "--polling_interval",
           "1",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=1)
def test_1_client_read_dir_filelist(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "read_dir",
           "--glob_str",
           "tests/*.jpg",
           "--read_input_type",
           "filelist",
           "--image_type",
           "capture",
           "--root_dir",
           ".",
           "--polling",
           "--polling_count",
           "2",
           "--polling_interval",
           "1",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=2)
def test_2_client_read_dir_jpeg(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "read_dir",
           "--glob_str",
           "tests/*.jpg",
           "--read_input_type",
           "jpeg",
           "--image_type",
           "capture",
           "--root_dir",
           ".",
           "--polling",
           "--polling_count",
           "2",
           "--polling_interval",
           "1",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=3)
def test_3_client_read_dir_bmp(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "read_dir",
           "--glob_str",
           "tests/*.jpg",
           "--read_input_type",
           "bmp",
           "--image_type",
           "bmp",
           "--root_dir",
           ".",
           "--include_hidden",
           "--polling",
           "--polling_count",
           "2",
           "--polling_interval",
           "1",
           "--output_csv",
           "read_dir.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=4)
def test_4_client_read_dir_png(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "read_dir",
           "--glob_str",
           "tests/*.jpg",
           "--read_input_type",
           "png",
           "--image_type",
           "png",
           "--root_dir",
           ".",
           "--polling",
           "--polling_count",
           "2",
           "--polling_interval",
           "1",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=5)
def test_5_client_capture_capture(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "capture",
           "--capture_device",
           "0",
           "--image_type",
           "capture",
           "--capture_frame_width",
           "640",
           "--capture_frame_height",
           "480",
           "--capture_fps",
           "5",
           "--capture_count",
           "3",
           "--output_preview",
           "--output_csv",
           "capture.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=6)
def test_6_client_capture_jpeg(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "capture",
           "--capture_device",
           "0",
           "--image_type",
           "capture",
           "--capture_frame_width",
           "640",
           "--capture_frame_height",
           "480",
           "--capture_fps",
           "5",
           "--capture_count",
           "3",
           "--output_preview",
           "--output_csv",
           "capture.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=7)
def test_7_client_capture_jpeg(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "capture",
           "--capture_device",
           "-1",
           "--image_type",
           "capture",
           "--capture_frame_width",
           "-10",
           "--capture_frame_height",
           "-10",
           "--capture_fps",
           "-1",
           "--capture_count",
           "-1",
           "--output_preview",
           "--output_csv",
           "capture.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=8)
def test_8_client_capture_bmp(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "capture",
           "--capture_device",
           "0",
           "--image_type",
           "bmp",
           "--capture_frame_width",
           "640",
           "--capture_frame_height",
           "480",
           "--capture_fps",
           "5",
           "--capture_count",
           "3",
           "--output_preview",
           "--output_csv",
           "capture.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=9)
def test_9_client_capture_png(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "capture",
           "--capture_device",
           "0",
           "--image_type",
           "png",
           "--capture_frame_width",
           "640",
           "--capture_frame_height",
           "480",
           "--capture_fps",
           "5",
           "--capture_count",
           "3",
           "--output_preview",
           "--output_csv",
           "capture.csv",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert result != ''


@pytest.mark.run(order=10)
def test_10_client_deploy_lnsightface(capfd):
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
           "lnsightface",
           "--model_file",
           "https://drive.usercontent.google.com/download?id=1pKIusApEfoHKDjeBTXYB3yOQ0EtTonNE&export=download&authuser=0&confirm=t&uuid=00c74cef-3534-49a3-942b-582771fad908&at=APZUnTXNi6MNLsiK-EMqx_cRMJ8a%3A1723645526732",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "insightface_det",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=11)
def test_11_client_deploy_san(capfd):
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
           "san",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/san/san-vit-b16_20230906-fd0a7684.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmseg/san-vit-b16_coco-stuff164k-640x640.py",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmseg_seg_San",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_seg_filter_injection",
           "--after_injection_type",
           "after_seg_bbox_injection",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmseg_seg_San",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=12)
def test_12_client_deploy_upernet(capfd):
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
           "upernet",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210526_192015-ee2fff1c.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmseg/swin-small-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmseg/swin-tiny-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py",
           "--model_img_width",
           "512",
           "--model_img_height",
           "512",
           "--predict_type",
           "mmseg_seg_SwinUpernet",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_seg_filter_injection",
           "--after_injection_type",
           "after_seg_bbox_injection",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmseg_seg_SwinUpernet",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=13)
def test_13_client_deploy_yolox(capfd):
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
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_tta.py",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmdet_det_YoloX",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_type",
           "after_det_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmdet_det_YoloX",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=14)
def test_14_client_deploy_yolox(capfd):
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
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_tta.XX",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "mmdet_det_YoloX",
           "--label_file",
           "iinfer/extensions/label_coco.ttt",
           "--before_injection_type",
           "before_grayimg_injection2",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.XXX",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_type",
           "after_det_jadge_injection2",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.XXX",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmdet_det_YoloX",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()


@pytest.mark.run(order=15)
def test_15_client_deploy_effnet(capfd):
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
           "effnet",
           "--model_file",
           "https://github.com/onnx/models/raw/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11-qdq.onnx",
           "--model_img_width",
           "224",
           "--model_img_height",
           "224",
           "--predict_type",
           "onnx_cls_EfficientNet_Lite4",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_cls_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=16)
def test_16_client_deploy_pspnet(capfd):
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
           "pspnet",
           "--model_file",
           "https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r18b-d8_512x1024_80k_cityscapes/pspnet_r18b-d8_512x1024_80k_cityscapes_20201226_063116-26928a60.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmseg/pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmseg/pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py",
           "--model_img_width",
           "512",
           "--model_img_height",
           "512",
           "--predict_type",
           "mmseg_seg_PSPNet",
           "--label_file",
           "iinfer/extensions/label_cityscapes.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_seg_filter_injection",
           "--after_injection_type",
           "after_seg_bbox_injection",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmseg_seg_PSPNet",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=17)
def test_17_client_deploy_swin(capfd):
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
           "swin",
           "--model_file",
           "https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_small_224_b16x64_300e_imagenet_20210615_110219-7f9d988b.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmpretrain/swin-small_16xb64_in1k.py",
           "--model_img_width",
           "384",
           "--model_img_height",
           "384",
           "--predict_type",
           "mmpretrain_cls_swin",
           "--label_file",
           "iinfer/extensions/label_imagenet1k.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_cls_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "mmpretrain_cls_swin",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=18)
def test_18_client_deploy_yolo3(capfd):
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
           "yolo3",
           "--model_file",
           "https://github.com/onnx/models/raw/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx",
           "--model_img_width",
           "416",
           "--model_img_height",
           "416",
           "--predict_type",
           "onnx_det_YoloV3",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_type",
           "after_det_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--overwrite",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=19)
def test_19_client_deploy_custom(capfd):
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
           "custom",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_tta.py",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "Custom",
           "--custom_predict_py",
           "iinfer/tools/datas/predicts/mmdet_det_YoloX2.py",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--before_injection_py",
           "iinfer/tools/datas/injections/before_grayimg_injection2.py",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_type",
           "after_det_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/injections/after_det_filter_injection2.py",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "Custom",
           "--custom_train_py",
           "iinfer/tools/datas/trains/mmdet_det_YoloX2.py",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--output_json",
           "pred.json",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=20)
def test_20_client_deploy_custom(capfd):
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
           "custom",
           "--model_file",
           "https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py",
           "--model_conf_file",
           "iinfer/extensions/configs/mmdet/yolox_tta.py",
           "--model_img_width",
           "640",
           "--model_img_height",
           "640",
           "--predict_type",
           "Custom",
           "--custom_predict_py",
           "iinfer/tools/datas/predicts/mmdet_det_YoloX2.py",
           "--label_file",
           "iinfer/extensions/label_coco.txt",
           "--before_injection_type",
           "before_grayimg_injection",
           "--before_injection_conf",
           "iinfer/tools/datas/injections/before_injection.json",
           "--before_injection_py",
           "iinfer/tools/datas/injections/before_grayimg_injection2.XXX",
           "--after_injection_type",
           "after_det_filter_injection",
           "--after_injection_type",
           "after_det_jadge_injection",
           "--after_injection_conf",
           "iinfer/tools/datas/injections/after_injection.json",
           "--after_injection_py",
           "iinfer/tools/datas/injections/after_det_filter_injection2.XXX",
           "--overwrite",
           "--train_dataset",
           "iinfer/extensions/data",
           "--train_dataset_upload",
           "--train_type",
           "Custom",
           "--custom_train_py",
           "iinfer/tools/datas/trains/mmdet_det_YoloX2.py",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "60",
           "--output_json",
           "pred.json",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()


@pytest.mark.run(order=21)
def test_21_client_deploy_list_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy_list",
           "--retry_count",
           "1",
           "--retry_interval",
           "1",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=22)
def test_22_client_deploy_list_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "deploy_list",
           "--retry_count",
           "1",
           "--retry_interval",
           "-1",
           "--timeout",
           "-1",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()


@pytest.mark.run(order=23)
def test_23_client_start_lnsightface(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "lnsightface",
           "--model_provider",
           "CUDAExecutionProvider",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=24)
def test_24_client_start_san(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "san",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=25)
def test_25_client_start_upernet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "upernet",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=26)
def test_26_client_start_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "yolox",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=27)
def test_27_client_start_effnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "effnet",
           "--model_provider",
           "CUDAExecutionProvider",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=28)
def test_28_client_start_pspnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "pspnet",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=29)
def test_29_client_start_swin(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "swin",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=30)
def test_30_client_start_yolo3(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "yolo3",
           "--model_provider",
           "CUDAExecutionProvider",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=31)
def test_31_client_start_custom(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "start",
           "--name",
           "custom",
           "--use_track",
           "--gpuid",
           "0",
           "--timeout",
           "120",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=32)
def test_32_client_predict_lnsightface(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "lnsightface",
           "--input_file",
           "capture.csv",
           "--nodraw",
           "--pred_input_type",
           "capture",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=33)
def test_33_client_predict_san(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "san",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=34)
def test_34_client_predict_upernet(capfd, monkeypatch):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "upernet",
           "--stdin",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    with open('tests/dog.jpg', 'br') as f:
        sys.stdin = f.buffer = f
        _, result = app.IinferApp().main(args_list=cmd)
        out, err = capfd.readouterr()
        print(out)
        assert 'success' in result.keys()


@pytest.mark.run(order=35)
def test_35_client_predict_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "yolox",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=36)
def test_36_client_predict_effnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "effnet",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=37)
def test_37_client_predict_pspnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "pspnet",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=38)
def test_38_client_predict_swin(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "swin",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "60",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=39)
def test_39_client_predict_yolo3(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "yolo3",
           "--input_file",
           "tests/dog.jpg",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=40)
def test_40_client_predict_custom(capfd, monkeypatch):
    cmd = ["-m",
           "client",
           "-c",
           "predict",
           "--name",
           "custom",
           "--stdin",
           "--nodraw",
           "--pred_input_type",
           "jpeg",
           "--output_image",
           "pred.jpg",
           "--output_preview",
           "--timeout",
           "15",
           "--debug"]

    with open('tests/dog.jpg', 'br') as f:
        sys.stdin = f.buffer = f
        _, result = app.IinferApp().main(args_list=cmd)
        out, err = capfd.readouterr()
        print(out)
        assert 'success' in result.keys()


@pytest.mark.run(order=41)
def test_41_client_stop_lnsightface(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "lnsightface",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=42)
def test_42_client_stop_san(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "san",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=43)
def test_43_client_stop_upernet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "upernet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=44)
def test_44_client_stop_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "yolox",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=45)
def test_45_client_stop_effnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "effnet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=46)
def test_46_client_stop_pspnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "pspnet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=47)
def test_47_client_stop_swin(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "swin",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=48)
def test_48_client_stop_yolo3(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "yolo3",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=49)
def test_49_client_stop_custom(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "stop",
           "--name",
           "custom",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=50)
def test_50_client_undeploy_lnsightface(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "lnsightface",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=51)
def test_51_client_undeploy_san(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "san",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=52)
def test_52_client_undeploy_upernet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "upernet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=53)
def test_53_client_undeploy_yolox(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "yolox",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=54)
def test_54_client_undeploy_effnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "effnet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=55)
def test_55_client_undeploy_pspnet(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "pspnet",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=56)
def test_56_client_undeploy_swin(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "swin",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=57)
def test_57_client_undeploy_yolo3(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "yolo3",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=58)
def test_58_client_undeploy_custom(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "undeploy",
           "--name",
           "custom",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=59)
def test_59_client_file_list_local(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_list",
           "--svpath",
           "/",
           "--local_data",
           "C:/Users/hama/.iinfer",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=60)
def test_60_client_file_list_server(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_list",
           "--svpath",
           "/",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=61)
def test_61_client_file_mkdir_local(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_mkdir",
           "--svpath",
           "file_mkdir",
           "--local_data",
           "C:/Users/hama/.iinfer",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=62)
def test_62_client_file_mkdir_server(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_mkdir",
           "--svpath",
           "file_mkdir",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=63)
def test_63_client_file_rmdir_local(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_rmdir",
           "--svpath",
           "file_mkdir",
           "--local_data",
           "C:/Users/hama/.iinfer",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=64)
def test_64_client_file_rmdir_server(capfd):
    cmd = ["-m",
           "client",
           "-c",
           "file_rmdir",
           "--svpath",
           "file_mkdir",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

