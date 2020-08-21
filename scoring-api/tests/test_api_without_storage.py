import requests
from api import api


URL_VALID = 'http://localhost:8000/method/'


def test_score_user_without_db(api_container, user_token):
    data = {
        "account": "test", 
        "login": "test", 
        "method": "online_score", 
        "token": user_token, 
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


def test_clients_interests_without_db(api_container, user_token):
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': user_token,
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2], 
            'date': '11.11.1111'
        }
    }
    r = requests.post(URL_VALID, json=data).json()
    assert r == {'code': 500, 'error': 'Internal Server Error'}
