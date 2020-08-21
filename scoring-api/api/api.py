import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from .validators import Validator
from . import fields
from .scoring import get_score, get_interests
from collections import namedtuple
from .store import Store


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class ClientsInterestsRequest(Validator):
    client_ids = fields.ClientIDsField(required=True)
    date = fields.DateField(required=False, nullable=True)


class OnlineScoreRequest(Validator):
    first_name = fields.CharField(required=False, nullable=True)
    last_name = fields.CharField(required=False, nullable=True)
    email = fields.EmailField(required=False, nullable=True)
    phone = fields.PhoneField(required=False, nullable=True)
    birthday = fields.BirthDayField(required=False, nullable=True)
    gender = fields.GenderField(required=False, nullable=True)

    required_groups = [
        ('phone', 'email'), 
        ('first_name', 'last_name'),
        ('gender', 'birthday')
    ]

    def get_online_score_ctx(self):
        return [k for k, v in self.request.items()
                if k in self._fields and not self.is_field_empty(k, v)]

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return False
        if not any(all(fld in self.request for fld in g) for g in self.required_groups):
            self.errors.append('Missing required field from <required_fields>.')
            return False
        return True


class MethodRequest(Validator):
    account = fields.CharField(required=False, nullable=True)
    login = fields.CharField(required=True, nullable=True)
    token = fields.CharField(required=True, nullable=True)
    arguments = fields.ArgumentsField(required=True, nullable=True)
    method = fields.CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def get_admin_token():
    return hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()).hexdigest()


def get_user_token(account, login):
    return hashlib.sha512((account + login + SALT).encode()).hexdigest()


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = get_admin_token()
    else:
        digest = get_user_token(request.account, request.login)
    if digest == request.token:
        return True
    return False


def handle_online_score(request, ctx, store):
    s = OnlineScoreRequest(request.arguments)
    if not s.is_valid():
        ctx['has'] = []
        return s.errors_string, INVALID_REQUEST
    ctx['has'] = s.get_online_score_ctx()
    if request.is_admin:
        return {'score': 42}, OK
    score = get_score(
        store, s.phone, s.email, 
        birthday=s.birthday, gender=s.gender, 
        first_name=s.first_name, last_name=s.last_name
    )
    return {'score': score}, OK


def handle_clients_interests(request, ctx, store):
    i = ClientsInterestsRequest(request.arguments)
    if not i.is_valid():
        ctx['nclients'] = 0
        return i.errors_string, INVALID_REQUEST
    ctx['nclients'] = len(i.client_ids)
    return {ci: get_interests(store, ci) for ci in i.client_ids}, OK


def method_handler(request, ctx, store):
    handlers = {
        'online_score': handle_online_score,
        'clients_interests': handle_clients_interests
    }
    try:
        data = request['body']
    except KeyError:
        return ERRORS[INVALID_REQUEST], INVALID_REQUEST
    m = MethodRequest(data)
    if not m.is_valid():
        return m.errors_string, INVALID_REQUEST
    if not check_auth(m):
        return ERRORS[FORBIDDEN], FORBIDDEN
    handler = handlers.get(m.method)
    if handler is not None:
        return handler(m, ctx, store)
    return ERRORS[INVALID_REQUEST], INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store('localhost', 6379, 1, 0.5)

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


def main():
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
