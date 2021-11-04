upstream api {
    server ${APP_HOST}:${APP_PORT};
}

server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              api;
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    100M;
    }
}

