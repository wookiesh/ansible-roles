# Ansible Role: admin_user

Creates and configures a single bootstrap/recovery admin user on managed hosts — typically a shared break-glass account (`it`, `admin`, etc.) independent of individual team members.

For creating named team accounts (fetching SSH keys from a git provider), use the `create_admin_users` role instead.

## Requirements

- Ansible 2.9+
- Root/sudo access on target hosts
- Vault file with encrypted password hash

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `admin_user_enabled` | `true` | Enable/disable the role |
| `admin_user_name` | `""` | Username — **required**, no default |
| `admin_user_shell` | `/bin/bash` | Default shell |
| `admin_user_groups` | `["sudo"]` | Groups to add user to |
| `admin_user_password_hash` | `""` | Encrypted password hash — **required**, store in vault |
| `admin_user_ssh_key` | `""` | SSH public key — **required**, no default |

### OS-Specific Packages

| Variable | Description |
|----------|-------------|
| `admin_user_packages_debian` | Packages installed on Debian/Ubuntu |
| `admin_user_packages_redhat` | Packages installed on RHEL/CentOS |
| `admin_user_packages_arch` | Packages installed on Arch Linux |

## Usage

Define the three required variables in `group_vars` or `host_vars` — the role fails if any is empty.

```yaml
# group_vars/all.yml
admin_user_name: it
admin_user_ssh_key: "ssh-ed25519 AAAA..."
admin_user_password_hash: "{{ vault_admin_user_password_hash }}"
```

```yaml
- hosts: all
  vars_files:
    - secrets/vault.yml
  roles:
    - role: admin_user
      become: true
```

## Dependencies

- `ansible.posix` collection
