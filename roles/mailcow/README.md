# mailcow

Installs [Mailcow Dockerized](https://github.com/mailcow/mailcow-dockerized) on a Docker host, designed to run behind Traefik as a reverse proxy.

## What this role does

- Clones the Mailcow repository to `mailcow_install_dir`
- Sets group ownership and permissions consistent with other Docker services (`02775`, group `docker`)
- Prints the manual steps required to complete the setup

## What this role does NOT do

Initial configuration and startup are intentionally manual — `generate_config.sh` requires root and interactive input (hostname, timezone, branch, IPv6/daemon.json). Updates are handled via Mailcow's own `./update.sh`.

## Setup (first install)

After running the playbook:

```bash
sudo git config --global --add safe.directory /opt/docker/mailcow-dockerized
cd /opt/docker/mailcow-dockerized && sudo ./generate_config.sh
```

Then patch `mailcow.conf` to use non-standard ports and bind on all interfaces (Traefik handles public 80/443, firewall must block 8080/8443 from outside):

```bash
sudo sed -i 's/^HTTP_PORT=.*/HTTP_PORT=8080/' mailcow.conf
sudo sed -i 's/^HTTP_BIND=.*/HTTP_BIND=0.0.0.0/' mailcow.conf
sudo sed -i 's/^HTTPS_PORT=.*/HTTPS_PORT=8443/' mailcow.conf
sudo sed -i 's/^HTTPS_BIND=.*/HTTPS_BIND=0.0.0.0/' mailcow.conf
sudo sed -i 's/^SKIP_LETS_ENCRYPT=.*/SKIP_LETS_ENCRYPT=y/' mailcow.conf
sudo sed -i 's/^SKIP_HTTP_VERIFICATION=.*/SKIP_HTTP_VERIFICATION=y/' mailcow.conf
```

Start:

```bash
sudo docker compose up -d --remove-orphans
```

## Traefik integration

Traefik proxies `mail.example.com` → `http://127.0.0.1:8080`. Configure the router and service in `traefik_dynamic_config` (see `host_vars/mail.yaml`).

## Updates

```bash
cd /opt/docker/mailcow-dockerized && sudo ./update.sh
```

## Variables

| Variable | Default | Description |
|---|---|---|
| `mailcow_install_dir` | `/opt/docker/mailcow-dockerized` | Clone destination |
| `mailcow_repo` | upstream GitHub | Mailcow repo URL |
| `mailcow_branch` | `master` | Git branch |
| `mailcow_hostname` | `mail.<domain>` | Mail server FQDN |
| `mailcow_timezone` | `Europe/Brussels` | Timezone |
| `mailcow_http_port` | `8080` | Internal HTTP port |
| `mailcow_http_bind` | `127.0.0.1` | Internal HTTP bind address |
| `mailcow_https_port` | `8443` | Internal HTTPS port |
| `mailcow_https_bind` | `127.0.0.1` | Internal HTTPS bind address |
| `mailcow_skip_lets_encrypt` | `true` | Disable Mailcow ACME (Traefik handles TLS) |
| `mailcow_skip_http_verification` | `true` | Skip HTTP verification behind reverse proxy |
