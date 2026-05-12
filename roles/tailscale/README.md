# Role: Tailscale VPN

## Description

This role installs and configures Tailscale VPN with 2025 best practices, providing secure mesh networking capabilities for your homelab infrastructure. It supports multiple authentication methods, advanced networking configurations, and comprehensive security hardening.

## Features

- **Multiple Installation Methods**: Repository, script, or package-based installation
- **Flexible Authentication**: Auth key, OAuth, or interactive authentication
- **Smart Authentication**: Only authenticates if not already connected to tailnet
- **Advanced Networking**: Exit nodes, subnet routing, and firewall configuration
- **Security Hardening**: Proper file permissions, firewall rules, and audit logging
- **Idempotent Operations**: Safe to run multiple times without side effects
- **Comprehensive Monitoring**: Health checks and status reporting
- **2025 Best Practices**: FQCN modules, proper validation, and error handling

## Requirements

- Ansible 2.15+
- Python 3.11+
- Root or sudo privileges
- Internet connectivity for package installation
- Valid Tailscale account and authentication credentials

## Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_enabled` | boolean | `true` | Enable or disable Tailscale installation |
| `tailscale_version` | string | `"latest"` | Tailscale version to install |
| `tailscale_install_method` | string | `"repository"` | Installation method: `repository`, `script`, `package` |
| `tailscale_auth_method` | string | `"authkey"` | Authentication method: `authkey`, `oauth`, `interactive` |

### Authentication

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_auth_key` | string | `""` | Tailscale authentication key (from vault) |
| `tailscale_oauth_client_id` | string | `""` | OAuth client ID for authentication |
| `tailscale_oauth_client_secret` | string | `""` | OAuth client secret (from vault) |
| `tailscale_auth_timeout` | int | `300` | Authentication timeout in seconds |
| `tailscale_force_reauth` | boolean | `false` | Force re-authentication even if already connected |

### Network Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_advertise_routes` | list | `[]` | Routes to advertise to Tailscale network |
| `tailscale_accept_routes` | boolean | `true` | Accept routes from other nodes |
| `tailscale_advertise_exit_node` | boolean | `false` | Advertise as exit node |
| `tailscale_accept_dns` | boolean | `true` | Accept DNS configuration |
| `tailscale_force_dns` | boolean | `true` | Force DNS settings |
| `tailscale_exit_node` | string | `""` | Use specific exit node |
| `tailscale_exit_node_allow_lan_access` | boolean | `false` | Allow LAN access via exit node |

### Security and Tags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_tags` | list | `[]` | Tags to apply to this node |
| `tailscale_force_reauth` | boolean | `false` | Force re-authentication |
| `tailscale_reset` | boolean | `false` | Reset Tailscale configuration |
| `tailscale_configure_firewall` | boolean | `true` | Configure firewall rules |

### Service Management

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_service_enabled` | boolean | `true` | Enable Tailscale service |
| `tailscale_service_state` | string | `"started"` | Service state: `started`, `stopped` |
| `tailscale_auto_update` | boolean | `false` | Enable automatic updates |
| `tailscale_restart_on_config_change` | boolean | `true` | Restart on configuration changes |

### Logging and Monitoring

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_log_level` | string | `"info"` | Log level: `debug`, `info`, `warn`, `error` |
| `tailscale_debug_mode` | boolean | `false` | Enable debug mode |
| `tailscale_health_check_enabled` | boolean | `true` | Enable health checks |
| `tailscale_health_check_interval` | int | `30` | Health check interval in seconds |

### Paths and Permissions

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `tailscale_config_dir` | string | `"/etc/tailscale"` | Configuration directory |
| `tailscale_state_dir` | string | `"/var/lib/tailscale"` | State directory |
| `tailscale_log_dir` | string | `"/var/log/tailscale"` | Log directory |
| `tailscale_file_permissions` | string | `"0644"` | File permissions |
| `tailscale_dir_permissions` | string | `"0755"` | Directory permissions |

## Example Playbook

### Basic Installation

```yaml
- hosts: servers
  become: true
  vars:
    tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
  roles:
    - tailscale
```

### Advanced Configuration

```yaml
- hosts: servers
  become: true
  vars:
    tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
    tailscale_advertise_routes:
      - "192.168.1.0/24"
      - "10.0.0.0/8"
    tailscale_tags:
      - "tag:server"
      - "tag:homelab"
    tailscale_advertise_exit_node: true
    tailscale_log_level: "debug"
    tailscale_configure_firewall: true
  roles:
    - tailscale
```

### Exit Node Configuration

```yaml
- hosts: exit_nodes
  become: true
  vars:
    tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
    tailscale_advertise_exit_node: true
    tailscale_advertise_routes:
      - "192.168.1.0/24"
    tailscale_tags:
      - "tag:exit-node"
    tailscale_exit_node_allow_lan_access: true
  roles:
    - tailscale
```

### Client Configuration

