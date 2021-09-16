FROM python:3.9-slim

MAINTAINER Wyatt Dahlenburg "wddahlenburg@gmail.com"

RUN apt update && apt install -y procps
RUN python3 -m pip install flask werkzeug

WORKDIR /app

COPY server.py /app/server.py
COPY app.py /app/app.py

RUN groupadd -g 1000 werkzeug-user && \
    useradd -r -u 1000 -g werkzeug-user werkzeug-user

USER werkzeug-user

ENTRYPOINT [ "python3" ]

CMD [ "/app/server.py" ]
