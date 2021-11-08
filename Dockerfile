FROM public.ecr.aws/lambda/python:3.8

# Copy function code
WORKDIR ${LAMBDA_TASK_ROOT}
COPY app/app.py .

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target .

# CMD value overrided by terraform
CMD [ "app.lambda_handler" ] 