
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


@pytest.mark.run(order=0)
def test_0_install_insightface_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "insightface",
           "--install_use_gpu",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=1)
def test_1_install_mmdet_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "mmdet",
           "--install_use_gpu",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=2)
def test_2_install_mmpretrain_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "mmpretrain",
           "--install_use_gpu",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=3)
def test_3_install_mmseg_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "mmseg",
           "--install_use_gpu",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=4)
def test_4_install_redis_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "redis",
           "--wsl_name",
           "Ubuntu_docker-22.04",
           "--wsl_user",
           "ubuntu",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' in result.keys()


@pytest.mark.run(order=5)
def test_5_install_server_win(capfd):
    cmd = ["-m",
           "install",
           "-c",
           "server",
           "--install_iinfer",
           "iinfer",
           "--debug"]

    _, result = app.IinferApp().main(args_list=cmd)
    out, err = capfd.readouterr()
    print(out)
    assert 'success' not in result.keys()

