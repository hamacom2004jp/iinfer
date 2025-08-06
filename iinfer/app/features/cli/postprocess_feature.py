from cmdbox.app import common, feature
from cmdbox.app.options import Options
from iinfer.app import postprocess
from typing import Dict, Any, Tuple, Union, List
import cv2
import logging
import time
import sys


class PostprocessFeature(feature.Feature):

    def _to_proc(self, f, proc:postprocess.Postprocess, timeout, format, tm,
                    output_json, output_json_append, output_image_file=None, output_csv=None, pf:List[Dict[str, float]]=[]):
        try:
            ret = None
            for line in f:
                line = line.rstrip()
                if line == "":
                    continue
                try:
                    if proc.logger.level == logging.DEBUG:
                        line_str = common.to_str(line, slise=100)
                        proc.logger.debug(f"app.main: args.mode={self.get_mode()}, args.cmd={self.get_cmd()}, proc={proc}, line={line_str}")
                    ret = proc.postprocess(line, output_image_file=output_image_file, timeout=timeout)
                    if output_csv is not None:
                        with open(output_csv, 'a' if output_json_append else 'w', encoding="utf-8") as f:
                            txt = common.print_format(ret, format, tm, output_json, output_json_append, stdout=False, pf=pf)
                            print(txt.strip(), file=f)
                    else: common.print_format(ret, format, tm, output_json, output_json_append, pf=pf)
                except Exception as e:
                    msg = {"warn":f"Invalid input. {e}"}
                    line_str = common.to_str(line, slise=100)
                    proc.logger.error(f"Invalid input.: args.mode={self.get_mode()}, args.cmd={self.get_cmd()}, proc={proc}, line={line_str}", exc_info=True)
                    common.print_format(msg, format, tm, output_json, output_json_append, pf=pf)
                    ret = msg
                tm = time.perf_counter()
                output_json_append = True
            return ret
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass

    def _exec_proc(self, input_file, stdin, proc:postprocess.Postprocess, timeout, format, tm,
                    output_json, output_json_append, output_image_file=None, output_csv=None, pf:List[Dict[str, float]]=[]):
        if input_file is not None:
            with open(input_file, 'r', encoding="UTF-8") as f:
                ret = self._to_proc(f, proc, timeout, format, tm, output_json, output_json_append,
                                output_image_file=output_image_file, output_csv=output_csv, pf=pf)
        elif stdin:
            ret = self._to_proc(sys.stdin, proc, timeout, format, tm, output_json, output_json_append,
                            output_image_file=output_image_file, output_csv=output_csv, pf=pf)
        else:
            msg = {"warn":f"Image file or stdin is empty."}
            common.print_format(msg, format, tm, output_json, output_json_append, pf=pf)
            return self.RESP_WARN, msg
        return self.RESP_SUCCESS, ret
