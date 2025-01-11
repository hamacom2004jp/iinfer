from cmdbox.app.commons import convert
from iinfer.app import common as cmn, injection
from PIL import Image
from typing import Tuple, Dict, Any, List
import numpy as np
import cv2


class AfterSegFilterInjection(injection.AfterInjection):

    def action(self, reskey:str, name:str, outputs:Dict[str, Any], output_image:Image.Image, session:Dict[str, Any]) -> Tuple[Dict[str, Any], Image.Image]:
        """
        このメソッドは推論を実行した後の処理を実行します。
        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            outputs (Dict[str, Any]): 推論結果。次の項目が含まれます。
                ・success or warn: 推論成功か警告のキーに対して、その内容が格納されます。
                ・output_image: 推論後の画像データをbase64エンコードした文字列
                ・output_image_shape: 推論後の画像データの形状（base46でコードするときに必要）
                ・output_image_name: クライアントから指定されてきた推論後の画像データの名前

            output_image (Image.Image): 推論後の画像データ
            session (Dict[str, Any]): 推論セッション。次の項目が含まれます。
                ・session: app.predict.Predict#create_session() で作成されたセッション
                ・model_img_width: モデルの入力画像の幅
                ・model_img_height: モデルの入力画像の高さ
                ・predict_obj: app.predict.Predict インスタンス
                ・labels: クラスラベルのリスト
                ・colors: ボックスの色のリスト
                ・tracker: use_trackがTrueの場合、トラッカーのインスタンス
        Returns:
            Tuple[Dict[str, Any], Image.Image]: 後処理後の推論結果と画像データのタプル
        """
        try:
            outputs = self.post_json(outputs)
            self.add_success(outputs, "filterd segment.")
        except Exception as e:
            self.add_warning(outputs, f'Error: {str(e)}')
        try:
            output_image = self.post_img(outputs, output_image)
            self.add_success(outputs, "draw segment.")
        except Exception as e:
            self.add_warning(outputs, f'Error: {str(e)}')

        return outputs, output_image

    def post_json(self, outputs:Dict[str, Any]) -> Dict[str, Any]:
        """
        outputsに対して後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_sem_seg': str,
                'output_sem_seg_shape': List[int],
                'output_sem_seg_dtype': str,
                'output_seg_logits': str,
                'output_seg_logits_shape': List[int],
                'output_seg_logits_dtype': str,
                'output_catalog': List[str],
                'output_palette': List[int],
                'output_classes': List[int],
                'output_labels': List[str],
                'output_palette': List[Tuple[int, int, int]]
            }
        }
        Args:
            outputs (Dict[str, Any]): 推論結果
        Returns:
            Dict[str, Any]: 後処理後の推論結果
        """
        logits_th = self.get_config('logits_th', -100.0)
        classes = self.get_config('classes', [])
        labels = self.get_config('labels', [])
        del_logits = self.get_config('del_logits', True)

        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_sem_seg' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg\'] must be set.')
        if 'output_sem_seg_shape' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_shape\'] must be set.')
        if 'output_sem_seg_dtype' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_dtype\'] must be set.')
        if 'output_seg_logits' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_seg_logits\'] must be set.')
        if 'output_seg_logits_shape' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_seg_logits_shape\'] must be set.')
        if 'output_seg_logits_dtype' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_seg_logits_dtype\'] must be set.')
        if 'output_catalog' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_catalog\'] must be set.')
        if 'output_classes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_classes\'] must be set.')
        if 'output_labels' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_labels\'] must be set.')

        output_catalog = data['output_catalog']
        output_labels = data['output_labels']
        chk_classes = [c for c in classes if c >= len(output_catalog)]
        if len(chk_classes) > 0:
            raise Exception(f'Invalid config classes. "{chk_classes}" not included in output_catalog index is specified.')
        if len(labels) == 0:
            labels = [output_catalog[c] for c in classes]
        chk_labels = [c for c in labels if c not in output_catalog]
        if len(chk_labels) > 0:
            raise Exception(f'Invalid config labels. "{chk_labels}" not included in output_catalog is specified.')
        cls_list = []
        for i, lbl in enumerate(output_catalog):
            if lbl in labels:
                cls_list.append(i)
        classes = list(set(cls_list+classes))

        segment = convert.b64str2npy(data['output_sem_seg'], data['output_sem_seg_shape'], data['output_sem_seg_dtype'])
        logits = convert.b64str2npy(data['output_seg_logits'], data['output_seg_logits_shape'], data['output_seg_logits_dtype'])

        if len(classes) > 0:
            data['output_classes'] = classes
            data['output_labels'] = labels
            segment = np.where(np.isin(segment, classes), segment, 0)
            logits = np.where(logits>logits_th, logits, 0)
            for c in classes:
                segment = np.where(logits[c]>logits_th, segment, 0)

        data['output_sem_seg'] = convert.npy2b64str(segment)
        if del_logits:
            del data['output_seg_logits']
            del data['output_seg_logits_shape']
            del data['output_seg_logits_dtype']

        return outputs

    def post_img(self, outputs:Dict[str, Any], output_image:Image.Image) -> Image.Image:
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。
        Args:
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 入力画像（RGB配列であること）
        Returns:
            Image: 後処理結果
        """

        nodraw = self.get_config('nodraw', False)
        if not nodraw:
            if 'success' not in outputs or type(outputs['success']) != dict:
                raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
            data = outputs['success']
            if 'output_sem_seg' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg\'] must be set.')
            if 'output_sem_seg_shape' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_shape\'] must be set.')
            if 'output_sem_seg_dtype' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_dtype\'] must be set.')
            if 'output_palette' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_palette\'] must be set.')
            segment = convert.b64str2npy(data['output_sem_seg'], data['output_sem_seg_shape'], data['output_sem_seg_dtype'])
            output_palette = data['output_palette']

            img_npy = convert.img2npy(output_image)
            img_npy = draw_segment(img_npy, segment, output_palette, nodraw)
            output_image = convert.npy2img(img_npy)

        return output_image


def draw_segment(img_npy:np.ndarray, segment:np.ndarray, colors:List[Tuple[int]], nodraw:bool=False) -> np.ndarray:
    """
    画像にマスクを描画します。

    Args:
        img_npy (np.ndarray): 元画像
        segment (np.ndarray): セグメンテーションのクラスマップ
        colors (List[Tuple[int]]): クラスごとの色のリスト
        nodraw (bool, optional): 描画しない場合はTrue. Defaults to False.

    Returns:
        Image: マスクが描画された画像
    """
    img_npy = cv2.cvtColor(img_npy, cv2.COLOR_RGB2BGR)
    masked_image = np.zeros_like(img_npy)

    for c in np.unique(segment):
        color = colors[int(c)] if colors is not None else cmn.make_color(str(int(c)))
        m = segment == c
        r = np.where(m, color[0], 0).astype(np.uint8)
        g = np.where(m, color[1], 0).astype(np.uint8)
        b = np.where(m, color[2], 0).astype(np.uint8)
        mask = cv2.merge([r, g, b])
        masked_image = cv2.addWeighted(masked_image, 1, mask[0], 1, 0)
    img_npy = cv2.addWeighted(img_npy, 0.5, masked_image, 0.5, 0)
    img_npy = cv2.cvtColor(img_npy, cv2.COLOR_BGR2RGB)
    return img_npy
