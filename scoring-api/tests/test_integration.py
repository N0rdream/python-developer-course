import pytest
import json
import redis
import time
from api import api
from api.scoring import generate_key


@pytest.fixture
def request_score(request):
    request.arguments = {
        'first_name': 'foo', 
        'last_name': 'bar', 
        'email': '@',
        'phone': 79991234567,
        'birthday': '11.11.1999', 
        'gender': 0
    }
    request.is_admin = False
    return request


def test_scoring_and_caching(store_client_with_db, redis_client, request_score):
    response, code = api.handle_online_score(request_score, {}, store_client_with_db)
    key = generate_key(
        request_score.arguments['first_name'],
        request_score.arguments['last_name'],
        request_score.arguments['birthday']
    )
    assert json.loads(redis_client[key])['score'] == 3.5
    assert response == {'score': 3.5}
    assert code == api.OK


def test_scoring_without_storage(store_client_without_db, request_score):
    ctx = {}
    response, code = api.handle_online_score(request_score, ctx, store_client_without_db)
    assert response == {'score': 3.5}
    assert code == api.OK
    assert sorted(ctx['has']) == sorted(['first_name', 'last_name', 'email', 'phone', 'birthday', 'gender'])


@pytest.fixture
def request_interests(request):
    request.arguments = {'client_ids': [1, 2], 'date': '11.11.1111'}
    return request


def test_clients_interests_ok(store_client_with_db, redis_client, request_interests):
    redis_client['i:1'] = json.dumps(['foo', 'bar'])
    redis_client['i:2'] = json.dumps(['baz', 'cats'])
    ctx = {}
    response, code = api.handle_clients_interests(request_interests, ctx, store_client_with_db)
    assert code == api.OK
    assert response == {1: ['foo', 'bar'], 2: ['baz', 'cats']}
    assert ctx['nclients'] == 2


def test_clients_interests_are_not_defined(store_client_with_db, request_interests):
    ctx = {}
    response, code = api.handle_clients_interests(request_interests, ctx, store_client_with_db)
    assert code == api.OK
    assert response == {1: [], 2: []}
    assert ctx['nclients'] == 2

   
def test_clients_interests_without_db(store_client_without_db, request_interests):
    with pytest.raises(redis.exceptions.ConnectionError):
        response, code = api.handle_clients_interests(request_interests, {}, store_client_without_db)


def test_cache_expiration(store_client_with_db, redis_client):
    store_client_with_db.cache_set('foo', 42, cache_valid=2)
    assert json.loads(redis_client['foo'])['score'] == 42
    assert store_client_with_db.cache_get('foo') == 42
    time.sleep(2)
    assert json.loads(redis_client['foo'])['score'] == 42
    assert store_client_with_db.cache_get('foo') == 0
