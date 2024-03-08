# Stock API

The Stock API application allows users to monitor stock prices from NASDAQ index.
The task is to create a project setup with django, drf and postgress database.

## Setup

- Prepare Python venv
- Install packages form requirements.t
- Build database of choice
- Make .env (example.env <- example file)

## Run app

To run the application execute command:

```
python manage.py runserver
```

## Celery and WS

- Run broker RabbitMQ (example with docker) and Reddis for channel layers

```sh
docker run -d -p 5672:5672 rabbitmq
docker run -p 6379:6379 redis:7 
```

- Run Celery worker and beat

```sh
celery -A stockProject worker -l info
```

```sh
celery -A stockProject beat -l info
```

- Run Flower monitor

```sh
celery --broker=amqp://guest:guest@localhost:5672// flower
```