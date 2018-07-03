import pytest
import api


# Testing 'handle_online_score'

def test_handle_online_score_invalid_request():
    class Request:
        arguments = {}
        is_admin = True

    ctx = {}
    response, code = api.handle_online_score(Request, ctx)
    assert response == 'Missing required field from <required_fields>.'
    assert code == api.INVALID_REQUEST
    assert ctx['has'] == []


def test_handle_online_score_admin():
    class Request:
        arguments = {
            'first_name': 'foo', 
            'last_name': 'bar', 
            'email': '', 
            'gender': ''
        }
        is_admin = True

    ctx = {}
    response, code = api.handle_online_score(Request, ctx)
    assert response == {'score': 42}
    assert code == api.OK
    assert sorted(ctx['has']) == ['first_name', 'last_name']


def test_handle_online_score_regular():
    class Request:
        arguments = {
            'first_name': 'foo', 
            'last_name': 'bar', 
            'email': '@',
            'phone': 79991234567,
            'birthday': '11.11.1999', 
            'gender': 0
        }
        is_admin = False

    ctx = {}
    response, code = api.handle_online_score(Request, ctx)
    assert response == {'score': 3.5}
    assert code == api.OK
    assert sorted(ctx['has']) == sorted(['first_name', 'last_name', 'email', 'phone', 'birthday', 'gender'])


# Testing 'handle_clients_interests'

def test_handle_clients_interests_invalid():
    class Request:
        arguments = {}

    ctx = {}
    act_resp, act_code = api.handle_clients_interests(Request, ctx)
    assert act_resp == 'Field <client_ids> is required.'
    assert act_code == api.INVALID_REQUEST
    assert ctx['nclients'] == 0


def test_handle_clients_interests_valid():
    class Request:
        arguments = {'client_ids': [1, 2, 3], 'date': '11.11.1111'}

    ctx = {}
    act_resp, act_code = api.handle_clients_interests(Request, ctx)
    assert isinstance(act_resp, dict) and len(act_resp) == 3
    assert act_code == api.OK
    assert ctx['nclients'] == 3


# Testing 'method_handler'

def test_method_handle_invalid_request():
    data = {}
    request, ctx, store = {'main': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert act_resp == api.ERRORS[api.BAD_REQUEST]
    assert act_code == api.BAD_REQUEST
    assert ctx == {}


def test_method_handle_missing_login():
    data = {}
    request, ctx, store = {'body': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert act_code == api.INVALID_REQUEST
    assert ctx == {}
    assert 'Field <login> is required.' in act_resp
    assert 'Field <token> is required.' in act_resp
    assert 'Field <arguments> is required.' in act_resp
    assert 'Field <method> is required.' in act_resp


def test_method_handle_invalid_token():
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': 'invalid_token',
        'method': 'online_score',
        'arguments': {}
    }
    request, ctx, store = {'body': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert act_resp == api.ERRORS[api.FORBIDDEN]
    assert act_code == api.FORBIDDEN
    assert ctx == {}


def test_method_handle_invalid_method():
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': '5c202c9b350ff604985d5518f578bcfbc42828144061d83bc02252b8cb2bb52c4fd123eb0a86775123b9564f20908928d2f2fb7b80f4a72ebe59cd5f30bc95d9',
        'method': 'foo',
        'arguments': {}
    }
    request, ctx, store = {'body': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert act_resp == api.ERRORS[api.BAD_REQUEST]
    assert act_code == api.BAD_REQUEST
    assert ctx == {}


def test_method_handle_valid_online_score():
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': '5c202c9b350ff604985d5518f578bcfbc42828144061d83bc02252b8cb2bb52c4fd123eb0a86775123b9564f20908928d2f2fb7b80f4a72ebe59cd5f30bc95d9',
        'method': 'online_score',
        'arguments': {
            'first_name': 'foo', 
            'last_name': 'bar', 
            'email': '@',
            'phone': 79991234567,
            'birthday': '11.11.1999', 
            'gender': 1
        }
    }
    request, ctx, store = {'body': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert act_resp == {'score': 5.0}
    assert act_code == api.OK
    assert isinstance(ctx['has'], list) and len(ctx['has']) == 6


def test_method_handle_valid_clients_interests():
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': '5c202c9b350ff604985d5518f578bcfbc42828144061d83bc02252b8cb2bb52c4fd123eb0a86775123b9564f20908928d2f2fb7b80f4a72ebe59cd5f30bc95d9',
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2, 3, 4], 
            'date': '11.11.1111'
        }
    }
    request, ctx, store = {'body': data, 'headers': {}}, {}, None
    act_resp, act_code = api.method_handler(request, ctx, store)
    assert isinstance(act_resp, dict) and len(act_resp) == 4
    assert act_code == api.OK
    assert ctx['nclients'] == 4


# admin method handler













