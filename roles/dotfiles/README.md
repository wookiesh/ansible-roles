# Ansible Role: dotfiles

Sets up dotfiles via a bootstrap script on macOS or Linux. Supports any dotfiles repo
structure (GNU Stow, symlinks, custom scripts).

## Requirements

- Ansible 2.9+
- Git and GNU Stow on the target host (installed by the role if needed)

## Role Variables

### Required

| Variable | Default | Description |
|----------|---------|-------------|
| `dotfiles_user` | `""` | Local user who owns the dotfiles (fails if unset) |
| `dotfiles_repo` | `""` | HTTPS URL of the dotfiles git repository (fails if unset) |

### Main Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `dotfiles_dest` | `"dev/dotfiles"` | Clone path relative to the user's home directory |
| `dotfiles_version` | `"main"` | Git branch/tag/commit to checkout |
| `dotfiles_force_update` | `false` | Force update existing repository |
| `dotfiles_backup_existing` | `true` | Backup existing dotfiles before overwriting |

### Bootstrap

| Variable | Default | Description |
|----------|---------|-------------|
| `dotfiles_bootstrap_script` | `"./bootstrap.sh"` | Path to the bootstrap script (relative to repo) |
| `dotfiles_bootstrap_remote` | `true` | On Linux: pass `remote` arg to bootstrap script |
| `dotfiles_bootstrap_dev` | `false` | On macOS: pass `dev` arg instead of `remote` |

### Package Management

| Variable | Default | Description |
|----------|---------|-------------|
| `dotfiles_packages_debian` | `["git", "stow"]` | Packages for Debian/Ubuntu |
| `dotfiles_packages_redhat` | `["git", "stow"]` | Packages for RHEL/CentOS |
| `dotfiles_packages_arch` | `["git", "stow"]` | Packages for Arch Linux |
| `dotfiles_packages_darwin` | `["git", "stow"]` | Packages for macOS |

### Advanced

| Variable | Default | Description |
|----------|---------|-------------|
| `dotfiles_stow_packages` | `[]` | Specific stow packages to deploy |
| `dotfiles_custom_scripts` | `[]` | Additional scripts to run after bootstrap |

## Example Playbook

```yaml
- hosts: managed_servers
  roles:
    - role: dotfiles
      become: true
      become_user: "{{ dotfiles_user }}"
      vars:
        dotfiles_user: "alice"
        dotfiles_repo: "https://github.com/yourusername/dotfiles.git"
        dotfiles_version: "main"
        dotfiles_backup_existing: true
```

> `become: true` and `become_user` are set at the role level, not the play level.
> The role elevates to root internally for package installation; all other tasks run as `dotfiles_user`.

## Repository Structure

The dotfiles repository must contain a `bootstrap.sh` at its root. The role calls it
with a positional argument:

- Linux: `bootstrap.sh remote` (or `local` if `dotfiles_bootstrap_remote: false`)
- macOS: `bootstrap.sh dev` (if `dotfiles_bootstrap_dev: true`) or `bootstrap.sh remote`

The `changed_when` condition matches on `Stowing` or `Linking` in the script output.

## Backup

When `dotfiles_backup_existing: true`, existing dotfiles are backed up via `backup.yaml`
before the bootstrap runs.

## License

MIT
