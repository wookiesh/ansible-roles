# Alloy Role

## Description

Deploys [Grafana Alloy](https://grafana.com/docs/alloy/) as a Docker Swarm global service on manager nodes. Ships Traefik access logs (JSON) to Grafana Cloud Loki and optionally scrapes Traefik metrics to Grafana Cloud Prometheus/Mimir.

Alloy is the successor to Grafana Agent / Promtail. It uses River syntax (`.alloy` files) and supports logs, metrics, and traces in a single agent.

## Requirements

- Ansible >= 2.15
- Docker Swarm (manager nodes)
- `docker_host` role
- Grafana Cloud account (free tier: 50 GB logs/month, 10k metric series)
- `vault_grafana_cloud_api_key` in your vault

## Dependencies

- `docker_host` role

## Opt-in

This role is disabled by default. Set `alloy_enabled: true` in your host_vars to activate it.

**Dependency on Traefik role:** Alloy reads log files written by Traefik. You must also enable file-based access logging in the Traefik role:

```yaml
# In host_vars — Traefik side
traefik_access_log_path: "{{ traefik_install_dir }}/logs"

traefik_static_config:
  accessLog:
    filePath: "{{ traefik_access_log_path }}/access.log"
    format: json
  # ... rest of your config

# In host_vars — Alloy side
alloy_enabled: true
alloy_traefik_log_path: "{{ traefik_access_log_path }}"
```

## Role Variables

### Main

- `alloy_enabled`: Enable Alloy deployment (default: `false`)
- `alloy_version`: Alloy image tag (default: `v1.7.4` — check for latest)

### Paths

- `alloy_install_dir`: Install directory (default: `{{ docker_host_services_root }}/alloy`)
- `alloy_config_dir`: Config directory (default: `{{ alloy_install_dir }}/config`)

### Grafana Cloud — Loki

- `alloy_loki_enabled`: Enable log shipping (default: `true`)
- `alloy_grafana_cloud_loki_url`: Loki push URL from Grafana Cloud
- `alloy_grafana_cloud_loki_username`: Loki numeric user ID from Grafana Cloud

### Grafana Cloud — Prometheus/Mimir (opt-in)

- `alloy_metrics_enabled`: Enable metrics scraping (default: `false`)
- `alloy_grafana_cloud_prometheus_url`: Remote write URL from Grafana Cloud
- `alloy_grafana_cloud_prometheus_username`: Prometheus numeric user ID
- `alloy_traefik_metrics_port`: Traefik metrics port (default: `8899`)
- `alloy_scrape_interval`: Prometheus scrape interval (default: `30s`)

### Traefik log collection

- `alloy_traefik_logs_enabled`: Enable Traefik log tailing (default: `true`)
- `alloy_traefik_log_path`: Path to Traefik log directory — **must match `traefik_access_log_path`** (default: `""`)

### Labels

- `alloy_environment`: Value for the `environment` label on all telemetry (default: `production`)
- `alloy_cluster`: Value for the `cluster` label — leave empty to omit (default: `""`)
- `alloy_extra_labels`: Additional labels to add to all telemetry (default: `{}`)

### Vault

```yaml
# vault.yml
vault_grafana_cloud_api_key: "glc_..."
```

Generate the key in Grafana Cloud → Security → API keys (MetricsPublisher role covers both Loki and Prometheus).

## Example host_vars (Swarm, Loki only)

```yaml
alloy_enabled: true
alloy_traefik_log_path: "{{ traefik_access_log_path }}"

alloy_loki_enabled: true
alloy_grafana_cloud_loki_url: "https://logs-prod-eu-west-0.grafana.net/loki/api/v1/push"
alloy_grafana_cloud_loki_username: "123456"

alloy_environment: "production"
alloy_cluster: "my-cluster"
```

## Example host_vars (Loki + Metrics)

```yaml
alloy_enabled: true
alloy_traefik_log_path: "{{ traefik_access_log_path }}"

alloy_loki_enabled: true
alloy_grafana_cloud_loki_url: "https://logs-prod-eu-west-0.grafana.net/loki/api/v1/push"
alloy_grafana_cloud_loki_username: "123456"

alloy_metrics_enabled: true
alloy_grafana_cloud_prometheus_url: "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push"
alloy_grafana_cloud_prometheus_username: "654321"

alloy_environment: "production"
alloy_cluster: "my-cluster"
```

## Log labels extracted from Traefik JSON

| Label | Traefik field |
|---|---|
| `method` | `RequestMethod` |
| `status` | `DownstreamStatus` |
| `router` | `RouterName` |
| `service` | `ServiceName` |
| `entrypoint` | `entryPointName` |
| `host` | node hostname (via `constants.hostname`) |
| `environment` | `alloy_environment` |
| `cluster` | `alloy_cluster` (if set) |

`RequestPath` and `ClientHost` are intentionally not labels (high cardinality — query them from the log body).

## Swarm placement

Alloy is deployed as a global service constrained to manager nodes — mirroring the Traefik placement so both services co-locate on the same nodes and can share the log directory bind mount.

Override with `alloy_swarm_placement_constraints` if needed.

## Credentials

The Grafana Cloud API key is stored as a Docker Swarm secret (`grafana_cloud_api_key`) and read by Alloy via `local.file`. It is never written to the stack file or config file in plaintext.

## Tags

- `alloy_validate`: Validate configuration
- `alloy_install`: Create directories
- `alloy_configure`: Deploy stack

## Troubleshooting

```bash
# Check service status
docker stack services alloy

# Check logs
docker service logs alloy_alloy

# Verify config syntax (on a manager node)
docker run --rm -v /opt/docker/alloy/config:/etc/alloy grafana/alloy:v1.7.4 \
  fmt /etc/alloy/config.alloy

# Check Alloy UI (port 12345 on any manager)
curl http://localhost:12345/-/ready
```
