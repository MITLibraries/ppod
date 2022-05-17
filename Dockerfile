FROM public.ecr.aws/lambda/python:3.9

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}/
COPY . ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip3 install pipenv
RUN pipenv requirements
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Default handler. See README for how to override to a different handler.
CMD [ "lambdas.webhook.lambda_handler" ]