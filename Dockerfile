FROM python:3.6.13-slim-buster
RUN pip install --upgrade pip
RUN mkdir -p /app

COPY . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

CMD ["python", "pilot.py"]
