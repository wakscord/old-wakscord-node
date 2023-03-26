FROM python:3.11.2-slim

ENV OBJECT_MODE 64
RUN apt-get update && apt-get upgrade -y && apt-get install gcc make -y
RUN pip install -U setuptools pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python", "-m", "node"]