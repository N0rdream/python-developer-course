import requests
import json
from api import api


URL_VALID = 'http://localhost:8000/method/'
USER_TOKEN = api.get_user_token('test', 'test')
ADMIN_TOKEN = api.get_admin_token()


def test_server_is_working(api_container, redis_container):
    r = requests.post(URL_VALID, json={})
    assert r.status_code == 200


def test_score_user_with_db(api_container, redis_container):
    data = {
        "account": "test", 
        "login": "test", 
        "method": "online_score", 
        "token": USER_TOKEN, 
        "arguments": {
            "phone": '79991234567', 
            "email": '', 
            "first_name": 'q',
            "last_name": '', 
            "birthday": '11.11.1948', 
            "gender": 1
        }
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'response': {'score': 3.0}, 'code': 200}


def test_score_admin(api_container, redis_container):
    data = {
        "account": "admin", 
        "login": "admin", 
        "method": "online_score", 
        "token": ADMIN_TOKEN, 
        "arguments": {
            'first_name': 'foo', 
            'last_name': 'bar', 
            'email': '', 
            'gender': ''
        }
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 200, 'response': {'score': 42}}


def test_invalid_request(api_container, redis_container):
    data = {
        "account": "admin", 
        "login": "admin", 
        "token": ADMIN_TOKEN, 
        "arguments": {}
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 422, 'error': 'Field <method> is required.'}


def test_invalid_auth(api_container, redis_container):
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': 'invalid_token',
        'method': 'online_score',
        'arguments': {}
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 403, 'error': 'Forbidden'}


def test_invalid_method(api_container, redis_container):
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': USER_TOKEN,
        'method': 'foo',
        'arguments': {}
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 422, 'error': 'Invalid Request'}


def test_clients_interests_are_not_defined(api_container, redis_container):
    data = {
        'account': 'test',
        'login': 'test', 
        'token': USER_TOKEN,
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2], 
            'date': '11.11.1111'
        }
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 200, 'response': {'1': [], '2': []}}


def test_clients_interests_are_defined(api_container, redis_client, redis_container):
    redis_client['i:1'] = json.dumps(['foo', 'bar'])
    redis_client['i:2'] = json.dumps(['baz', 'cats'])
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': USER_TOKEN,
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2], 
            'date': '11.11.1111'
        }
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 200, 'response': {'1': ['foo', 'bar'], '2': ['baz', 'cats']}}
