FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY /app ${LAMBDA_TASK_ROOT}

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

ENV PYTHONPATH "${LAMBDA_TASK_ROOT}"

WORKDIR "${LAMBDA_TASK_ROOT}"
CMD [ "app.get_properties" ]