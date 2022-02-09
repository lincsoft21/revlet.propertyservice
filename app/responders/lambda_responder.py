from dataclasses import dataclass
import json


@dataclass
class LambdaResponse:
    body: str
    statusCode: int
    isBase64Encoded: bool = False


class LambdaResponder:
    def return_success_response(self, body: str):
        response_body = body

        # If body is not a string, convert json body
        if not type(body) == type(str):
            response_body = json.dumps(body, default=str)

        return LambdaResponse(response_body, 200)

    def return_internal_server_error_response(self, error):
        return LambdaResponse(error, 500)

    def return_not_found_response(self, error):
        return LambdaResponse(error, 404)

    def return_invalid_request_response(self, error):
        return LambdaResponse(error, 400)
