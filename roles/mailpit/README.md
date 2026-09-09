# Mailpit Role

> **DEPRECATED**, Migrated to a Komodo Stack (`mailpit`, `homelab-docker-stacks` repo, 2026-09-08). This role will be removed once confirmed unused elsewhere.

Deploys [Mailpit](https://mailpit.axllent.org), an SMTP catch-all and email testing tool with a web UI.

## Requirements

- `docker_host` role
- `traefik` role

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `mailpit_image` | `axllent/mailpit:v1.30.1` | Container image |
| `mailpit_install_dir` | `{{ docker_host_services_root }}/mailpit` | Installation directory |
| `mailpit_domain` | `mailpit.{{ server_domain }}` | Web UI domain (Traefik) |
| `mailpit_network` | `traefik_public` | Traefik network name |
| `mailpit_smtp_port` | `1025` | Host port for SMTP |
| `mailpit_max_messages` | `5000` | Maximum stored messages |
| `mailpit_smtp_auth_accept_any` | `true` | Accept any SMTP credentials |
| `mailpit_smtp_auth_allow_insecure` | `true` | Allow insecure SMTP auth |

## Typical setup

**`playbooks/site.yaml`**
```yaml
- name: Mailpit
  hosts: vm-docker
  roles:
    - role: mailpit
      become: true
      tags: [mailpit]
```

**`host_vars/vm-docker/vars.yaml`** (override domain if needed)
```yaml
mailpit_domain: "mailpit.lan.miom.be"
```

## Ports

- **SMTP**: `mailpit_smtp_port` (default 1025), exposed on the host, used by services sending mail
- **Web UI**: 8025, served by Traefik at `mailpit_domain`
- **POP3**: 1110, not exposed (not used)

## Tags

- `mailpit`
