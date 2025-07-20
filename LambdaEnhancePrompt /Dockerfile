# Use AWS Lambda base image for Python 3.12
FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies (only if needed)
RUN microdnf update -y && microdnf install -y gcc-c++ make

# Copy requirements and install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy .env file if needed (for local dev or extra settings)
COPY .env ${LAMBDA_TASK_ROOT}/.env

# Set the Lambda handler (module.function_name)
CMD ["lambda_function.lambda_handler"]
