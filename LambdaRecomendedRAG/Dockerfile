FROM public.ecr.aws/lambda/python:3.12

RUN microdnf update -y && microdnf install -y gcc-c++ make

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

# copy all files, including data folder
COPY . ${LAMBDA_TASK_ROOT}

RUN chmod +x lambda_function.py

CMD ["lambda_function.lambda_handler"]