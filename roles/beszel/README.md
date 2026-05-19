# Beszel Role

Deploys [Beszel](https://beszel.dev/) lightweight server monitoring hub. Supports Docker Compose (standalone) and Docker Swarm stack — the mode is auto-detected from `docker_host_swarm_enabled`.

## Requirements

- `docker_host` role
- Traefik reverse proxy on the same Docker network

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `beszel_image` | `henrygd/beszel:latest` | Beszel hub image |
| `beszel_install_dir` | `{{ docker_host_services_root }}/beszel` | Install directory |
| `beszel_deployment_mode` | auto-detected | `stack` if swarm, `compose` otherwise |
| `beszel_domain` | `monitor.{{ server_domain }}` | Traefik hostname |
| `beszel_network` | `{{ traefik_network_name }}` | External Traefik network |
| `beszel_swarm_placement_node` | `{{ docker_swarm_manager }}` | Swarm node to pin the hub to |

### Deployment mode auto-detection

```yaml
beszel_deployment_mode: "{{ 'stack' if docker_host_swarm_enabled | default(false) else 'compose' }}"
```

## Example

```yaml
# site.yaml
- name: Swarm services (infra cluster)
  hosts: swarm_infra
  roles:
    - role: beszel
      tags: [beszel]
```

```yaml
# group_vars/swarm_infra/vars.yaml
beszel_domain: "monitor.ops.ana.lu"
```

## Swarm behaviour

In swarm mode the stack deploy runs `run_once: true` delegated to `docker_swarm_manager`. The hub service is pinned to the swarm manager node via a placement constraint (`node.hostname == {{ beszel_swarm_placement_node }}`).

## Dependencies

- `docker_host` role
