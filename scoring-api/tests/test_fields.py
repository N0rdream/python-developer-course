import pytest
from api import fields
from api.fields import ValidationError


@pytest.fixture
def cls():
    class HelperClass:
        pass
    return HelperClass


@pytest.fixture
def cls_instance(cls):
    return cls()


@pytest.mark.parametrize('value, error_message', [
    (1, 'Expected str.'),
    (None, 'Expected str.'),
    ([], 'Expected str.')
])
def test_charfield_fail(value, error_message, cls_instance):
    descriptor = fields.CharField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    '1', 
    '', 
    'Кириллица'
])
def test_charfield_ok(value, cls, cls_instance):
    descriptor = fields.CharField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    ({}, 'Expected str.'),
    (None, 'Expected str.'),
    ('test_gmail.com', 'Expected <@> in email.')
])
def test_emailfield_fail(value, error_message, cls_instance):
    descriptor = fields.EmailField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    '@',
    '', 
    'почта@'
])
def test_emailfield_ok(value, cls, cls_instance):
    descriptor = fields.EmailField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    (-1, 'Expected 7YYYZZZZZZZ format.'),
    (None, 'Expected str, int.'),
    (8000123467, 'Expected 7YYYZZZZZZZ format.'),
    (' 70001234567 ', 'Expected 7YYYZZZZZZZ format.'),
    ('7---1234567', 'Expected 7YYYZZZZZZZ format.'),
    ('7 000 123467', 'Expected 7YYYZZZZZZZ format.')
])
def test_phonefield_fail(value, error_message, cls_instance):
    descriptor = fields.PhoneField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message

@pytest.mark.parametrize('value', [
    '70001234567', 
    '', 
    70001234567
])
def test_phonefield_ok(value, cls, cls_instance):
    descriptor = fields.PhoneField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    (None, 'Expected str.'),
    ('01-01-1999', 'Expected DD.MM.YYYY format.'),
    ('00.00.0000', 'Expected DD.MM.YYYY format.'),
    ('01.13.2000', 'Expected DD.MM.YYYY format.'),
    (10012000, 'Expected str.')
])
def test_datefield_fail(value, error_message, cls_instance):
    descriptor = fields.DateField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    '01.01.2000', 
    ''
])
def test_datefield_ok(value, cls, cls_instance):
    descriptor = fields.DateField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    ('01.12.1940', 'Expected age < 70.'),
    (None, 'Expected str.'),
    ([], 'Expected str.'),
    ('01-01-2001', 'Expected DD.MM.YYYY format.')
])
def test_bdayfield_fail(value, error_message, cls_instance):
    descriptor = fields.BirthDayField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    '12.12.2012', 
    ''
])
def test_bdayfield_ok(value, cls, cls_instance):
    descriptor = fields.BirthDayField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    (-1, 'Expected 0, 1 or 2.'),
    (None, 'Expected int.'),
    ('0', 'Expected int.')
])
def test_genderfield_fail(value, error_message, cls_instance):
    descriptor = fields.GenderField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    0, 
    '', 
])
def test_genderfield_ok(value, cls, cls_instance):
    descriptor = fields.GenderField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    (0, 'Expected list.'),
    (['1', 2], 'Expected int clients IDs.'),
    ((), 'Expected list.')
])
def test_cidsfield_fail(value, error_message, cls_instance):
    descriptor = fields.ClientIDsField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message


@pytest.mark.parametrize('value', [
    [1, 2, 3], 
    [], 
    ''
])
def test_cidsfield_ok(value, cls, cls_instance):
    descriptor = fields.ClientIDsField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value


@pytest.mark.parametrize('value, error_message', [
    ({1}, 'Expected dict.'),
    (None, 'Expected dict.'),
    ((), 'Expected dict.'),
])
def test_argsfield_fail(value, error_message, cls_instance):
    descriptor = fields.ArgumentsField()
    with pytest.raises(ValidationError) as e:
        descriptor.__set__(cls_instance, value)
    assert str(e.value) == error_message

  
@pytest.mark.parametrize('value', [
    '', 
    {}, 
    {'q': 1}
])
def test_argsfield_ok(value, cls, cls_instance):
    descriptor = fields.ArgumentsField()
    descriptor.__set_name__(cls, 'field')
    descriptor.__set__(cls_instance, value)
    assert cls_instance.field == value
