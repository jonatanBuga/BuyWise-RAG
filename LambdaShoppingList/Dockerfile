#Use the aws base image for python 
FROM public.ecr.aws/lambda/python:3.12

RUN microdnf update -y && microdnf install -y gcc-c++ make

#copy requirements.txt 
COPY requirements.txt ${LAMBDA_TASK_ROOT}

#Install the specified packages
RUN pip install -r requirements.txt

#Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy the additional modules (directories)
COPY pdf_parser ${LAMBDA_TASK_ROOT}/pdf_parser
COPY OCR ${LAMBDA_TASK_ROOT}/OCR

# Copy .env file
COPY .env ${LAMBDA_TASK_ROOT}/.env

#set the premissions to make the file executable
RUN chmod +x lambda_function.py

#set the CMD to your handler
CMD ["lambda_function.lambda_handler"]