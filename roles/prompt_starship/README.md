# Ansible Role: prompt_starship

This role sets [Starship](https://starship.rs) as prompt, a minimal, blazing-fast, and infinitely customizable prompt for any shell!

## Features

- Automatic Starship installation
- Support for both standard `.zshrc` and `ZDOTDIR` configurations
- Proper user permissions handling
- Clean installation process

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `prompt_starship_zdotdir` | `"{{ admin_user_info.home }}/.config/zsh"` | ZDOTDIR path for zsh configuration |

## Usage

```yaml
- hosts: workstations
  roles:
    - prompt_starship
```

## Notes

- The role will add Starship configuration to both standard `.zshrc` and ZDOTDIR `.zshrc` if it exists
- Requires admin_user_info.home to be available (set by admin_user role)
- Uses the official Starship installation script
