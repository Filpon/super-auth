FROM quay.io/keycloak/keycloak:26.3.0
COPY realm-config-initial.json /tmp/import/realm-config-initial.json
COPY import-realm.sh /tmp/import/import-realm.sh
COPY new-client-initial.json /tmp/import/new-client-initial.json
COPY new-user-initial.json /tmp/import/new-user-initial.json
COPY sub-token.json /tmp/import/sub-token.json
ENTRYPOINT ["/tmp/import/import-realm.sh"]
