# TODO

## Known limitations

- **`dozzle` agent auth** — agents expose port 7007 with no authentication. `dozzle_agent_bind_ip`
  limits the bind interface but relies on external firewall for production isolation.
  Long-term fix: mTLS between agent and central (Dozzle supports `--ssl-cert-file` / `--ssl-key-file`).

## New roles to create

### System-level services (dedicated roles — config beyond a compose file)

- [ ] `ntp` — chrony NTP server; covers dns hosts, ubuntu hosts, mail (see homelab TODO)
- [ ] `fail2ban` — intrusion prevention; needs jail config templated per host type
- [ ] `wireguard` — VPN; needs key management and peer config generation

### Platform services (dedicated roles — complex or multi-host config)

- [ ] `authentik` — SSO / identity provider; needs bootstrap, tenant config, outpost setup
- [ ] `vaultwarden` — Bitwarden-compatible password manager; needs backup hooks
- [ ] `uptime_kuma` — uptime monitoring; already a role in ana-infra, extract to shared

### App stacks (stack templates only — straight compose deploys, no Ansible logic needed)

Currently running on `vm-docker`, to be templated as `stacks/` in each consumer project:

| Stack             | Description                        |
| ----------------- | ---------------------------------- |
| `apprise`         | Notification aggregator            |
| `backrest`        | Backup manager (restic frontend)   |
| `calibre`         | Ebook library                      |
| `cloudflare`      | Cloudflare tunnel / DDNS           |
| `emqx`            | MQTT broker                        |
| `esphome`         | ESP8266/ESP32 firmware builder     |
| `garage`          | S3-compatible object storage       |
| `gitea`           | Self-hosted git                    |
| `homeassistant`   | Home automation                    |
| `homepage`        | Dashboard                          |
| `ittools`         | IT tools collection                |
| `jellyfin`        | Media server                       |
| `karakeep`        | Bookmarks / read-it-later          |
| `kms`             | Microsoft KMS activation server    |
| `logs`            | Log aggregation (Loki / Promtail)  |
| `mailpit`         | SMTP catch-all for dev/testing     |
| `monitoring`      | Grafana + alerting                 |
| `ntfy`            | Push notifications                 |
| `nut`             | Network UPS Tools client           |
| `outline`         | Wiki (already a role in ana-infra) |
| `owntracks`       | Location recorder                  |
| `paperless`       | Document management                |
| `portainer`       | Docker management UI               |
| `prometheus`      | Metrics scraping                   |
| `reitti`          | Custom app                         |
| `searxng`         | Metasearch engine                  |
| `servarrs`        | *arr stack (Sonarr/Radarr/etc.)    |
| `bentopdf`        | PDF tools                          |
| `uptime-kuma`     | Uptime monitoring                  |
| `vaultwarden`     | Password manager                   |
| `whatsupdocker`   | Docker image update watcher        |
| `windmill`        | Workflow automation                |
| `zigbee2mqtt`     | Zigbee → MQTT bridge               |
