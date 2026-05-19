# DNS Server Role

Deploys [Technitium DNS Server](https://technitium.com/dns/) as a Docker Compose service on standalone hosts. Designed for pairs of DNS servers managed by Keepalived for VIP failover.

Binds port 53 to `ansible_host` (the host's main IP) to avoid conflict with `systemd-resolved` stub listener on `127.0.0.53`.

## Requirements

- `docker_host` role (compose mode, `docker_host_swarm_enabled: false`)
- `traefik` role for the management UI
- `keepalived` role for VIP failover between the two DNS nodes

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_image` | `technitium/dns-server:13` | Image tag |
| `dns_server_install_dir` | `{{ docker_host_services_root }}/technitium` | Install directory |
| `dns_server_bind_ip` | `{{ ansible_host }}` | IP to bind port 53 on |
| `dns_server_ui_port` | `5380` | Internal HTTP port for the management UI |
| `dns_server_domain` | `{{ inventory_hostname }}.{{ server_domain }}` | Traefik hostname (per-node dashboard) |
| `dns_server_ui_domain` | `technitium.{{ inventory_hostname }}.ops.ana.lu` | Alt hostname for UI |
| `dns_server_timezone` | `{{ timezone \| default('Europe/Luxembourg') }}` | Container timezone |
| `dns_server_network` | `{{ traefik_network_name }}` | External Traefik network |

## Example

```yaml
# site.yaml
- name: DNS servers
  hosts: dns_servers
  roles:
    - role: docker_host
      tags: [docker]
    - role: traefik
      tags: [traefik]
    - role: keepalived
      tags: [keepalived]
    - role: dns_server
      tags: [dns]
```

```yaml
# group_vars/dns_servers/vars.yaml
docker_host_swarm_enabled: false
keepalived_interface: ens192
keepalived_vrrp_instances:
  - name: VI_DNS_HA
    virtual_router_id: 53
    virtual_ipaddress:
      - "10.219.206.253/24 dev {{ keepalived_interface }}"
    # ...
```

## Port 53 binding

Technitium listens on the host's `ansible_host` IP, not `0.0.0.0`. This leaves `127.0.0.53` (systemd-resolved stub) untouched so local name resolution on the host is unaffected.

## Dependencies

- `docker_host` role (compose mode)
