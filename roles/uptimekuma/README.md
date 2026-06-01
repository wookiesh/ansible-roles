# Uptime Kuma Role

Deploys [Uptime Kuma](https://github.com/louislam/uptime-kuma) status page and uptime monitor. Supports Docker Compose (standalone) and Docker Swarm stack — the mode is auto-detected from `docker_host_swarm_enabled`.

Mounts the Docker socket so Uptime Kuma can monitor containers directly.

## Requirements

- `docker_host` role
- Traefik reverse proxy on the same Docker network

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `uptimekuma_image` | `louislam/uptime-kuma:2` | Image tag |
| `uptimekuma_install_dir` | `{{ docker_host_services_root }}/uptimekuma` | Install directory |
| `uptimekuma_deployment_mode` | auto-detected | `stack` if swarm, `compose` otherwise |
| `uptimekuma_domain` | `uptime.{{ server_domain }}` | Traefik hostname |
| `uptimekuma_network` | `{{ traefik_network_name }}` | External Traefik network |

### Deployment mode auto-detection

```yaml
uptimekuma_deployment_mode: "{{ 'stack' if docker_host_swarm_enabled | default(false) else 'compose' }}"
```

## Example

```yaml
# site.yaml
- name: Swarm services (infra cluster)
  hosts: swarm_infra
  roles:
    - role: uptimekuma
      tags: [uptimekuma]
```

```yaml
# group_vars/swarm_infra/vars.yaml
uptimekuma_domain: "uptime.ops.example.com"
```

## Data persistence

The role creates `{{ uptimekuma_install_dir }}/uptime-data/` and bind-mounts it to `/app/data`. In swarm mode the bind mount means data lives on the node where the service runs — pin it to a specific node if persistence across restarts matters.

## Swarm behaviour

In swarm mode the stack deploy runs `run_once: true` delegated to `docker_swarm_manager`.

## Dependencies

- `docker_host` role
