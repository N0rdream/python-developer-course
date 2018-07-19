import re
from datetime import datetime


class ValidationError(Exception):
    pass


class Field:

    def __set_name__(self, cls, name):
        self.name = name
    
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def is_empty(self, value):
        return value in self.empty_values

    def is_valid_type(self, value):
        return type(value) in self.valid_types

    def get_valid_types(self):
        return ', '.join([t.__name__ for t in self.valid_types])

    def __set__(self, instance, value):
        if not self.is_empty(value):
            if not self.is_valid_type(value):
                raise ValidationError(
                    f'Expected {self.get_valid_types()}.')
            if hasattr(self, 'is_valid'):
                self.is_valid(value)
        instance.__dict__[self.name] = value


class CharField(Field):
    empty_values = ('',)
    valid_types = (str,)


class EmailField(CharField):
    def is_valid(self, value):
        if value:
            if '@' not in value:
                raise ValidationError('Expected <@> in email.')


class ArgumentsField(Field):
    empty_values = ('', {})
    valid_types = (dict,)


class PhoneField(Field):
    empty_values = ('',)
    valid_types = (str, int)

    def is_valid(self, value):
        if value:
            pattern = re.compile(r'^7\d{10}$')
            match = pattern.search(str(value))
            if match is None:
                raise ValidationError('Expected 7YYYZZZZZZZ format.')


class DateField(Field):
    empty_values = ('',)
    valid_types = (str,)

    def is_valid(self, value):
        try:
            return datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValidationError('Expected DD.MM.YYYY format.')


class BirthDayField(DateField):

    def is_valid(self, value):
        dt_ext = super().is_valid(value)
        dt_now = datetime.now()
        diff_y = dt_now.year - dt_ext.year
        diff_m = dt_now.month - dt_ext.month
        diff_d = dt_now.day - dt_ext.day
        if diff_y > 70 or (diff_y == 70 and diff_m >=0 and diff_d >= 0):
            raise ValidationError('Expected age < 70.')


class GenderField(Field):
    empty_values = ('',)
    valid_types = (int,)
    
    def is_valid(self, value):
        if value and value not in [0, 1, 2]:
            raise ValidationError('Expected 0, 1 or 2.')


class ClientIDsField(Field):
    empty_values = ('', [])
    valid_types = (list,)

    def is_valid(self, value):
        for i in value:
            if not isinstance(i, int):
                raise ValidationError('Expected int clients IDs.')
