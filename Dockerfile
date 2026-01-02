FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY . .
RUN pip install flask psycopg2-binary boto3
EXPOSE 80
CMD ["python", "app.py"]
