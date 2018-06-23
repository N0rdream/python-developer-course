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

    @property
    def required_fields(self):
        return [k for k, v in self._fields.items() if v.required]

    @property
    def non_nullable_fields(self):
        return [k for k, v in self._fields.items() if not v.nullable]

    def is_field_empty(self, field, value):
        return value in self._fields[field].empty_values

    def get_non_nullable_fields(self, request_body):
        return [k for k, v in request_body.items() if k in self._fields and not self.is_field_empty(k, v)]

    def check_required_fields(self, request_body):
        for field in self.required_fields:
            if field not in request_body:
                raise AttributeError(f'Field <{field}> is required.')

    def check_non_nullable_fields(self, request_body):
        for field in self.non_nullable_fields:
            if field in request_body:
                if self.is_field_empty(field, request_body[field]):
                    raise AttributeError(f'Field <{field}> is non-nullable.')

    def check_for_excess_fields(self, request_body):
        for field in request_body:
            if field not in self._fields:
                raise AttributeError(
                    f'Field <{field}> is not defined in <{self.__class__.__name__}>.')

    def check_required_groups(self, request_body):
        for sublist in self.required_groups:
            flag = True
            for field in sublist:
                if field not in self._fields:
                    raise AttributeError(
                        f'Unknown field <{field}> in <required_fields>.')
                if field not in request_body or self.is_field_empty(field, request_body[field]):
                    flag = False
            if flag:
                return None
        raise AttributeError('Missing required field from <required_fields>.')

    def is_valid(self, request_body):
        try:
            if hasattr(self, 'required_groups'):
                self.check_required_groups(request_body)
            else:
                self.check_required_fields(request_body)
            self.check_non_nullable_fields(request_body)
            self.check_for_excess_fields(request_body)
        except (ValueError, AttributeError) as e:
            self.error = str(e)
            return False
        for k, v in request_body.items():
            try:
                setattr(self, k, v)
            except TypeError as e:
                self.error = f'Error in <{k}> field. {e}'
                return False
        return True
