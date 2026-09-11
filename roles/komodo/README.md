# Komodo Role

Deploys [Komodo](https://komo.do), GitOps orchestrator for Docker Compose/Swarm stacks (deployment, image updates, drift detection).

Mode is controlled per-host by `komodo_mode`, following the same pattern as the `dozzle` role:

- **`core`** (exactly one host, the central server): deploys MongoDB + Komodo Core + a local Periphery agent, all sharing a `keys` volume for the built-in co-located key exchange (no onboarding key needed for this host's own Periphery).
- **`periphery`** (every other host): deploys a standalone Periphery agent that connects outbound to Core over HTTPS, authenticating via a per-host onboarding key minted automatically through the Core API (login as admin, then `POST /write/CreateOnboardingKey`), delegated to the `core` host.

## Requirements

- `docker_host` role
- Traefik reverse proxy on the same Docker network (core host only)
- `vault_komodo_db_password`, `vault_komodo_admin_password`, `vault_komodo_webhook_secret`, `vault_komodo_jwt_secret`, `vault_komodo_oidc_client_secret` defined in the vault

## Role Variables

| Variable | Default | Description |
|----------|---------|--------------|
| `komodo_mode` | `periphery` | `core` on exactly one host, `periphery` everywhere else |
| `komodo_core_host` | `vm-docker` | Inventory hostname of the `core` host, periphery hosts delegate onboarding-key creation here |
| `komodo_image_tag` | `"2"` | Komodo Core/Periphery image tag (tracks latest v2.x) |
| `komodo_mongo_image` | `mongo:7` | MongoDB image (core host only) |
| `komodo_install_dir` | `{{ docker_host_services_root }}/komodo` | Compose project directory |
| `komodo_domain` | `komodo.{{ server_domain }}` | Traefik hostname for Core's web UI/API |
| `komodo_network` | `{{ traefik_network_name }}` | External Traefik network (core host only) |
| `komodo_periphery_root_directory` | `/etc/komodo` | Root dir Periphery uses for the stacks/repos it manages on that host, must be identical inside/outside the container ([moghtech/komodo#180](https://github.com/moghtech/komodo/discussions/180)) |
| `komodo_oidc_enabled` | `true` | Enable OIDC login (Authentik) on Core, in addition to local auth |
| `komodo_oidc_provider` |, | Authentik application issuer URL, e.g. `https://auth.example.com/application/o/komodo` (no `.well-known` suffix) |
| `komodo_oidc_client_id` / `komodo_oidc_client_secret` |, | From the Authentik OAuth2/OpenID Connect Provider. Redirect URI to register in Authentik: `https://{{ komodo_domain }}/auth/oidc/callback` |
| `komodo_oidc_use_full_email` | `true` | Use the full email as username for OIDC users instead of the bare subject id (requires the IdP to actually send an `email` claim) |

## Example

```yaml
# playbooks/site.yaml
- name: Docker hosts
  hosts: docker_hosts
  roles:
    - role: komodo
      become: true
      tags: [komodo]
```

```yaml
# host_vars/vm-docker/vars.yaml
komodo_mode: core
```

`group_vars/docker_hosts/vars.yaml` leaves `komodo_mode` at its `periphery` default, so every other host in the group only runs a Periphery agent.

## Notes

- The Komodo stack itself is **not** onboarded as a Komodo-managed "Stack" resource, Komodo cannot cleanly redeploy/restart its own stack (see [moghtech/komodo#223](https://github.com/moghtech/komodo/discussions/223)). It stays a plain Ansible-deployed compose stack, like every other app on `docker_hosts`.
- Re-running the play on an already-connected periphery host mints a new (unused) onboarding key each time, harmless, since Periphery ignores the key once already known to Core under its `PERIPHERY_CONNECT_AS` name, but it does leave stale keys visible in Core's onboarding key list.

## Dependencies

- `docker_host` role
