# Ansible Role: alloy_native

Installs [Grafana Alloy](https://grafana.com/docs/alloy/) directly from Grafana's apt repository (`apt.grafana.com`), no Docker. For hosts that don't run Docker (e.g. hardened, single-purpose VMs) but still need to ship metrics/logs to Grafana Cloud, as an alternative to the Docker-based `alloy` role.

Compared to being scraped remotely by another cluster's Alloy, running Alloy locally lets the host ship both metrics *and* logs (local file tailing) and removes any dependency on another cluster's health.

## Variables

- `alloy_native_grafana_cloud_prometheus_url` / `_username`: Prometheus/Mimir remote_write endpoint
- `alloy_native_grafana_cloud_loki_url` / `_username`: Loki push endpoint
- `alloy_native_scrape_targets`: list of `{job_name, address, scrape_interval?}` — other exporters on the same host (e.g. `node_exporter` on `127.0.0.1:9100`). The Prometheus `job` label is `prometheus.scrape.<job_name>` (Alloy's own component-path convention), `instance` is set to `inventory_hostname`.
- `alloy_native_scrape_interval`: default scrape interval (default `30s`)
- `alloy_native_log_targets`: list of `{job_name, path}` — local log files to tail via `loki.source.file`. Labels: `job = job_name`, `instance = inventory_hostname`.
- `alloy_native_environment` / `alloy_native_cluster`: external labels added to all telemetry

Requires `vault_grafana_cloud_api_key` (same key used by the Docker `alloy` role).

## Usage

```yaml
- hosts: smtp_relays
  roles:
    - alloy_native
```

```yaml
# group_vars
alloy_native_grafana_cloud_prometheus_url: "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push"
alloy_native_grafana_cloud_prometheus_username: "391266"
alloy_native_grafana_cloud_loki_url: "https://logs-prod-eu-west-0.grafana.net/loki/api/v1/push"
alloy_native_grafana_cloud_loki_username: "194603"
alloy_native_scrape_targets:
  - { job_name: "smtp_relay_node", address: "127.0.0.1:9100" }
  - { job_name: "smtp_relay_postfix", address: "127.0.0.1:9154" }
alloy_native_log_targets:
  - { job_name: "smtp_relay_postfix_log", path: "/var/lib/prometheus/postfix-exporter/mail.log" }
```

## Verification

```bash
curl -s localhost:12345/-/ready
systemctl status alloy
curl -s http://localhost:12345/api/v0/web/components | jq
```
