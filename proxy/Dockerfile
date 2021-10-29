FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="olorunshola matins"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    chmod -R 755 /vol && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh
    # chown -R app:app /vol && \
    # RUN chmod -R 755 /vol/web && \
    # RUN chmod -R 755 /app && \
    # chmod -R 755 /vol && \
    # # chmod -R +x /scripts 
    # chmod +x /scripts/*

VOLUME /vol/static

USER nginx

CMD ["/run.sh"]
