# Portainer Role

Deploys [Portainer CE](https://www.portainer.io/) container management UI with its agent. Supports both Docker Compose (standalone) and Docker Swarm stack deployment — the mode is auto-detected from `docker_host_swarm_enabled`.

## Requirements

- `docker_host` role
- Traefik reverse proxy on the same Docker network

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `portainer_image` | `portainer/portainer-ce:latest` | Portainer CE image |
| `portainer_agent_image` | `portainer/agent:latest` | Portainer agent image (swarm only) |
| `portainer_install_dir` | `{{ docker_host_services_root }}/portainer` | Install directory |
| `portainer_deployment_mode` | auto-detected | `stack` if swarm, `compose` otherwise |
| `portainer_domain` | `swarm.{{ server_domain }}` | Traefik hostname |
| `portainer_network` | `{{ traefik_network_name }}` | External Traefik network |

### Deployment mode auto-detection

```yaml
portainer_deployment_mode: "{{ 'stack' if docker_host_swarm_enabled | default(false) else 'compose' }}"
```

Override explicitly if needed:
```yaml
portainer_deployment_mode: "compose"
```

## Example

```yaml
# site.yaml
- name: Swarm services (all clusters)
  hosts: swarm_nodes
  roles:
    - role: portainer
      tags: [portainer]
```

```yaml
# group_vars/swarm_infra/vars.yaml
portainer_domain: "swarm.ops.ana.lu"
```

## Swarm behaviour

In swarm mode the stack deploy runs `run_once: true` delegated to `docker_swarm_manager`. The Portainer agent runs as a global service on all nodes; the CE server runs as a replicated service (1 replica).

## Dependencies

- `docker_host` role
