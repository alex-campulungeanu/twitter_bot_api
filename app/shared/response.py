import json
from http import HTTPStatus

from flask import Response, jsonify

def response_success(msg, code=HTTPStatus.OK):
    return jsonify({'status': True, 'msg': msg, 'status_code': code}), code

def response_fail(msg, code=HTTPStatus.BAD_REQUEST):
    return jsonify({'status': False, 'msg': msg, 'status_code': code}), code

def response_data(data, code=HTTPStatus.OK):
    # print(jsonify(data))
    return Response(json.dumps(data), mimetype="application/json", status=200)