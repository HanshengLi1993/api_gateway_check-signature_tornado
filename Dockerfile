FROM python:3-slim

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

RUN mkdir /api_gateway_check_signature_tornado
RUN mkdir /var/log/api_gateway_check_signature_tornado
COPY src  /api_gateway_check_signature_tornado/src


WORKDIR /api_gateway_check_signature_tornado/src/main
CMD python Main.py --port=8080