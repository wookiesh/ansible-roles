# Ansible Role: create_admin_users

Creates and configures admin users on managed hosts from a list defined in inventory, with SSH keys fetched automatically from a git provider (GitLab, GitHub, or compatible).

## Features

- Creates multiple admin users in a single role invocation
- Fetches SSH public keys from any git provider that exposes `/<username>.keys`
- Configures `pam_ssh_agent_auth` for passwordless sudo authenticated via SSH key
- Disabled by default — opt-in per group/host via `create_admin_users_enabled`

## Requirements

- `ansible.posix` collection
- SSH agent forwarding enabled on connecting clients (`ForwardAgent yes`)
- Git provider with public profile visibility (or accessible from the control node)

## Variables

| Variable                              | Default     | Description                              |
| ------------------------------------- | ----------- | ---------------------------------------- |
| `create_admin_users_enabled`          | `false`     | Enable/disable the role                  |
| `create_admin_users_git_url`          | `""`        | Git provider base URL (required)         |
| `create_admin_users_shell`            | `/bin/bash` | Default shell for created users          |
| `create_admin_users_default_groups`   | `[sudo]`    | Default groups if not specified per user |
| `create_admin_users_pam_sudo_enabled` | `true`      | Configure pam_ssh_agent_auth for sudo    |
| `create_admin_users_list`             | `[]`        | List of users to create (see below)      |

### User list format

```yaml
create_admin_users_list:
  - name: alice             # Linux username (required)
    git_user: alice_git     # username on the git provider (required)
    full_name: Alice        # optional, sets GECOS field in /etc/passwd
    groups: [sudo, docker]
    shell: /bin/zsh         # optional, overrides create_admin_users_shell
```

## Sudo authentication

When `create_admin_users_pam_sudo_enabled` is true, the role:

1. Installs `libpam-ssh-agent-auth`
2. Adds `auth sufficient pam_ssh_agent_auth.so file=%h/.ssh/authorized_keys` to `/etc/pam.d/sudo`
3. Creates `/etc/sudoers.d/ssh_agent_auth` to preserve `SSH_AUTH_SOCK`

Users can then run `sudo` without a password as long as their SSH agent is forwarded and holds a key matching their `authorized_keys`.

**Client requirement**: `ForwardAgent yes` in `~/.ssh/config` for the relevant hosts, or `-A` flag when connecting.

> **Note**: SSH agent forwarding is safe in this setup because connections go through Tailscale or VPN — the exit node only sees encrypted Tailscale traffic and cannot access the agent socket.

## Usage

Define in `group_vars` or `host_vars`:

```yaml
create_admin_users_enabled: true
create_admin_users_git_url: "https://github.com"
create_admin_users_list:
  - name: alice
    git_user: alice_git
    full_name: Alice
    groups: [sudo, docker]
    shell: /bin/zsh
```

Run:

```bash
ansible-playbook -i inventories/myproject/hosts.yaml infrastructure.yaml --tags admin_users
```
