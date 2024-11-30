from cmdbox.app.commons import convert
from pathlib import Path
from PIL import Image
from typing import Dict, Tuple, Any
import logging
import json

class Postprocess(object):
    def __init__(self, logger:logging.Logger):
        """
        後処理クラスのベースクラスです。
        後処理クラスはこのクラスを継承してください。
        
        Args:
            logger (logging.Logger): ロガー
        """
        self.logger = logger

    def postprocess(self, res_str:str, output_image_file:str=None, timeout:int=60) -> Dict[str, Any]:
        outputs = json.loads(res_str)
        output_image = None
        if "output_image" in outputs and "output_image_shape" in outputs:
            img_npy = convert.b64str2npy(outputs["output_image"], outputs["output_image_shape"])
            output_image = convert.npy2img(img_npy)
            del outputs["output_image"]
            del outputs["output_image_shape"]

        result_outputs, result_output_image = self.post(outputs, output_image)
        output_image_npy = None
        output_image_b64 = None
        if result_output_image is not None:
            output_image_npy = convert.img2npy(result_output_image)
            output_image_b64 = convert.npy2b64str(output_image_npy)
            if output_image_file is not None:
                exp = Path(output_image_file).suffix
                exp = exp[1:] if exp[0] == '.' else exp
                convert.npy2imgfile(output_image_npy, output_image_file=output_image_file, image_type=exp)

        if type(result_outputs) == dict:
            if output_image_b64 is None:
                return dict(success=result_outputs)
            return dict(success=result_outputs, output_image=output_image_b64, output_image_shape=output_image_npy.shape, output_image_name=outputs["output_image_name"])
        return result_outputs

    def post(self, outputs:Dict[str, Any], output_image:Image.Image) -> Tuple[Dict[str, Any], Image.Image]:
        """
        後処理を行う関数です。

        Args:
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
            Image: 後処理結果
        """
        raise NotImplementedError()
