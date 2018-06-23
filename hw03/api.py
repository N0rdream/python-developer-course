import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from validators import Validator
import fields
from scoring import get_score, get_interests
from collections import namedtuple


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
    first_name = fields.CharField(required=True, nullable=True)
    last_name = fields.CharField(required=False, nullable=True)
    email = fields.EmailField(required=False, nullable=True)
    phone = fields.PhoneField(required=False, nullable=True)
    birthday = fields.BirthDayField(required=False, nullable=True)
    gender = fields.GenderField(required=False, nullable=True)

    required_groups = [
        ('phone', 'email'), 
        ('first_name', 'last_name'),
        ('gender', 'birthday'),
    ]


class MethodRequest(Validator):
    account = fields.CharField(required=False, nullable=True)
    login = fields.CharField(required=True, nullable=True)
    token = fields.CharField(required=True, nullable=True)
    arguments = fields.ArgumentsField(required=True, nullable=True)
    method = fields.CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.login == ADMIN_LOGIN:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode()).hexdigest()
    if digest == request.token:
        return True
    return False


def handle_online_score(data, is_admin):
    s = OnlineScoreRequest()
    Result = namedtuple('Result', ['response', 'code', 'ctx_val'])
    if not s.is_valid(data):
        return Result(response=s.error, code=INVALID_REQUEST, ctx_val=[])
    ctx_val = s.get_non_nullable_fields(data)
    if is_admin:
        return Result(response={'score': 42}, code=OK, ctx_val=ctx_val)
    score = get_score(
        None, s.phone, s.email, 
        birthday=s.birthday, gender=s.gender, 
        first_name=s.first_name, last_name=s.last_name
    )
    return Result(response={'score': score}, code=OK, ctx_val=ctx_val)


def handle_clients_interests(data):
    i = ClientsInterestsRequest()
    Result = namedtuple('Result', ['response', 'code', 'ctx_val'])
    if not i.is_valid(data):
        return Result(response=i.error, code=INVALID_REQUEST, ctx_val=0)
    interests = {ci: get_interests(None, ci) for ci in i.client_ids}
    return Result(response=interests, code=OK, ctx_val=len(i.client_ids))


def method_handler(request, ctx, store):
    try:
        data = request['body']
    except KeyError:
        return ERRORS[BAD_REQUEST], BAD_REQUEST
    m = MethodRequest()
    if not m.is_valid(data):
        return m.error, INVALID_REQUEST
    if not check_auth(m):
        return ERRORS[FORBIDDEN], FORBIDDEN
    if m.method == 'online_score':
        result = handle_online_score(m.arguments, m.is_admin)
        ctx['has'] = result.ctx_val
        return result.response, result.code
    if m.method == 'clients_interests':
        result = handle_clients_interests(m.arguments)
        ctx['nclients'] = result.ctx_val
        return result.response, result.code
    return ERRORS[BAD_REQUEST], BAD_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

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

if __name__ == "__main__":
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
