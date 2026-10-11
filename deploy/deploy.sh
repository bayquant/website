#!/bin/bash
# Deploys one service to the droplet from the committed HEAD of this repo.
#
# Usage: deploy/deploy.sh <service> [user@host]
#
# <service> is a folder in deploy/ (website, postgres, prefect, ...). The host
# defaults to deploy@bayquant.dev. Pass deploy@DROPLET_IP instead right after
# the droplet is recreated, before DNS has caught up.
set -euo pipefail

service="${1:?usage: deploy/deploy.sh <service> [user@host]}"
host="${2:-deploy@bayquant.dev}"
app_dir="/opt/apps/${service}"
secrets_file="/opt/secrets/${service}.env"
compose_path="deploy/${service}/compose.yaml"

cd "$(git rev-parse --show-toplevel)"

if ! git cat-file -e "HEAD:${compose_path}" 2> /dev/null; then
    echo "error: ${compose_path} is not committed" >&2
    exit 1
fi

if ! git diff --quiet HEAD; then
    echo "warning: uncommitted changes are not deployed (only HEAD is)" >&2
fi

# A service that builds from this repo needs the whole tree as build context.
# Every other service only needs its own folder.
if git show "HEAD:${compose_path}" | grep -q '^[[:space:]]*build:'; then
    ship_path="."
else
    ship_path="deploy/${service}"
fi

# Replace the previous copy with the committed files. git archive runs here,
# so the droplet needs no git access to the repo.
git archive --format=tar HEAD "${ship_path}" \
    | ssh "${host}" "rm -rf ${app_dir} && mkdir -p ${app_dir} && tar -x -C ${app_dir}"

ssh "${host}" "bash -s" << REMOTE
set -euo pipefail
cd ${app_dir}

# Network shared by services that talk to each other (postgres <-> prefect)
docker network inspect backend > /dev/null 2>&1 || docker network create backend

# Secrets live outside the app dir, which is wiped on every deploy
env_flag=""
if [ -f ${secrets_file} ]; then
    env_flag="--env-file ${secrets_file}"
fi

compose() {
    docker compose \$env_flag -f ${compose_path} "\$@"
}

# --wait blocks until every service with a healthcheck reports healthy
if ! compose up -d --build --pull always --wait --wait-timeout 120; then
    echo "${service} did not become healthy; recent logs:" >&2
    compose logs --tail 30 >&2
    exit 1
fi

# Register the site with Caddy. A reload keeps the old config if the new one
# is invalid, so a bad snippet cannot take other apps down.
if [ -f deploy/${service}/${service}.caddy ]; then
    cp deploy/${service}/${service}.caddy /etc/caddy/conf.d/${service}.caddy
    sudo systemctl reload caddy
fi

echo "${service} is up"
REMOTE
