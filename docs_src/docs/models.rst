.. -*- coding: utf-8 -*-

******************
動作確認済みモデル
******************

下記のモデルはiinferで推論実行できることを確認しています。

Object Detection
==================

.. csv-table::

    :header: "base","frameWork","input","model","predict_type","memo"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","416x416","YOLOX-tiny","mmdet_det_YoloX_Lite",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-s","mmdet_det_YoloX",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-l","mmdet_det_YoloX",""
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox>`_ ","mmdetection","640x640","YOLOX-x","mmdet_det_YoloX",""
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","YOLOX-Nano","onnx_det_YoloX_Lite","\*1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","YOLOX-Tiny","onnx_det_YoloX_Lite","\*1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-s","onnx_det_YoloX","\*1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-m","onnx_det_YoloX","\*1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-l","onnx_det_YoloX","\*1"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","YOLOX-x","onnx_det_YoloX","\*1"
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-10","onnx_det_YoloV3",""
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-12","onnx_det_YoloV3",""
    "`YOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","YOLOv3-12-int8","onnx_det_YoloV3",""
    "`TinyYOLOv3 <https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3>`_ ","onnx","416x416","TinyYOLOv3","onnx_det_TinyYoloV3",""

*1）`pth2onnx <https://github.com/hamacom2004jp/pth2onnx>`_ を使用してONNX形式に変換して使用*

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

