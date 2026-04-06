FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
RUN mkdir -p ./certs
COPY certs ./certs

EXPOSE 8080 8443

CMD ["python", "app.py"]
