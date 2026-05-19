# ansible-roles

A collection of reusable Ansible roles for Linux infrastructure automation.
Designed to be consumed by multiple projects via `requirements.yml`.

## Roles

Roles have no `xxx_enabled` gate flag — they run unconditionally when assigned.
Use `hosts:` in your playbook to control which hosts a role runs on.

### Infrastructure

| Role | Description |
|------|-------------|
| [`admin_user`](roles/admin_user/) | Create and configure a single bootstrap/recovery admin user |
| [`create_admin_users`](roles/create_admin_users/) | Create named admin users with SSH keys fetched from a git provider |
| [`docker_host`](roles/docker_host/) | Install and configure Docker with security best practices and Swarm support |
| [`dotfiles`](roles/dotfiles/) | Install and configure dotfiles using GNU Stow |
| [`glusterfs`](roles/glusterfs/) | Install and configure GlusterFS distributed storage |
| [`keepalived`](roles/keepalived/) | Keepalived high availability and virtual IP management |
| [`prompt_starship`](roles/prompt_starship/) | Install and configure the Starship shell prompt |
| [`server`](roles/server/) | Configure automatic updates for servers |
| [`smtp`](roles/smtp/) | Configure Postfix as null client or relay host |
| [`ssh`](roles/ssh/) | Harden SSH server configuration |
| [`ssh_config_gen`](roles/ssh_config_gen/) | Generate `~/.ssh/config` entries from Ansible inventory |
| [`tailscale`](roles/tailscale/) | Install and configure Tailscale VPN (`tailscale_enabled` flag kept — no hosts yet) |
| [`traefik`](roles/traefik/) | Traefik reverse proxy for Docker containers and Swarm |

### Observability

| Role | Description |
|------|-------------|
| [`alloy`](roles/alloy/) | Grafana Alloy observability agent for Docker Swarm |

### Applications (per-app roles, replacing docker_stacks)

| Role | Description |
|------|-------------|
| [`portainer`](roles/portainer/) | Portainer CE management UI — compose or swarm stack, auto-detected |
| [`beszel`](roles/beszel/) | Beszel monitoring hub — compose or swarm stack, auto-detected |
| [`uptimekuma`](roles/uptimekuma/) | Uptime Kuma status page — compose or swarm stack, auto-detected |
| [`dns_server`](roles/dns_server/) | Technitium DNS server — compose mode |
| [`docker_stacks`](roles/docker_stacks/) | ~~DEPRECATED~~ — replaced by per-app roles above |

## Usage

### Option A — `ansible.cfg` (local clone)

Clone this repo alongside your project and point `roles_path` at it:

```ini
# ansible.cfg
[defaults]
roles_path = ../ansible-roles/roles
```

Roles are available immediately with no install step. Useful for active development or monorepo-style layouts.

### Option B — `requirements.yml` (pinned version)

```yaml
roles:
  - name: admin_user
    src: https://github.com/wookiesh/ansible-roles
    version: v1.0.0
    scm: git
```

```bash
ansible-galaxy install -r requirements.yml
```

## Versioning

Releases follow [semantic versioning](https://semver.org/) via git tags (`v1.0.0`, `v1.1.0`, …).
Pin to a specific tag in `requirements.yml` to ensure reproducible deployments.

## License

MIT
