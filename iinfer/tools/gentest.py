from pathlib import Path
from cmdbox.app import options, common
import glob
import io

"""
def main():
    option = options.Options()
    outdir = Path("tests") / "genapp"
    common.rmdirs(outdir)
    common.mkdirs(outdir)

    opt_files = glob.glob(f"iinfer/tools/datas/*.json", recursive=False)
    buffer =  io.StringIO()
    buffer.write(BASE_TEST)
    index = 0
    for opt_file in opt_files:
        opt = common.loadopt(opt_file)
        opt_list = option.mk_opt_list(opt)
        cmd_line = TEMP_TEST.format(index=index, mode_key=opt["mode"], cmd_key=opt["cmd"], opt_list=' " \\\n\t\t  "'.join(opt_list[0]))
        buffer.write(cmd_line)
        index += 1

    testfile = outdir / f"test_gentest.py"
    with open(testfile, "w", encoding="utf-8") as f:
        f.write(buffer.getvalue())
"""

def main():
    option = options.Options()
    outdir = Path("tests") / "genapp"
    common.rmdirs(outdir)
    common.mkdirs(outdir)

    def _set(tv, opt_name, opt_map):
        if type(tv) == list:
            for t in tv:
                if t is None or type(t) == bool and not t:
                    continue
                opt_map["opt_list"].append(f"--{opt_name}")
                if type(t) == bool:
                    continue
                if isinstance(t, Path):
                    opt_map["opt_list"].append(str(t).replace("\\", "/"))
                else:
                    opt_map["opt_list"].append(str(t))
            return
        elif tv is None or not tv:
            return
        opt_map["opt_list"].append(f"--{opt_name}")
        if type(tv) == bool:
            return
        if isinstance(tv, Path):
            opt_map["opt_list"].append(str(tv).replace("\\", "/"))
        else:
            opt_map["opt_list"].append(str(tv))

    for mode_key in option.get_mode_keys():
        if mode_key == '':
            continue
        index = 0
        buffer =  io.StringIO()
        buffer.write(BASE_TEST)
        for cmd_key in option.get_cmd_keys(mode_key):
            choices = option.get_cmd_choices(mode_key, cmd_key)
            names = set()
            for choice in choices:
                if "test_true" in choice:
                    names |= set(choice["test_true"].keys())
                if "test_false" in choice:
                    names |= set(choice["test_false"].keys())
            names = list(names)
            if len(names) <= 0:
                continue
            opt_list_true = dict()
            opt_list_chk = dict()
            opt_list_false = dict()
            opt_list_stdin = dict()
            for name in names:
                opt_list_true[name] = dict(opt_list=[], judge=True)
                opt_list_chk[name] = dict(opt_list=[], judge=False)
                opt_list_false[name] = dict(opt_list=[], judge=False)
                for choice in choices:
                    set_false = True
                    if "test_false" in choice and name in choice["test_false"]:
                        testval = choice["test_false"][name]
                        _set(testval, choice["opt"], opt_list_chk[name])
                        _set(testval, choice["opt"], opt_list_false[name])
                        set_false = False
                    if "test_true" in choice:
                        if name in choice["test_true"]:
                            testval = choice["test_true"][name]
                        else:
                            testval = choice["test_true"][list(choice["test_true"].keys())[0]]
                        _set(testval, choice["opt"], opt_list_true[name])
                        if set_false: _set(testval, choice["opt"], opt_list_false[name])
                    if "test_stdin" in choice:
                        if name in choice["test_stdin"]:
                            testval = choice["test_stdin"][name]
                        else:
                            testval = choice["test_stdin"][list(choice["test_stdin"].keys())[0]]
                        opt_list_stdin[name] = testval
                if len(opt_list_true[name]["opt_list"]) <= 0:
                    del opt_list_true[name]
                if len(opt_list_chk[name]["opt_list"]) <= 0:
                    del opt_list_chk[name]
                    del opt_list_false[name]

            test_assert = option.get_cmd_attr(mode_key, cmd_key, "test_assert")
            test_assert = test_assert if test_assert is not None else "assert 'success' {judge} result.keys()"
            jointxt = '",\n           "'
            for name in names:
                temp = TEMP_TEST
                stdin_file = ""
                if name in opt_list_stdin and opt_list_stdin[name] is not None:
                    temp = TEMP_TEST_STDIN
                    stdin_file = opt_list_stdin[name]
                temp = temp.replace("{test_assert}", test_assert)
                if name in opt_list_true:
                    opt_list = ["-m", mode_key, "-c", cmd_key] + opt_list_true[name]["opt_list"]
                    opt_list = [str(x) for x in opt_list if str(x) != "--debug"] + ["--debug"]
                    cmd_line = temp.format(index=index, mode_key=mode_key, cmd_key=cmd_key,
                                                name=name, judge="in", opt_list=jointxt.join(opt_list),
                                                stdin_file=stdin_file)
                    buffer.write(cmd_line)
                    index += 1

                if name in opt_list_false:
                    opt_list = ["-m", mode_key, "-c", cmd_key] + opt_list_false[name]["opt_list"]
                    opt_list = [str(x) for x in opt_list if str(x) != "--debug"] + ["--debug"]
                    cmd_line = temp.format(index=index, mode_key=mode_key, cmd_key=cmd_key,
                                                name=name, judge="not in", opt_list=jointxt.join(opt_list),
                                                stdin_file=stdin_file)
                    buffer.write(cmd_line)
                    index += 1

        testfile = outdir / f"test_{mode_key}.py"
        with open(testfile, "w", encoding="utf-8") as f:
            f.write(buffer.getvalue())


TEMP_TEST = """
@pytest.mark.run(order={index})
def test_{index}_{mode_key}_{cmd_key}_{name}(capfd):
    cmd = ["{opt_list}"]

    _, result = app.IinferApp.getInstance().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    {test_assert}

"""

TEMP_TEST_STDIN = """
@pytest.mark.run(order={index})
def test_{index}_{mode_key}_{cmd_key}_{name}(capfd, monkeypatch):
    cmd = ["{opt_list}"]

    with open('{stdin_file}', 'br') as f:
        sys.stdin = f.buffer = f
        _, result = app.IinferApp.getInstance().main(args_list=cmd)
        out, err = capfd.readouterr()
        print(out)
        {test_assert}

"""

BASE_TEST = """
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
    shutil.rmtree("mmdetection", ignore_errors=True)
    shutil.rmtree("mmpretrain", ignore_errors=True)
    shutil.rmtree("mmsegmentation", ignore_errors=True)
    time.sleep(15)
    yield
    cmd = f"{python} -m iinfer -m server -c stop --svname server --timeout 15".split(' ')
    subprocess.run(cmd)

"""


if __name__ == "__main__":
    main()
