
FROM python:3.9-alpine3.13
LABEL maintainer="olorunshola matins"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app
COPY ./scripts /scripts


WORKDIR /app
EXPOSE 3000

ENV USER=app
ENV UID=12345
ENV GID=23456

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev libffi-dev \
     libressl-dev zlib zlib-dev && \
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home app && \
    # RUN adduser \
    # --disabled-password \
    # --gecos "" \
    # --ingroup "$USER" \
    # --no-create-home \
    # --uid "$UID" \
    # "$USER" && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /app && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

USER app

ENV PATH="/scripts:/py/bin:$PATH"

CMD ["run.sh"]
