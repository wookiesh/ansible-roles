# SSH Hardening Role

A comprehensive Ansible role for hardening SSH servers with modern security best practices.

## Features

- **SSH Daemon Hardening**: Disables insecure protocols, enforces key-based authentication
- **Cryptographic Hardening**: Uses modern ciphers, MACs, and key exchange algorithms
- **Access Control**: Group-based user restrictions and deny lists
- **Fail2ban Integration**: Automatic IP banning for failed login attempts
- **Security Banner**: Legal warning for unauthorized access attempts
- **Configuration Validation**: Automated testing of SSH settings

## Variables

### Core Settings
- `ssh_install_server`: Enable SSH server installation (default: false)
- `ssh_port`: SSH port (default: 22)
- `ssh_permit_root_login`: Root login access (default: "no")
- `ssh_password_authentication`: Password auth (default: "no")

### Security Settings
- `ssh_max_auth_tries`: Maximum authentication attempts (default: 3)
- `ssh_client_alive_interval`: Keep-alive interval (default: 300)
- `ssh_fail2ban_enabled`: Enable fail2ban protection (default: true)

### User Management
- `ssh_allow_groups`: Groups allowed SSH access (default: ["ssh-users", "sudo", "wheel"])
- `ssh_deny_users`: Users denied SSH access (default: ["root", "guest", "nobody"])
- `ssh_authorized_keys`: List of user SSH keys to deploy
- `ssh_ssh_users`: Users to add to ssh-users group

## Example Usage

```**yaml**
- name: Harden SSH servers
  hosts: servers
  vars:
    ssh_install_server: true
    ssh_port: 2222
    ssh_authorized_keys:
      - name: admin
        key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI..."
        exclusive: true
    ssh_ssh_users:
      - admin
      - deploy
  roles:
    - ssh
```

## Security Features Applied

1. **Protocol Security**: SSH protocol 2 only, modern crypto algorithms
2. **Authentication**: Key-based only, no passwords, strict mode checking
3. **Access Control**: Group-based restrictions, user deny lists
4. **Session Security**: Connection timeouts, session limits
5. **Network Security**: Disabled forwarding, tunneling restrictions
6. **Monitoring**: Fail2ban integration, verbose logging
7. **Legal Protection**: Security banner for unauthorized access warnings

## Testing

The role includes validation tasks that verify:
- SSH configuration syntax
- Service status
- Port connectivity
- Fail2ban jail status

Run with `--check` mode for safe testing before deployment.
