from dataclasses import dataclass

@dataclass
class LambdaResponse:
  Body: str
  StatusCode: int


class LambdaResponder:
    def SuccessResponse(self):
        pass

    def InternalServerErrorResponse(self, error):
        pass

    def InvalidResponse(self):
      pass