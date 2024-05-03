# Only for evaluation
_base_ = [
    'configs/_base_/models/swin_transformer/base_384.py',
    'configs/_base_/datasets/imagenet_bs64_swin_384.py',
    'configs/_base_/schedules/imagenet_bs1024_adamw_swin.py',
    'configs/_base_/default_runtime.py'
]