```yaml
- hosts: clients
  become: true
  vars:
    tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
    tailscale_exit_node: "exit-node-server"
    tailscale_accept_dns: true
    tailscale_force_dns: true
  roles:
    - tailscale
```

## Vault Configuration

Add the following to your `secrets/vault.yml`:

```yaml
vault_tailscale_auth_key: "tskey-auth-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
vault_tailscale_oauth_client_id: "your-oauth-client-id"
vault_tailscale_oauth_client_secret: "your-oauth-client-secret"
```

## Installation Methods

### Repository (Recommended)

Uses official Tailscale repositories for package management:

```yaml
tailscale_install_method: "repository"
tailscale_repository_enabled: true
```

### Script Installation

Uses the official Tailscale installation script:

```yaml
tailscale_install_method: "script"
```

### Package Installation

Uses system package manager without adding repositories:

```yaml
tailscale_install_method: "package"
```

## Authentication Methods

### Auth Key (Recommended)

Generate an auth key from the [Tailscale admin console](https://login.tailscale.com/admin/authkeys):

```yaml
tailscale_auth_method: "authkey"
tailscale_auth_key: "{{ vault_tailscale_auth_key }}"
```

### OAuth Authentication

Configure OAuth in the Tailscale admin console:

```yaml
tailscale_auth_method: "oauth"
tailscale_oauth_client_id: "{{ vault_tailscale_oauth_client_id }}"
tailscale_oauth_client_secret: "{{ vault_tailscale_oauth_client_secret }}"
```

### Interactive Authentication

Requires manual authentication on the target machine:

```yaml
tailscale_auth_method: "interactive"
```

## Firewall Configuration

The role automatically configures firewall rules when `tailscale_configure_firewall: true`:

- **UFW**: Automatically configures UFW rules on Ubuntu/Debian
- **iptables**: Configures iptables rules on other systems
- **Exit Node**: Sets up NAT and IP forwarding for exit nodes

## Testing

### Syntax Check

```bash
ansible-playbook roles/tailscale/tests/test.yml --syntax-check
```

### Dry Run

```bash
ansible-playbook roles/tailscale/tests/test.yml --check
```

### Idempotence Test

```bash
ansible-playbook roles/tailscale/tests/test.yml
ansible-playbook roles/tailscale/tests/test.yml  # Should show no changes
```

### Full Test

```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --limit test_host --tags tailscale
```

## Troubleshooting

### Common Issues

1. **Authentication Fails**
   - Verify auth key is valid and not expired
   - Check network connectivity to Tailscale control plane
   - Ensure proper permissions for Tailscale service
   - Set `tailscale_force_reauth: true` to force re-authentication

2. **Service Won't Start**
   - Check system logs: `journalctl -u tailscaled`
   - Verify configuration file syntax
   - Ensure proper file permissions

3. **Network Connectivity Issues**
   - Verify firewall rules allow Tailscale traffic
   - Check UDP port 41641 is open
   - Verify DNS configuration

4. **Already Connected Issues**
   - The role automatically detects if already connected to tailnet
   - Authentication is skipped if node is already authenticated and online
   - Use `tailscale_force_reauth: true` to force re-authentication

### Debug Mode

Enable debug mode for detailed logging:

```yaml
tailscale_debug_mode: true
tailscale_log_level: "debug"
```

### Status Commands

```bash
# Check Tailscale status
tailscale status

# Check service status
systemctl status tailscaled

# View logs
journalctl -u tailscaled -f
```

## Security Considerations

- **Auth Keys**: Store auth keys in Ansible vault
- **Firewall**: Configure firewall rules properly
- **Exit Nodes**: Understand security implications of exit nodes
- **Subnet Routing**: Only advertise necessary routes
- **Tags**: Use tags to enforce ACL policies

## Performance Tuning

### Network Mode

```yaml
tailscale_network_mode: "kernel"  # Better performance, requires kernel module
```

### MTU Configuration

```yaml
tailscale_mtu: 1420  # Adjust for your network
```

### Keepalive Settings

```yaml
tailscale_heartbeat_interval: 60
tailscale_keepalive_interval: 25
```

## Integration with Other Roles

This role integrates well with:

- **server**: Base system configuration
- **ssh**: Secure remote access
- **docker_host**: Container networking
- **firewall**: Advanced firewall rules

## Contributing

Please follow the contributing guidelines in [CONTRIBUTING.md](../../CONTRIBUTING.md) and role development standards in [docs/ROLE_DEVELOPMENT.md](../../docs/ROLE_DEVELOPMENT.md).

## License

This role is licensed under the MIT License - see the [LICENSE](../../LICENSE) file for details.

## Changelog

### v2.0.0
- Complete rewrite with 2025 best practices
- Added comprehensive variable validation
- Implemented idempotent operations
- Added support for multiple authentication methods
- Enhanced security and firewall configuration
- Added comprehensive testing and documentation

### v1.0.0
- Initial basic implementation