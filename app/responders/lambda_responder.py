from dataclasses import dataclass, asdict
import json


@dataclass
class LambdaResponse:
    body: str
    statusCode: int
    isBase64Encoded: bool = False


class LambdaResponder:
    def return_success_response(self, body):
        response_body = json.dumps(body, default=str)
        return asdict(LambdaResponse(response_body, 200))

    def return_internal_server_error_response(self, error: str):
        return asdict(LambdaResponse(json.dumps({"error": error}), 500))

    def return_not_found_response(self, error: str):
        return asdict(LambdaResponse(json.dumps({"error": error}), 404))

    def return_invalid_request_response(self, error: str):
        return asdict(LambdaResponse(json.dumps({"error": error}), 400))

    def return_unauthenticated_response(self):
        return asdict(LambdaResponse(json.dumps({"error": "Unauthenticated"}), 403))
