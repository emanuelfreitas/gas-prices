FROM python:slim

LABEL maintainer="Emanuel Freitas <emanuelfreitas@outlook.com>"

RUN pip install --no-cache-dir flask prometheus_client

COPY src /

ENTRYPOINT ["python", "-m", "flask run"]

EXPOSE 5000/tcp