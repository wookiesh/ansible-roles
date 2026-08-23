# Ansible Role: node_exporter

Installs the distro-packaged Prometheus [`node_exporter`](https://github.com/prometheus/node_exporter) (`prometheus-node-exporter` on Debian/Ubuntu). No Docker required — the package ships its own systemd unit, creates the `prometheus` system user, and starts/enables the service on install.

## Why distro package, not the upstream binary/Docker

Node metrics don't need anything Docker gives you, and pulling GitHub releases onto a host that otherwise has no reason to reach the internet adds surface for no benefit. The `prometheus-node-exporter` package is in the standard Ubuntu `universe` / Debian `main` repos and needs no extra APT source.

## Variables

None — the package default (`--web.listen-address=":9100"`, all standard collectors enabled) is used as-is. Scraping is configured on the Alloy/Prometheus side (see the `alloy` role's `alloy_extra_scrape_targets`).

## Usage

```yaml
- hosts: smtp_relays
  roles:
    - node_exporter
```

## Verification

```bash
curl -s localhost:9100/metrics | head
systemctl status prometheus-node-exporter
```
