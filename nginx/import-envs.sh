#!/bin/bash

set -a

# Disabing automatic export
set +a

process_conf_file() {
  local input_conf_file="$1"
  local output_conf_file="$2"

  # Checking if conf file exists
  if [[ ! -f "$input_conf_file" ]]; then
    echo "File $input_conf_file is not found"
    exit 1
  fi

  # Output file creation
  cp "$input_conf_file" "$output_conf_file"

  # Env substitution
  for var in $(grep -o '\${[^}]*}' "$input_conf_file" | tr -d '${}'); do
    value=${!var}
    if [ -n "$value" ]; then
      sed -i "s|\${$var}|$value|g" "$output_conf_file"
    else
      echo "Warning: env $var is not found"
    fi
  done
}

INPUT_CONF_FILE="/site.conf"
OUTPUT_CONF_FILE="/etc/nginx/conf.d/default.conf"


# Process conf file
process_conf_file "$INPUT_CONF_FILE" "$OUTPUT_CONF_FILE"

echo "Envs values are substituted. Results are saved in $OUTPUT_CONF_FILE"