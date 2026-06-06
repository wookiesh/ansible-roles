# Dozzle Role

Deploys [Dozzle](https://dozzle.dev) — a real-time Docker log viewer.

Supports two modes controlled per-host by `dozzle_agent_mode`:

- **Central** (`dozzle_agent_mode: false`): serves the web UI via Traefik and aggregates logs from remote agents.
- **Agent** (`dozzle_agent_mode: true`): lightweight sidecar, exposes gRPC on port 7007, no web UI.

## Requirements

- `docker_host` role
- `traefik` role (central mode only)

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `dozzle_image` | `amir20/dozzle:latest` | Container image |
| `dozzle_install_dir` | `{{ docker_host_services_root }}/dozzle` | Installation directory |
| `dozzle_deployment_mode` | auto (`compose`/`stack`) | Compose or Swarm stack |
| `dozzle_domain` | `logs.{{ server_domain }}` | Central web UI domain (Traefik) |
| `dozzle_network` | `traefik_public` | Traefik network name |
| `dozzle_agent_mode` | `false` | `true` = agent only, `false` = central |
| `dozzle_agents` | `[]` | List of remote agents for the central (see below) |
| `dozzle_agent_bind_ip` | `""` | Bind IP for agent port 7007 (empty = all interfaces) |

### `dozzle_agents` format

```yaml
dozzle_agents:
  - name: dns01          # display name (used by DOZZLE_HOSTNAME on the agent)
    addr: "10.0.0.3:7007"  # bare ip:port — name@ip:port breaks gRPC resolver
```

> **Note:** Use bare `ip:port` format. The `name@ip:port` format causes a gRPC resolver error in Dozzle v10+. Display names come from `DOZZLE_HOSTNAME` set on each agent.

## Typical setup

Run all docker hosts as agents, override one host as the central viewer:

**`group_vars/docker_hosts/vars.yaml`**
```yaml
dozzle_agent_mode: true
```

**`host_vars/vm-docker/vars.yaml`**
```yaml
dozzle_agent_mode: false
dozzle_agents:
  - name: dns01
    addr: "{{ hostvars['dns01']['ansible_host'] }}:7007"
  - name: rpi
    addr: "{{ hostvars['rpi']['ansible_host'] }}:7007"
```

**`playbooks/site.yaml`**
```yaml
- name: Dozzle
  hosts: docker_hosts
  roles:
    - role: dozzle
      become: true
      tags: [dozzle]
```

## Security

The agent port (7007) has no authentication. For homelab use this is acceptable with a host firewall. For production, mTLS between agent and central is on the Dozzle roadmap.

## Tags

- `dozzle`
