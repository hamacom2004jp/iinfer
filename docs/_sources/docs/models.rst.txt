.. -*- coding: utf-8 -*-

******************
動作確認済みモデル
******************

- 下記のモデルはiinferで推論実行できることを確認しています。
- なお、以下に示すサイトの事前学習モデルは、配布元のライセンスに従って使用してください。

Segmentation
==================

.. csv-table::

    :header: "base","frameWork","input","config","model","predict_type"
    "`PSPNet_r18(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet>`_ ","mmsegmentation","512x1024","`pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","`pspnet_r18-d8 <https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r18b-d8_512x1024_80k_cityscapes/pspnet_r18b-d8_512x1024_80k_cityscapes_20201226_063116-26928a60.pth>`_","mmseg_seg_PSPNet"
    "`PSPNet_r50(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet>`_ ","mmsegmentation","512x1024","`pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","`pspnet_r50-d8 <https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r50b-d8_512x1024_80k_cityscapes/pspnet_r50b-d8_512x1024_80k_cityscapes_20201225_094315-6344287a.pth>`_","mmseg_seg_PSPNet"
    "`PSPNet_r101(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet>`_ ","mmsegmentation","512x1024","`pspnet_r101-d8_4xb2-80k_cityscapes-512x1024.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/pspnet/pspnet_r101-d8_4xb2-80k_cityscapes-512x1024.py>`_ ","`pspnet_r101-d8 <https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r101b-d8_512x1024_80k_cityscapes/pspnet_r101b-d8_512x1024_80k_cityscapes_20201226_170012-3a4d38ab.pth>`_","mmseg_seg_PSPNet"
    "`Swin-T(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin>`_ ","mmsegmentation","512x512","`swin-tiny-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin/swin-tiny-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py>`_ ","`upernet_swin_tiny <https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_tiny_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_tiny_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210531_112542-e380ad3e.pth>`_","mmseg_seg_SwinUpernet"
    "`Swin-S(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin>`_ ","mmsegmentation","512x512","`swin-small-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin/swin-small-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py>`_ ","`upernet_swin_small <https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210526_192015-ee2fff1c.pth>`_","mmseg_seg_SwinUpernet"
    "`Swin-B(mmseg) <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin>`_ ","mmsegmentation","512x512","`swin-base-patch4-window12-in22k-384x384-pre_upernet_8xb2-160k_ade20k-512x512.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/swin/swin-base-patch4-window12-in22k-384x384-pre_upernet_8xb2-160k_ade20k-512x512.py>`_ ","`upernet_swin_base <https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_base_patch4_window12_512x512_160k_ade20k_pretrain_384x384_22K/upernet_swin_base_patch4_window12_512x512_160k_ade20k_pretrain_384x384_22K_20210531_125459-429057bf.pth>`_","mmseg_seg_SwinUpernet"
    "`SAN(mmseg) <https://github.com/open-mmlab/mmsegmentation/tree/main/configs/san>`_ ","mmsegmentation","640x640","`san-vit-b16_coco-stuff164k-640x640.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/san/san-vit-b16_coco-stuff164k-640x640.py>`_ ","`san-vit-b16 <https://download.openmmlab.com/mmsegmentation/v0.5/san/san-vit-b16_20230906-fd0a7684.pth>`_","mmseg_seg_San"
    "`SAN(mmseg) <https://github.com/open-mmlab/mmsegmentation/tree/main/configs/san>`_ ","mmsegmentation","640x640","`san-vit-l14_coco-stuff164k-640x640.py <https://github.com/open-mmlab/mmsegmentation/blob/main/configs/san/san-vit-l14_coco-stuff164k-640x640.py>`_ ","`san-vit-l14 <https://download.openmmlab.com/mmsegmentation/v0.5/san/san-vit-l14_20230907-a11e098f.pth>`_","mmseg_seg_San"

Object Detection
==================

