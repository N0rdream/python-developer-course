import pytest
from api import fields


@pytest.fixture
def test_class():
    class CheckField:
        char = fields.CharField()
        email = fields.EmailField()
        phone = fields.PhoneField()
        bday = fields.BirthDayField()
        gender = fields.GenderField()
        ids = fields.ClientIDsField()
        date = fields.DateField()
        args = fields.ArgumentsField()
    return CheckField()


data_invalid = [
    ('char', 1),
    ('email', None),
    ('phone', []),    
    ('date', 10012000),
    ('bday', None),
    ('gender', '0'),
    ('ids', 0),
    ('args', []),
    ('email', 'test_gmail.com'),
    ('phone', -1),    
    ('phone', 8000123467),
    ('phone', ' 70001234567 '),
    ('phone', '7---1234567'),
    ('phone', '7 000 123467'),
    ('date', '01-01-1999'),
    ('date', '00.00.0000'),
    ('date', '01.13.2000'),
    ('bday', '01.12.1940'),
    ('gender', -1),
    ('ids', ['1', 2])
]

@pytest.mark.parametrize('field, value', data_invalid)
def test_invalid_input(field, value, test_class):
    with pytest.raises(fields.ValidationError):
        setattr(test_class, field, value)


data_valid = [
    ('email', 'a@b.c'),
    ('email', ''),
    ('phone', ''),
    ('phone', '70001234567'),
    ('phone', 70001234567),
    ('bday', '12.12.2012'),
    ('gender', 0),
    ('gender', ''),
    ('ids', [1, 2, 3]),
    ('ids', []),
    ('ids', ''),
    ('args', ''),
    ('args', {}),
    ('args', {'q': 1}),    
]

@pytest.mark.parametrize('field, value', data_valid)
def test_valid_input(field, value, test_class):
    assert setattr(test_class, field, value) is None
