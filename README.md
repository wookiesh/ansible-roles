# ansible-roles

A collection of reusable Ansible roles for Linux infrastructure automation.
Designed to be consumed by multiple projects via `requirements.yml`.

## Roles

| Role | Description |
|------|-------------|
| [`admin_user`](roles/admin_user/) | Create and configure a single bootstrap/recovery admin user |
| [`alloy`](roles/alloy/) | Grafana Alloy observability agent for Docker Swarm |
| [`create_admin_users`](roles/create_admin_users/) | Create named admin users with SSH keys fetched from a git provider |
| [`docker_host`](roles/docker_host/) | Install and configure Docker with security best practices and Swarm support |
| [`docker_stacks`](roles/docker_stacks/) | Deploy and manage Docker Compose and Docker Swarm stacks |
| [`dotfiles`](roles/dotfiles/) | Install and configure dotfiles using GNU Stow |
| [`glusterfs`](roles/glusterfs/) | Install and configure GlusterFS distributed storage |
| [`keepalived`](roles/keepalived/) | Keepalived high availability and virtual IP management |
| [`nut_client`](roles/nut_client/) | Configure NUT client for UPS monitoring |
| [`nut_server`](roles/nut_server/) | Install and configure NUT server for UPS management |
| [`prompt_starship`](roles/prompt_starship/) | Install and configure the Starship shell prompt |
| [`server`](roles/server/) | Configure automatic updates for servers |
| [`smtp`](roles/smtp/) | Configure Postfix as null client or relay host |
| [`ssh`](roles/ssh/) | Harden SSH server configuration |
| [`ssh_config_gen`](roles/ssh_config_gen/) | Generate `~/.ssh/config` entries from Ansible inventory |
| [`tailscale`](roles/tailscale/) | Install and configure Tailscale VPN |
| [`traefik`](roles/traefik/) | Traefik reverse proxy for Docker containers and Swarm |

## Usage

Add to your project's `requirements.yml`:

```yaml
roles:
  - name: admin_user
    src: https://github.com/wookiesh/ansible-roles
    version: v1.0.0
    scm: git
```

Then install:

```bash
ansible-galaxy install -r requirements.yml
```

## Versioning

Releases follow [semantic versioning](https://semver.org/) via git tags (`v1.0.0`, `v1.1.0`, …).
Pin to a specific tag in `requirements.yml` to ensure reproducible deployments.

## License

MIT
