"""
result:         boolean, indicates success/fail of request
code:           mainly 2 cases: 
                    - success: 200
                    - fail: 500
message:        detail description (if applicable)
data:           json object to store response data
"""
from flask import Response, jsonify
def response_template(result, code, message, data):
    response_body = {
        'result': result,
        'code': code,
        'message': message,
        'data': data,
    }
    response = jsonify(response_body)
    return response