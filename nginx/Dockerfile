FROM nginx:1.28.0

COPY ./import-envs.sh  /import-envs.sh
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./site.conf /site.conf

EXPOSE 80

ENTRYPOINT ["/bin/bash", "-c", \
    "/import-envs.sh && exec nginx -g 'daemon off;'"]
