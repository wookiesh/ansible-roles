# DNS Server Role

Deploys [Technitium DNS Server](https://technitium.com/dns/) as a Docker Compose service on standalone hosts. Designed for primary/secondary pairs managed by Keepalived for VIP failover.

Binds port 53 to `0.0.0.0` so the Keepalived VIP (secondary address) is also reachable. Disables the `systemd-resolved` stub listener and configures fallback DNS so the host resolves normally if Technitium is down.

## Requirements

- `docker_host` role (compose mode, `docker_host_swarm_enabled: false`)
- `traefik` role for the management UI
- `keepalived` role for VIP failover between the two DNS nodes

## Role Variables

### Core

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_image` | `technitium/dns-server:15.2.0` | Image tag |
| `dns_server_install_dir` | `{{ docker_host_services_root }}/technitium` | Install directory |
| `dns_server_bind_ip` | `0.0.0.0` | IP to bind ports 53 and 853 on |
| `dns_server_ui_port` | `5380` | Internal HTTP port for the management UI |
| `dns_server_domain` | `{{ inventory_hostname }}.{{ server_domain }}` | Traefik hostname (per-node dashboard) |
| `dns_server_ui_domain` | `technitium.{{ inventory_hostname }}.{{ server_domain }}` | Alt hostname for UI |
| `dns_server_vip_domain` | `""` | Optional shared VIP domain exposed on both nodes |
| `dns_server_timezone` | `{{ timezone \| default('Europe/Luxembourg') }}` | Container timezone |
| `dns_server_network` | `{{ traefik_network_name }}` | External Traefik network |
| `dns_server_admin_password` | — | Technitium admin password (from vault) |
| `dns_server_real_ip_header` | `""` | HTTP header for real client IP when behind a reverse proxy |

### Upstream forwarders

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_fallback_dns` | `["9.9.9.9", "149.112.112.112"]` | Upstream resolvers (also written to systemd-resolved fallback) |
| `dns_server_fallback_dns_protocol` | `Udp` | Protocol for upstream: `Udp` \| `Tcp` \| `Tls` \| `Https` \| `Quic` |

### DNS-over-TLS (DoT)

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_dot_enabled` | `false` | Enable DoT listener on port 853 |
| `dns_server_tls_cert_dir` | `""` | Path to directory with `cert.pem` + `key.pem`; a `dot.pfx` is generated from them |

### Zone management

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_group_name` | `dns_servers` | Inventory group name; `[0]` is the primary node |
| `dns_server_zones` | `[]` | List of zone definitions (see below) |
| `dns_server_apps` | `[]` | List of Technitium apps to install from the app store |

Each zone entry:

```yaml
dns_server_zones:
  - name: "ops.ana.lu"
    primary_type: Primary          # zone type applied to groups[dns_server_group_name][0]
    secondary_type: Secondary      # zone type applied to remaining nodes
    # For Forwarder zones:
    forwarder: "9.9.9.9"
    dnssec_validation: true        # optional
    records:
      - { name: swarm, type: A, value: "10.219.206.36" }
      - { name: traefik, type: CNAME, value: "swarm.ops.ana.lu." }
      - { name: "10", type: PTR, value: "host.ops.ana.lu." }
```

Supported zone types: `Primary`, `Secondary`, `Stub`, `Forwarder`, `SecondaryForwarder`.

The primary node configures zone transfer (AXFR) authorization and notify for the secondary. The secondary auto-resyncs all zones after provisioning.

### Security / hardening

| Variable | Default | Description |
|----------|---------|-------------|
| `dns_server_recursion` | `AllowOnlyForPrivateNetworks` | Recursion policy: `Deny` \| `Allow` \| `AllowOnlyForPrivateNetworks` \| `UseSpecifiedNetworkACL` |
| `dns_server_dnssec_validation` | `true` | Validate DNSSEC for all upstream/forwarder responses |
| `dns_server_qname_minimization` | `true` | Send minimal labels to upstream resolvers (privacy) |
| `dns_server_randomize_name` | `true` | 0x20 QNAME randomization against cache poisoning |
| `dns_server_enable_blocking` | `false` | Enable DNS blocking via block lists |
| `dns_server_blocking_type` | `NxDomain` | Blocking response type: `NxDomain` \| `AnyAddress` \| `CustomAddress` |
| `dns_server_block_list_urls` | `[]` | Block list URLs (standard hosts file or plain domain list format) |
| `dns_server_qpm_limits_ipv4` | `""` | Per-subnet QPM rate limits: pipe-separated `prefix\|udpLimit\|tcpLimit` rows |
| `dns_server_qpm_limits_ipv6` | `""` | Same for IPv6 |

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
dns_server_vip_domain: "dns.ops.ana.lu"
dns_server_ui_domain: "{{ 'dns01' if inventory_hostname == groups['dns_servers'][0] else 'dns02' }}.ops.ana.lu"
dns_server_admin_password: "{{ vault_dns_server_admin_password }}"
dns_server_dot_enabled: true
dns_server_tls_cert_dir: "{{ traefik_tls_cert_dir }}"
dns_server_fallback_dns:
  - "9.9.9.9"
  - "149.112.112.112"
dns_server_fallback_dns_protocol: "Tls"

dns_server_enable_blocking: true
dns_server_block_list_urls:
  - "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
dns_server_qpm_limits_ipv4: "32|500|100"

dns_server_zones:
  - name: "ops.ana.lu"
    primary_type: Primary
    secondary_type: Secondary
    records:
      - { name: swarm, type: A, value: "10.219.206.36" }

keepalived_interface: ens192
keepalived_vrrp_instances:
  - name: VI_DNS_HA
    state: "{{ 'MASTER' if inventory_hostname == groups['dns_servers'][0] else 'BACKUP' }}"
    interface: "{{ keepalived_interface }}"
    virtual_router_id: 53
    priority: "{{ 110 if inventory_hostname == groups['dns_servers'][0] else 100 }}"
    virtual_ipaddress:
      - "10.219.206.253/24 dev {{ keepalived_interface }}"
```

## Dependencies

- `docker_host` role (compose mode)
