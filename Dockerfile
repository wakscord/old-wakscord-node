FROM python:3.11.2-slim AS builder

ENV OBJECT_MODE 64
RUN apt-get update && apt-get install gcc make -y --no-install-recommends && python3 -m pip install -U setuptools pip

COPY ./requirements.txt /tmp/requirements.txt

RUN python3 -m pip install --user -r /tmp/requirements.txt

FROM python:3.11.2-slim

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

COPY . .

ENTRYPOINT ["python3", "-m", "node"]