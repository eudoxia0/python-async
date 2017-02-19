FROM ubuntu:16.10

RUN apt-get update && apt-get -y install --no-upgrade libpq-dev python3 \
    python3-pip

ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3 --version

CMD ["python3", "app.py"]