.. csv-table::

    :header: "base","frameWork","input","config","model","predict_type"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox>`_ ","mmdetection","416x416","`yolox_tiny_8xb8-300e_coco.py <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox/yolox_tiny_8xb8-300e_coco.py>`_ ","`YOLOX-tiny <https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_tiny_8x8_300e_coco/yolox_tiny_8x8_300e_coco_20211124_171234-b4047906.pth>`_","mmdet_det_YoloX_Lite"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox>`_ ","mmdetection","640x640","`yolox_s_8xb8-300e_coco.py <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox/yolox_s_8xb8-300e_coco.py>`_ ","`YOLOX-s <https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth>`_","mmdet_det_YoloX"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox>`_ ","mmdetection","640x640","`yolox_l_8xb8-300e_coco.py <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox/yolox_l_8xb8-300e_coco.py>`_ ","`YOLOX-l <https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_l_8x8_300e_coco/yolox_l_8x8_300e_coco_20211126_140236-d3bd2b23.pth>`_","mmdet_det_YoloX"
    "`YOLOX(mmdet) <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox>`_ ","mmdetection","640x640","`yolox_x_8xb8-300e_coco.py <https://github.com/open-mmlab/mmdetection/blob/main/configs/yolox/yolox_x_8xb8-300e_coco.py>`_ ","`YOLOX-x <https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_x_8x8_300e_coco/yolox_x_8x8_300e_coco_20211126_140254-1ef88d67.pth>`_","mmdet_det_YoloX"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","`yolox_nano.py <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_nano.py>`_ ","`ONNX-YOLOX-Nano <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth>`_※1","onnx_det_YoloX_Lite"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","416x416","`yolox_tiny.py <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_tiny.py>`_","`ONNX-YOLOX-Tiny <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth>`_※1","onnx_det_YoloX_Lite"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","`yolox_s.py <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_s.py>`_","`ONNX-YOLOX-s <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth>`_※1","onnx_det_YoloX"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","`yolox_m.py <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_m.py>`_","`ONNX-YOLOX-m <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.pth>`_※1","onnx_det_YoloX"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","`yolox_l.p <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_l.py>`_","`ONNX-YOLOX-l <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_l.pth>`_※1","onnx_det_YoloX"
    "`YOLOX <https://github.com/Megvii-BaseDetection/YOLOX/#benchmark>`_ ","onnx","640x640","`yolox_x.py <https://github.com/Megvii-BaseDetection/YOLOX/blob/main/exps/default/yolox_x.py>`_","`ONNX-YOLOX-x <https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_x.pth>`_※1","onnx_det_YoloX"
    "`YOLOv3 <https://github.com/onnx/models/tree/main/validated/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","","`ONNX-YOLOv3-10 <https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx>`_","onnx_det_YoloV3"
    "`YOLOv3 <https://github.com/onnx/models/tree/main/validated/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","","`ONNX-YOLOv3-12 <https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-12.onnx>`_","onnx_det_YoloV3"
    "`YOLOv3 <https://github.com/onnx/models/tree/main/validated/vision/object_detection_segmentation/yolov3>`_ ","onnx","416x416","","`ONNX-YOLOv3-12-int8 <https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-12-int8.onnx>`_","onnx_det_YoloV3"
    "`TinyYOLOv3 <https://github.com/onnx/models/tree/main/validated/vision/object_detection_segmentation/tiny-yolov3>`_ ","onnx","416x416","","`ONNX-TinyYOLOv3 <https://github.com/onnx/models/blob/main/validated/vision/object_detection_segmentation/tiny-yolov3/model/tiny-yolov3-11.onnx>`_","onnx_det_TinyYoloV3"

- ※1 : `pth2onnx <https://github.com/hamacom2004jp/pth2onnx>`_ を使用してONNX形式に変換して使用*

Image Classification
======================

.. csv-table::

    :header: "base","frameWork","input","config","model","predict_type"
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","224x224","`swin-tiny_16xb64_in1k.py <https://github.com/open-mmlab/mmclassification/blob/master/configs/swin_transformer/swin-tiny_16xb64_in1k.py>`_ ","`swin-tiny_16xb64_in1k <https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_tiny_224_b16x64_300e_imagenet_20210616_090925-66df6be6.pth>`_","mmpretrain_cls_swin_Lite"
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","224x224","`swin-small_16xb64_in1k.py <https://github.com/open-mmlab/mmclassification/blob/master/configs/swin_transformer/swin-small_16xb64_in1k.py>`_","`swin-small_16xb64_in1k <https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_small_224_b16x64_300e_imagenet_20210615_110219-7f9d988b.pth>`_","mmpretrain_cls_swin_Lite"
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","384x384","`swin-base_16xb64_in1k-384px.py <https://github.com/open-mmlab/mmclassification/blob/master/configs/swin_transformer/swin-base_16xb64_in1k-384px.py>`_","`swin-base_16xb64_in1k-384px <https://download.openmmlab.com/mmclassification/v0/swin-transformer/convert/swin_base_patch4_window12_384-02c598a4.pth>`_","mmpretrain_cls_swin"
    "`Swin Transformer <https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer>`_ ","mmpretrain","384x384","`swin-large_16xb64_in1k-384px.py <https://github.com/open-mmlab/mmclassification/blob/master/configs/swin_transformer/swin-large_16xb64_in1k-384px.py>`_","`swin-large_16xb64_in1k-384px <https://download.openmmlab.com/mmclassification/v0/swin-transformer/convert/swin_large_patch4_window12_384_22kto1k-0a40944b.pth>`_","mmpretrain_cls_swin"
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/validated/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","","`EfficientNet-Lite4-11 <https://github.com/onnx/models/blob/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11.onnx>`_","onnx_cls_EfficientNet_Lite4"
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/validated/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","","`EfficientNet-Lite4-11-int8 <https://github.com/onnx/models/blob/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11-int8.onnx>`_","onnx_cls_EfficientNet_Lite4"
    "`EfficientNet-Lite4 <https://github.com/onnx/models/tree/main/validated/vision/classification/efficientnet-lite4>`_ ","onnx","224x224","","`EfficientNet-Lite4-11-qdq <https://github.com/onnx/models/blob/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11-qdq.onnx>`_","onnx_cls_EfficientNet_Lite4"

Face Detection and Recognition
================================

.. csv-table::

    :header: "base","frameWork","input","config","model","predict_type"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","","`antelopev2 <https://drive.google.com/file/d/18wEUfMNohBJ4K3Ly5wpTejPfDzp-8fI8/view?usp=sharing>`_","insightface_det"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","","`buffalo_l <https://drive.google.com/file/d/1qXsQJ8ZT42_xSmWIYy85IcidpiZudOCB/view?usp=sharing>`_","insightface_det"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","","`buffalo_m <https://drive.google.com/file/d/1net68yNxF33NNV6WP7k56FS6V53tq-64/view?usp=sharing>`_","insightface_det"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","","`buffalo_s <https://drive.google.com/file/d/1pKIusApEfoHKDjeBTXYB3yOQ0EtTonNE/view?usp=sharing>`_","insightface_det"
    "`insightface <https://github.com/deepinsight/insightface/tree/master/python-package>`_ ","insightface","640x640","","`buffalo_sc <https://drive.google.com/file/d/19I-MZdctYKmVf3nu5Da3HS6KH5LBfdzG/view?usp=sharing>`_","insightface_det"

