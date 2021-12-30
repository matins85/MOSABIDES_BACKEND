upstream api {
    server ${APP_HOST}:${APP_PORT};
}

server {
    listen ${LISTEN_PORT};
    charset     utf-8;
    client_max_body_size    100M;

    location /static {
        alias /vol/static;
    }

    location /media {
        alias /vol/media;
    }

    location / {
        uwsgi_pass              api;
        include                 /etc/nginx/uwsgi_params;
    }
}

