FROM python:3.10-slim

WORKDIR app/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python manage.py ru  nserver 0.0.0.0:8000