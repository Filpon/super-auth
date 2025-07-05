FROM quay.io/keycloak/keycloak:latest
COPY import-realm.sh /tmp/import/import-realm.sh
COPY new-client-initial.json /tmp/import/new-client-initial.json
COPY new-user-initial.json /tmp/import/new-user-initial.json
ENTRYPOINT ["bash", "/tmp/import/import-realm.sh"]
