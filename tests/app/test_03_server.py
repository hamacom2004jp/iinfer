from iinfer.app import common
from iinfer.app import redis
from iinfer.app import server
from pathlib import Path
import os
import time
import threading

wsl_name = 'Ubuntu_docker-20.04'
wsl_user = 'ubuntu'
HOME_DIR = os.path.expanduser("~")
data = Path(HOME_DIR) / ".iinfer"

def _test_01_start_stop():
    logger, _ = common.load_config('reids')
    rd = redis.Redis(logger=logger, wsl_name=wsl_name, wsl_user=wsl_user)
    ret = rd.docker_run(6379, 'password')
    sv = server.Server(Path(data), logger, redis_host='localhost', redis_port=6379, redis_password='password')
    threading.Thread(target=sv.start_server).start()
    time.sleep(10)
    sv.is_running = False
