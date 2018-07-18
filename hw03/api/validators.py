from .fields import Field, ValidationError


class ValidatorMeta(type):
    
    def __new__(meta, clsname, bases, clsdict):
        fields = {k: v for k, v in clsdict.items() if isinstance(v, Field)}
        clsdict['_fields'] = fields or {}
        return super().__new__(meta, clsname, bases, clsdict)


class Validator(metaclass=ValidatorMeta):

    def __init__(self, request):
        self.errors = []
        self.request = request

    def is_field_empty(self, field, value):
        return value in self._fields[field].empty_values

    @property
    def errors_string(self):
        return ' '.join(self.errors)

    def is_valid(self):
        for f, fv in self._fields.items():
            if f not in self.request and fv.required:
                self.errors.append(f'Field <{f}> is required.')
            if f in self.request and self.is_field_empty(f, self.request[f]) and not fv.nullable:
                self.errors.append(f'Field <{f}> is non-nullable.')           
        for rf, rfv in self.request.items():
            try:
                setattr(self, rf, rfv)
            except ValidationError as e:
                self.errors.append(f'Error in <{rf}> field. {e}')
        return not self.errors
