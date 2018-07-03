from fields import Field


class ValidatorMeta(type):
    
    def __new__(meta, clsname, bases, clsdict):
        fields = {k: v for k, v in clsdict.items() if isinstance(v, Field)}
        if fields:
            clsdict['_fields'] = fields
        else:
            clsdict['_fields'] = {}
        return super().__new__(meta, clsname, bases, clsdict)


class Validator(metaclass=ValidatorMeta):

    def __init__(self, request):
        self.errors = []
        self.request = request

    def is_field_empty(self, field, value):
        return value in self._fields[field].empty_values

    def get_online_score_ctx(self):
        return [k for k, v in self.request.items()
                if k in self._fields and not self.is_field_empty(k, v)]

    @property
    def errors_string(self):
        return ' '.join(self.errors)

    def is_valid(self):
        if hasattr(self, 'required_groups'):
            if not any(all(f in self.request for f in g) for g in self.required_groups):
                self.errors.append('Missing required field from <required_fields>.')
        else:
            for f, fv in self._fields.items():
                if f not in self.request and fv.required:
                    self.errors.append(f'Field <{f}> is required.')
        for f, fv in self._fields.items():
            if f in self.request and self.is_field_empty(f, self.request[f]) and not fv.nullable:
                self.errors.append(f'Field <{f}> is non-nullable.')
        for rf, rfv in self.request.items():
            try:
                setattr(self, rf, rfv)
            except (TypeError, ValueError) as e:
                self.errors.append(f'Error in <{rf}> field. {e}')
        return not self.errors
