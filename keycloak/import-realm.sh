#!/bin/bash

set -a

# Disable automatic export
set +a

sleep 5
echo $KC_REALM_NAME
echo $KC_REALM_COMMON
echo $KEYCLOAK_ADMIN
echo $KEYCLOAK_ADMIN_PASSWORD
sleep 3

# Variables
REALM_JSON_FILE="/tmp/import/realm-mod.json"  # Adjust the path as necessary /tmp/import/realm-mod.json
KEYCLOAK_URL="http://localhost:8080"  # Adjust if necessary

echo "Starting the script..."

/opt/keycloak/bin/kc.sh start-dev &

sleep 20

echo "20 seconds have passed."

# Log in to Keycloak
/opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm $KC_REALM_NAME --user $KEYCLOAK_ADMIN --password $KEYCLOAK_ADMIN_PASSWORD

sleep 3

echo "Keycloak started and Admin CLI configured."

# Check if the realm exists
if /opt/keycloak/bin/kcadm.sh get realms/$KC_REALM_COMMON > /dev/null 2>&1; then
    echo "Realm '$KC_REALM_COMMON' already exists. Skipping import."
else
    echo "Realm '$KC_REALM_COMMON' does not exist. Importing..."
    /opt/keycloak/bin/kcadm.sh create realms -f $REALM_JSON_FILE
    echo "Realm '$KC_REALM_COMMON' imported successfully."
fi

wait
