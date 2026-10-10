#!/bin/bash
# Deploys the committed HEAD of this repo to the droplet.
#
# Usage: deploy/deploy.sh [user@host]
#
# The host defaults to deploy@bayquant.dev. Pass deploy@DROPLET_IP instead
# right after the droplet is recreated, before DNS has caught up.
set -euo pipefail

app=website
port=8000
host="${1:-deploy@bayquant.dev}"
app_dir="/opt/apps/${app}"

cd "$(git rev-parse --show-toplevel)"

if ! git diff --quiet HEAD; then
    echo "warning: uncommitted changes are not deployed (only HEAD is)" >&2
fi

# Replace the previous copy with the committed files. git archive runs here,
# so the droplet needs no git access to the repo.
git archive --format=tar HEAD \
    | ssh "${host}" "rm -rf ${app_dir} && mkdir -p ${app_dir} && tar -x -C ${app_dir}"

ssh "${host}" "bash -s" << REMOTE
set -euo pipefail
cd ${app_dir}

docker compose -f deploy/compose.yaml up -d --build

# Register the site with Caddy. A reload keeps the old config if the new one
# is invalid, so a bad snippet cannot take other apps down.
cp deploy/${app}.caddy /etc/caddy/conf.d/${app}.caddy
sudo systemctl reload caddy

# The app fetches its content at startup, so give it time before failing
for _ in \$(seq 1 30); do
    if curl -fsS http://127.0.0.1:${port}/health > /dev/null; then
        echo "${app} is up"
        exit 0
    fi
    sleep 2
done
echo "${app} did not become healthy; recent logs:" >&2
docker compose -f deploy/compose.yaml logs --tail 30 >&2
exit 1
REMOTE
