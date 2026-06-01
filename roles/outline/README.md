# Outline Role

Deploys [Outline](https://www.getoutline.com/) wiki with Postgres and Redis via Docker Compose. OIDC authentication (Authentik).

## Requirements

- `docker_host` role
- Traefik reverse proxy on the same Docker network
- Vault-encrypted secrets for OIDC and database credentials

## Role Variables

### Images

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_image_tag` | `1.7.1` | Outline image tag |
| `outline_postgres_image_tag` | `17.6-alpine` | Postgres image tag |
| `outline_redis_image_tag` | `8.2.2-alpine` | Redis image tag |

### Infrastructure

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_install_dir` | `{{ docker_host_services_root }}/outline` | Install directory |
| `outline_fqdn` | `wiki.{{ base_domain }}` | Public URL (Traefik rule) |
| `outline_network` | `{{ traefik_network_name }}` | External Traefik network |

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_web_concurrency` | `1` | Worker processes |
| `outline_language` | `en_US` | Default UI language |
| `outline_file_storage` | `local` | Storage backend (`local` or `s3`) |
| `outline_file_storage_local_root_dir` | `/var/lib/outline/data` | Local storage path |
| `outline_file_storage_upload_max_size` | `262144000` | Max upload size in bytes |
| `outline_force_https` | `false` | HTTPS redirect (Traefik handles TLS) |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_pg_user` | `outline` | Postgres username |
| `outline_pg_db` | `outline` | Postgres database name |
| `outline_pg_password` | — | **vault** |

### SMTP

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_smtp_host` | `""` | SMTP server hostname |
| `outline_smtp_port` | `25` | SMTP port |
| `outline_smtp_secure` | `false` | TLS for SMTP |
| `outline_smtp_from_email` | `Outline <outline@{{ base_domain }}>` | From address |

### OIDC

| Variable | Default | Description |
|----------|---------|-------------|
| `outline_oidc_display_name` | `authentik` | SSO button label |
| `outline_oidc_username_claim` | `preferred_username` | JWT claim for username |
| `outline_oidc_scopes` | `openid profile email` | OAuth scopes |
| `outline_oidc_client_id` | — | **vault** |
| `outline_oidc_client_secret` | — | **vault** |
| `outline_oidc_auth_uri` | — | **vault** |
| `outline_oidc_token_uri` | — | **vault** |
| `outline_oidc_userinfo_uri` | — | **vault** |
| `outline_oidc_logout_uri` | — | **vault** |

### Secrets

| Variable | Description |
|----------|-------------|
| `outline_secret_key` | **vault** — `openssl rand -hex 32` |
| `outline_utils_secret` | **vault** — `openssl rand -hex 32` |

## Example

```yaml
# site.yaml
- name: Docker services
  hosts: vm_docker
  roles:
    - role: outline
      tags: [outline]
```

```yaml
# group_vars/vm_docker/vars.yaml
outline_smtp_host: smtp.lan.example.com
outline_smtp_from_email: "Outline <outline@doc.lan.example.com>"
```

```yaml
# group_vars/vm_docker/vault.yaml (ansible-vault encrypted)
outline_pg_password: "..."
outline_secret_key: "..."
outline_utils_secret: "..."
outline_oidc_client_id: "..."
outline_oidc_client_secret: "..."
outline_oidc_auth_uri: "https://auth.lan.example.com/application/o/authorize/"
outline_oidc_token_uri: "https://auth.lan.example.com/application/o/token/"
outline_oidc_userinfo_uri: "https://auth.lan.example.com/application/o/userinfo/"
outline_oidc_logout_uri: "https://auth.lan.example.com/application/o/outline/end-session/"
```

## Notes

- Postgres and Redis run on an isolated `internal` network; only Outline is exposed via Traefik.
- `docker.env` is rendered with `no_log: true` — secrets never appear in Ansible output.
- Outline matches users by email on first OIDC login, making provider migration transparent.
- Postgres backup is out of scope for this role.

## Dependencies

- `docker_host` role
