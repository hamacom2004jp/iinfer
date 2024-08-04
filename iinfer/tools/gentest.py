from pathlib import Path
from iinfer.app import common, options
import glob
import io


def main():
    option = options.Options()
    outdir = Path("tests") / "genapp"
    common.rmdirs(outdir)
    common.mkdirs(outdir)
    for mode_key in option.get_mode_keys():
        if mode_key == '':
            continue
        buffer =  io.StringIO(BASE_TEST)
        for index, cmd_key in enumerate(option.get_cmd_keys(mode_key)):
            opt_files = glob.glob(f"iinfer/tools/datas/*_{mode_key}_{cmd_key}.json", recursive=False)
            for opt_file in opt_files:
                opt = common.loadopt(opt_file)
                opt_list = option.mk_opt_list(opt)
                cmd_line = TEMP_TEST.format(index=index, mode_key=mode_key, cmd_key=cmd_key, opt_list=" ".join(opt_list[0]))
                buffer.write(cmd_line)

        testfile = outdir / f"test_{mode_key}.py"
        with open(testfile, "w", encoding="utf-8") as f:
            f.write(buffer.getvalue())


TEMP_TEST = """
@pytest.mark.run(order={index})
def test_{index}_{mode_key}_{cmd_key}(capfd):
    cmd = f"{opt_list}".split(' ')
    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()

"""

BASE_TEST = """
from iinfer.app import app
from pathlib import Path
from unittest.mock import patch
import iinfer
import os
import pytest
import time
import subprocess


@pytest.fixture(scope='module', autouse=True)
def fixture_server():
    python = Path(iinfer.__file__).parent.parent / '.venv' / 'Scripts' / 'python.exe'
    cmd = f"{python} -m iinfer -m server -c start --svname server1".split(' ')
    proc1 = subprocess.Popen(cmd)
    cmd = f"{python} -m iinfer -m server -c start --svname server2".split(' ')
    proc2 = subprocess.Popen(cmd)
    cmd = f"{python} -m iinfer -m server -c start --svname server3".split(' ')
    proc3 = subprocess.Popen(cmd)
    time.sleep(15)
    yield
    cmd = f"{python} -m iinfer -m server -c stop --svname server3 --timeout 15".split(' ')
    subprocess.run(cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server2 --timeout 15".split(' ')
    subprocess.run(cmd)
    cmd = f"{python} -m iinfer -m server -c stop --svname server1 --timeout 15".split(' ')
    subprocess.run(cmd)

"""


if __name__ == "__main__":
    main()
