#!/bin/bash

set -a

# Disabing automatic export
set +a

process_json_file() {
  local json_file="$1"
  local output_file="$2"

  # Checking if JSON file exists
  if [[ ! -f "$json_file" ]]; then
    echo "File $json_file is not found"
    exit 1
  fi

  # Output file creation
  cp "$json_file" "$output_file"

  # Env substitution
  for var in $(grep -o '\${[^}]*}' "$json_file" | tr -d '${}'); do
    value=${!var}
    if [ -n "$value" ]; then
      sed -i "s|\${$var}|$value|g" "$output_file"
    else
      echo "Warning: env $var is not found"
    fi
  done
}

# Defining JSON files and output file
JSON_FILE_CLIENT="/tmp/import/new-client-initial.json"
OUTPUT_FILE_CLIENT="/tmp/import/new-client.json"

JSON_FILE_USER="/tmp/import/new-user-initial.json"
OUTPUT_FILE_USER="/tmp/import/new-user.json"

# Process both JSON files
process_json_file "$JSON_FILE_CLIENT" "$OUTPUT_FILE_CLIENT"
process_json_file "$JSON_FILE_USER" "$OUTPUT_FILE_USER"

echo "Envs values are substituted. Results are saved in $OUTPUT_FILE_CLIENT and $OUTPUT_FILE_USER"

sleep 3
echo $KC_REALM_NAME
echo $KC_REALM_COMMON
echo $KEYCLOAK_ADMIN
echo $KEYCLOAK_ADMIN_PASSWORD
echo $KC_REALM_COMMON_USER
echo $KC_REALM_COMMON_USER_PASSWORD

# Variables
KEYCLOAK_URL="http://localhost:8080"  # Adjust if necessary

echo "Starting the script..."

/opt/keycloak/bin/kc.sh start-dev &

sleep 25

echo "25 seconds have passed."

# Log in to Keycloak
/opt/keycloak/bin/kcadm.sh config credentials --server $KEYCLOAK_URL --realm $KC_REALM_NAME --user $KEYCLOAK_ADMIN --password $KEYCLOAK_ADMIN_PASSWORD

sleep 5

echo "Keycloak started and Admin CLI configured."

# Client creation
if /opt/keycloak/bin/kcadm.sh get clients -r "$KC_REALM_NAME" | grep -q "\"clientId\": \"$KC_REALM_COMMON_CLIENT\""; then
  echo "Client $KC_REALM_COMMON_CLIENT exists in realm $KC_REALM_NAME"
else
  echo "Client $KC_REALM_COMMON_CLIENT does not exist in realm $KC_REALM_NAME"
  # Client creation from file
  /opt/keycloak/bin/kcadm.sh create clients -r "$KC_REALM_NAME" -f $OUTPUT_FILE_CLIENT
  echo "Client $KC_REALM_COMMON_CLIENT was created in realm $KC_REALM_NAME"
fi

# User сreation
if /opt/keycloak/bin/kcadm.sh get users -r "$KC_REALM_NAME" | grep -q "\"username\": \"$KC_REALM_COMMON_USER\""; then
  echo "User $KC_REALM_COMMON_USER exists in realm $KC_REALM_NAME"
else
  echo "User $KC_REALM_COMMON_USER does not exist in realm $KC_REALM_NAME"
  # User сreation from file
  /opt/keycloak/bin/kcadm.sh create users -r "$KC_REALM_NAME" -f $OUTPUT_FILE_USER
  echo "User $KC_REALM_COMMON_USER was created in realm $KC_REALM_NAME"
  /opt/keycloak/bin/kcadm.sh add-roles -r "$KC_REALM_NAME" --uusername "$KC_REALM_COMMON_USER" --rolename admin
  echo "Roles were included for user $KC_REALM_COMMON_USER"
fi

wait
