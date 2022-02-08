from dataclasses import dataclass

@dataclass
class LambdaResponse:
  Body: str
  StatusCode: int


class LambdaResponder:
    def GetSuccessResponse(self):
        pass

    def GetInternalServerErrorResponse(self, error):
        pass
