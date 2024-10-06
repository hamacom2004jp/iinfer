from iinfer.app import common, options, injection
from iinfer.app.commons import convert
from PIL import Image
from typing import Tuple, Dict, Any
import gevent
import re
import subprocess
import tempfile

class AfterCmdInjection(injection.AfterInjection):

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
        env = {}
        ext = self.get_config('output_image_ext', 'jpeg')
        cmdline = self.get_config('cmdline', 'cwd')
        output_maxsize = self.get_config('output_maxsize', 1024*1024*5)

        try:
            with tempfile.NamedTemporaryFile(suffix='.'+ext) as img:
                img.write(convert.img2byte(output_image, format=ext))
                env['output_image'] = img.name
                with tempfile.NamedTemporaryFile('wt', suffix='.json') as out:
                    out.write(common.to_str(outputs))
                    env['outputs'] = out.name
                    cmdline = re.sub('^["\'](.*)["\']$', '\\1', cmdline)
                    outputs['cmdline'] = cmdline
                    proc = subprocess.Popen(cmdline, shell=True, env=env, text=True, encoding='utf-8',
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    cmd_output = ""
                    cmd_output_size = 0
                    while proc.poll() is None:
                        gevent.sleep(0.1)
                        o = proc.stdout.readline().strip()
                        o_len = len(o)
                        if 0 >= o_len:
                            continue
                        if o_len < output_maxsize:
                            cmd_output += o + '\n'
                            cmd_output_size += o_len
                        else:
                            o = [dict(warn=f'The captured stdout was discarded because its size was larger than {output_maxsize} bytes.')]
                    cmd_output += proc.stdout.read() # 最後のストリームは読み捨て
                    outputs['cmd_output'] = cmd_output

        except Exception as e:
            self.add_warning(outputs, str(e))

        return outputs, output_image
