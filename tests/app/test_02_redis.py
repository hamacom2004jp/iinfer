from iinfer.app import common
from iinfer.app import redis


wsl_name = 'Ubuntu_docker-20.04'
wsl_user = 'ubuntu'

def _test_01_docker_run():
    logger, _ = common.load_config('reids')
    rd = redis.Redis(logger=logger, wsl_name=wsl_name, wsl_user=wsl_user)
    ret = rd.docker_run(6379, 'password')
    assert ret['output'] == 0

def _test_02_docker_stop():
    logger, _ = common.load_config('reids')
    rd = redis.Redis(logger=logger, wsl_name=wsl_name, wsl_user=wsl_user)
    ret = rd.docker_stop()
    #assert ret['output'] == 0
