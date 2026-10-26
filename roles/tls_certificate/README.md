# Ansible Role: tls_certificate

Pushes the wildcard certificate and its private key to a Linux host, then reloads the services that use them. It replaces the reboot-on-change behaviour of the old pyinfra task (`linux-management`).

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `tls_certificate_deploy` | `false` | Per-host switch. Set to `true` on the hosts that must receive the certificate. |
| `tls_certificate_cert` | `{{ vault_traefik_tls_cert }}` | Leaf certificate followed by the intermediate(s), PEM. |
| `tls_certificate_key` | `{{ vault_traefik_tls_key }}` | Private key, PEM. Never printed (`no_log`). |
| `tls_certificate_cert_path` | `/etc/ssl/certs/star_ana_lu.crt` | Destination, `0644 root:root`. |
| `tls_certificate_key_path` | `/etc/ssl/private/star_ana_lu.key` | Destination, `0640 root:<key group>`. |
| `tls_certificate_key_group` | `ssl-cert` | Group allowed to read the key, created if missing. |
| `tls_certificate_reload_services` | `[]` | Services reloaded (not restarted) when a file changes, e.g. `["nginx"]`. |
| `tls_certificate_reload_commands` | `[]` | Commands run after the services, for consumers that are not a plain service, e.g. `["gitlab-ctl hup nginx"]`. |

The role first checks that the key matches the certificate (public key fingerprint, run on the controller) and fails before touching any host otherwise.

## Usage

```yaml
# host_vars/vms-docker.yaml
tls_certificate_deploy: true
tls_certificate_reload_services: [nginx]
```

```yaml
- hosts: managed_servers
  roles:
    - role: tls_certificate
      tags: [tls]
```

Test on one host first with `--limit <host>`, preceded by `--check --diff`.
