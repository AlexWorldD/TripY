FROM python:3.5
ADD requirements.txt /app/requirements.txt
ADD ./TripY/ /app/
WORKDIR /app/
RUN pip install -r requirements.txt
ENTRYPOINT celery worker -l info -A TripY.celery -Q hotel,restaurant,attraction --concurrency=10