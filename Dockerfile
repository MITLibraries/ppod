FROM public.ecr.aws/lambda/python:3.9

# Copy function code
COPY lambdas ${LAMBDA_TASK_ROOT}/lambdas
COPY lambdas ${LAMBDA_TASK_ROOT}/lambdas

# Install dependencies
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Default handler. See README for how to override to a different handler.
CMD [ "lambdas.webhook.lambda_handler" ]