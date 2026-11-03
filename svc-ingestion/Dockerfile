FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt

COPY app ./app
COPY test_data ./test_data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
