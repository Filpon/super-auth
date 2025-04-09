FROM python:3.12.7
RUN python realm.py
RUN echo "Waiting for 10 seconds..." && sleep 10
FROM quay.io/keycloak/keycloak:latest
COPY realm-mod.json /tmp/import/realm-mod.json
COPY import-realm.sh /tmp/import/import-realm.sh
