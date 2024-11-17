
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

