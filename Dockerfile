FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY app/app.py ${LAMBDA_TASK_ROOT}

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "app.post_property" ]