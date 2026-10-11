#!/bin/bash
# Creates one login role and one database per app. Runs once, on the first boot
# of an empty data volume (see README.md to add an app later).
set -euo pipefail

create_app() {
    local name="$1"
    local password="$2"
    psql -v ON_ERROR_STOP=1 --username postgres --set=password="${password}" << SQL
CREATE ROLE "${name}" LOGIN PASSWORD :'password';
CREATE DATABASE "${name}" OWNER "${name}";
SQL
}

create_app prefect "${PREFECT_DB_PASSWORD}"
