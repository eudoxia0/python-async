FROM ubuntu:16.10

RUN apt-get update
RUN apt-get -y install --no-upgrade libpq-dev python3.6 python3-pip python3.6-dev

ADD . /app
WORKDIR /app

RUN python3.6 -m pip install -r requirements.txt

CMD ["python3.6", "app.py"]
