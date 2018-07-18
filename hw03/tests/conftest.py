import docker 
import redis
import pytest
import os
from api.store import Store


@pytest.fixture(scope='session')
def docker_client():
    return docker.from_env(version='auto')


@pytest.fixture(scope='module')
def redis_container(docker_client):
    container = docker_client.containers.run(
        image='redis:3',
        detach=True,
        ports={'6379/tcp': 6379},
    )
    yield container
    container.kill(signal=9)
    container.remove(force=True)


@pytest.fixture(scope='session')
def api_container(docker_client):
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    i = docker_client.images.build(path=path, tag='otus_api', rm=True)
    container = docker_client.containers.run(
        image='otus_api',
        detach=True,
        network_mode='host'
    )
    yield container
    container.kill(signal=9)
    container.remove(force=True)


@pytest.fixture
def redis_client(redis_container):
    client = redis.StrictRedis(
        host='127.0.0.1',
        port=6379,
        db=0, 
        decode_responses=True
    )
    yield client
    client.flushdb()


@pytest.fixture
def store_client_with_db(redis_container):
    return Store('127.0.0.1', 6379)
    

@pytest.fixture
def store_client_without_db():
    return Store('bad_address', 777)
