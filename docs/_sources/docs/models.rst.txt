.. -*- coding: utf-8 -*-

******************
動作確認済みモデル
******************

- 下記のモデルはiinferで推論実行できることを確認しています。
- なお、以下に示すサイトの事前学習モデルは、配布元のライセンスに従って使用してください。

Segmentation
==================

.. csv-table::

    :header: "base","frameWork","input","model","predict_type","memo"
    "`PSPNet_r18(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","mmsegmentation","512x1024","pspnet_r18-d8","mmseg_seg_PSPNet",""
    "`PSPNet_r50(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","mmsegmentation","512x1024","pspnet_r50-d8","mmseg_seg_PSPNet",""
    "`PSPNet_r101(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r101-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","mmsegmentation","512x1024","pspnet_r101-d8","mmseg_seg_PSPNet",""

Object Detection
==================

.. csv-table::

    :header: "base","frameWork","input","model","predict_type","memo"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","416x416","YOLOX-tiny","mmdet_det_YoloX_Lite",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-s","mmdet_det_YoloX",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-l","mmdet_det_YoloX",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-x","mmdet_det_YoloX",""
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","YOLOX-Nano","onnx_det_YoloX_Lite","※1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","YOLOX-Tiny","onnx_det_YoloX_Lite","※1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-s","onnx_det_YoloX","※1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-m","onnx_det_YoloX","※1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-l","onnx_det_YoloX","※1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-x","onnx_det_YoloX","※1"
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-10","onnx_det_YoloV3",""
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-12","onnx_det_YoloV3",""
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-12-int8","onnx_det_YoloV3",""
    "`TinyYOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3>`_ ","onnx","416x416","TinyYOLOv3","onnx_det_TinyYoloV3",""

- ※1 : `pth2onnx <https://github.com/hamacom2004jp/pth2onnx>`_ を使用してONNX形式に変換して使用*

Image Classification
======================

.. csv-table::

    :header: "base","frameWork","input","model","predict_type","memo"
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","224x224","swin-tiny_16xb64_in1k","mmpretrain_cls_swin_Lite",""
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","224x224","swin-small_16xb64_in1k","mmpretrain_cls_swin_Lite",""
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","384x384","swin-base_16xb64_in1k-384px","mmpretrain_cls_swin",""
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","384x384","swin-large_16xb64_in1k-384px","mmpretrain_cls_swin",""
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","EfficientNet-Lite4-11","onnx_cls_EfficientNet_Lite4",""
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","EfficientNet-Lite4-11-int8","onnx_cls_EfficientNet_Lite4",""
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","EfficientNet-Lite4-11-qdq","onnx_cls_EfficientNet_Lite4",""

Face Detection and Recognition
================================

.. csv-table::

    :header: "base","frameWork","input","model","predict_type","memo"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","antelopev2","insightface_det",""
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","buffalo_l","insightface_det",""
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","buffalo_m","insightface_det",""
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","buffalo_s","insightface_det",""
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","buffalo_sc","insightface_det",""

