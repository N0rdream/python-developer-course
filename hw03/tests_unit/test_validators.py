import pytest
import fields
from validators import Validator


class CheckField(Validator):
    char = fields.CharField(required=True, nullable=True)
    email = fields.EmailField(required=False, nullable=False)
    phone = fields.PhoneField()
    bday = fields.BirthDayField()
    gender = fields.GenderField()
    ids = fields.ClientIDsField()
    date = fields.DateField()
    args = fields.ArgumentsField()

    required_groups = [
        ('char', 'email'), 
        ('gender', 'bday'),
    ]


data_invalid = [
    (
        {'email': '@'}, 
        ['Missing required field from <required_fields>.']
    ),
    (
        {'char': '1', 'email': ''}, 
        ['Field <email> is non-nullable.']
    ), (
        {'char': 1, 'email': '@'}, 
        ['Error in <char> field. Expected str.']
    ), (
        {'char': '1', 'email': 1}, 
        ['Error in <email> field. Expected str.']
    ), (
        {'char': '1', 'email': 'foo'}, 
        ['Error in <email> field. Expected <@> in email.']
    ), (
        {'char': '1'}, 
        ['Missing required field from <required_fields>.']
    ), (
        {'char': '1', 'gender': 0}, 
        ['Missing required field from <required_fields>.']
    ), (
        {'char': '1', 'gender': 2, 'bday': ''}, 
        ['Field <bday> is non-nullable.', 'Error in <bday> field. Expected DD.MM.YYYY format.']
    ), (
        {'char': '1', 'gender': -1, 'bday': -1}, 
        ['Error in <gender> field. Expected 0, 1 or 2.', 'Error in <bday> field. Expected str.']
    ),
]

@pytest.fixture(params=data_invalid)
def data_invalid_param(request):
    return request.param

def test_is_invalid(data_invalid_param):
    data, errors = data_invalid_param
    c = CheckField(data)
    assert not c.is_valid()
    assert sorted(c.errors) == sorted(errors)


data_valid = [
    {'char': '1', 'email': '@'},
    {'char': '1', 'bday': '12.12.2000', 'gender': 0},
]

@pytest.fixture(params=data_valid)
def data_valid_param(request):
    return request.param

def test_is_valid(data_valid_param):
    c = CheckField(data_valid_param)
    assert c.is_valid()

















