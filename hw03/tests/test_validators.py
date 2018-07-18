import pytest
from api import fields
from api.validators import Validator


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
        ('gender', 'bday')
    ]

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        if not any(all(fld in self.request for fld in g) for g in self.required_groups):
            self.errors.append('Missing required field from <required_fields>.')
            return False
        return True


data_invalid = [
    (
        {'email': '@'}, 
        ['Field <char> is required.']
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

@pytest.mark.parametrize('input, errors', data_invalid)
def test_invalid_input(input, errors):
    c = CheckField(input)
    assert not c.is_valid()
    assert sorted(c.errors) == sorted(errors)


data_valid = [
    {'char': '1', 'email': '@'},
    {'char': '1', 'bday': '12.12.2000', 'gender': 0},
]

@pytest.mark.parametrize('input', data_valid)
def test_valid_input(input):
    c = CheckField(input)
    assert c.is_valid()
