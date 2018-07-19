from api import api


def test_multiple_errors(user_token):
    data = {
        'account': 42, 
        'login': 'test', 
        'token': user_token,
        'method': '',
        'arguments': {}
    }
    ctx = {}
    response, code = api.method_handler({'body': data, 'headers': {}}, ctx, None)
    assert 'Error in <account> field. Expected str.' in response
    assert 'Field <method> is non-nullable.' in response
    assert code == api.INVALID_REQUEST
    assert ctx == {}


def test_clients_interests_empty_request(request):
    request.arguments = {}
    ctx = {}
    response, code = api.handle_clients_interests(request, ctx, None)
    assert response == 'Field <client_ids> is required.'
    assert code == api.INVALID_REQUEST
    assert ctx['nclients'] == 0


def test_scoring_empty_request(request):
    request.arguments = {}
    request.is_admin = True
    ctx = {}
    response, code = api.handle_online_score(request, ctx, None)
    assert response == 'Missing required field from <required_fields>.'
    assert code == api.INVALID_REQUEST
    assert ctx['has'] == []


def test_scoring_admin(request):
    request.arguments = {
        'first_name': 'foo', 
        'last_name': 'bar'
    }
    request.is_admin = True
    ctx = {}
    response, code = api.handle_online_score(request, ctx, None)
    assert response == {'score': 42}
    assert code == api.OK
    assert sorted(ctx['has']) == ['first_name', 'last_name']


def test_invalid_request():
    ctx = {}
    response, code = api.method_handler({'main': {}, 'headers': {}}, ctx, None)
    assert response == api.ERRORS[api.INVALID_REQUEST]
    assert code == api.INVALID_REQUEST
    assert ctx == {}


def test_missing_required_fields():
    ctx = {}
    response, code = api.method_handler({'body': {}, 'headers': {}}, ctx, None)
    assert code == api.INVALID_REQUEST
    assert ctx == {}
    assert 'Field <login> is required.' in response
    assert 'Field <token> is required.' in response
    assert 'Field <arguments> is required.' in response
    assert 'Field <method> is required.' in response


def test_invalid_token():
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': 'invalid_token',
        'method': 'online_score',
        'arguments': {}
    }
    ctx = {}
    response, code = api.method_handler({'body': data, 'headers': {}}, ctx, None)
    assert response == api.ERRORS[api.FORBIDDEN]
    assert code == api.FORBIDDEN
    assert ctx == {}


def test_invalid_method(user_token):
    data = {
        'account': 'test', 
        'login': 'test', 
        'token': user_token,
        'method': 'foo',
        'arguments': {}
    }
    ctx = {}
    response, code = api.method_handler({'body': data, 'headers': {}}, ctx, None)
    assert response == api.ERRORS[api.INVALID_REQUEST]
    assert code == api.INVALID_REQUEST
    assert ctx == {}
