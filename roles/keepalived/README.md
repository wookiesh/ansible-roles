# Keepalived Role

A comprehensive Ansible role for deploying and managing Keepalived high availability and load balancing solutions with 2025 best practices.

## Features

- **High Availability**: VRRP protocol implementation for automatic failover
- **Load Balancing**: LVS (Linux Virtual Server) integration for traffic distribution
- **Health Monitoring**: Customizable health check scripts and monitoring
- **Security**: Authentication, non-root execution, and firewall integration
- **Monitoring**: Built-in metrics collection and status reporting
- **Multi-Platform**: Support for Ubuntu, Debian, RedHat, CentOS, and Rocky Linux
- **Idempotent**: Safe to run multiple times without side effects

## Requirements

- Ansible >= 2.15
- Python >= 3.11
- Root or sudo privileges
- Supported OS: Ubuntu 20.04+, Debian 10+, RHEL 8+, CentOS 8+, Rocky 8+

## Role Variables

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `keepalived_enabled` | boolean | `false` | Enable keepalived installation and configuration |
| `keepalived_install_method` | string | `"package"` | Installation method: `package` or `source` |
| `keepalived_version` | string | `"latest"` | Keepalived version to install |
| `keepalived_interface` | string | `"eth0"` | Network interface for VRRP |
| `keepalived_router_id` | string | `"{{ inventory_hostname_short }}"` | Unique router identifier |
| `keepalived_priority` | integer | `100` | VRRP priority (1-255, higher = preferred master) |

### VRRP Configuration

```yaml
keepalived_vrrp_instances:
  - name: "VI_1"
    state: "MASTER"  # MASTER, BACKUP, or FAULT
    interface: "{{ keepalived_interface }}"
    virtual_router_id: 51
    priority: "{{ keepalived_priority }}"
    advert_int: 1
    authentication:
      auth_type: "PASS"
      auth_pass: "{{ vault_keepalived_auth_pass }}"
    virtual_ipaddress:
      - "192.168.1.100/24 dev {{ keepalived_interface }}"
    track_scripts:
      - "check_haproxy"
    track_interfaces:
      - "{{ keepalived_interface }}"
```

### Load Balancing Configuration

```yaml
keepalived_virtual_servers:
  - delay_loop: 6
    lb_algo: "rr"  # rr, wrr, lc, wlc, sh, dh, lblc
    lb_kind: "NAT"  # NAT, DR, TUN
    persistence_timeout: 50
    protocol: "TCP"
    virtual_server: "192.168.1.100 80"
    real_server:
      - "192.168.1.101 80"
      - "192.168.1.102 80"
```

### Health Check Scripts

```yaml
keepalived_track_scripts:
  - name: "check_haproxy"
    script: "/usr/local/bin/check_haproxy.sh"
    interval: 2
    weight: -20
    fall: 3
    rise: 2
```

### Custom Scripts

```yaml
keepalived_custom_scripts:
  - name: "check_service.sh"
    content: |
      #!/bin/bash
      systemctl is-active nginx >/dev/null 2>&1
    mode: "0755"
```

### Monitoring and Metrics

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `keepalived_metrics_enabled` | boolean | `false` | Enable metrics collection |
| `keepalived_stats_socket` | string | `"/etc/keepalived/stats.sock"` | Statistics socket path |
| `keepalived_log_level` | string | `"INFO"` | Log level: DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL |

### Email Notifications

```yaml
keepalived_email_enabled: true
keepalived_email_from: "keepalived@{{ ansible_domain }}"
keepalived_email_to:
  - "admin@example.com"
  - "ops@example.com"
keepalived_email_smtp_server: "smtp.example.com"
keepalived_email_smtp_port: 587
keepalived_email_smtp_username: "keepalived@example.com"
keepalived_email_smtp_password: "{{ vault_keepalived_smtp_password }}"
keepalived_email_smtp_tls: true
```

### Security Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `keepalived_user` | string | `"root"` | User to run keepalived as |
| `keepalived_group` | string | `"root"` | Group to run keepalived as |
| `keepalived_enable_non_root` | boolean | `false` | Enable non-root execution |
| `keepalived_drop_capabilities` | boolean | `true` | Drop capabilities for security |

## Example Playbook

### Basic High Availability Setup

```yaml
---
- name: Configure Keepalived High Availability
  hosts: load_balancers
  become: true
  vars:
    keepalived_enabled: true
    keepalived_interface: "eth0"
    keepalived_vrrp_instances:
      - name: "VI_WEB"
        state: "{{ 'MASTER' if inventory_hostname == 'lb01' else 'BACKUP' }}"
        interface: "{{ keepalived_interface }}"
        virtual_router_id: 51
        priority: "{{ 150 if inventory_hostname == 'lb01' else 100 }}"
        advert_int: 1
        authentication:
          auth_type: "PASS"
          auth_pass: "{{ vault_keepalived_auth_pass }}"
        virtual_ipaddress:
          - "192.168.1.100/24 dev {{ keepalived_interface }}"
        track_scripts:
          - "check_nginx"
    keepalived_track_scripts:
      - name: "check_nginx"
        script: "/usr/local/bin/check_nginx.sh"
        interval: 2
        weight: -20
        fall: 3
        rise: 2
    keepalived_custom_scripts:
      - name: "check_nginx.sh"
        content: |
          #!/bin/bash
          # Check if nginx is responding
          curl -f http://localhost:80/health >/dev/null 2>&1
        mode: "0755"
  roles:
    - keepalived
```

### Load Balancing Setup

```yaml
---
- name: Configure Keepalived Load Balancer
  hosts: load_balancers
  become: true
  vars:
    keepalived_enabled: true
    keepalived_vrrp_instances:
      - name: "VI_LB"
        state: "{{ 'MASTER' if inventory_hostname == 'lb01' else 'BACKUP' }}"
        interface: "eth0"
        virtual_router_id: 52
        priority: "{{ 150 if inventory_hostname == 'lb01' else 100 }}"
        virtual_ipaddress:
          - "10.0.0.100/24 dev eth0"
        authentication:
          auth_type: "PASS"
          auth_pass: "{{ vault_keepalived_auth_pass }}"
    keepalived_virtual_servers:
      - delay_loop: 6
        lb_algo: "wrr"
        lb_kind: "DR"
        persistence_timeout: 300
        protocol: "TCP"
        virtual_server: "10.0.0.100 80"
        real_server:
          - "10.0.0.101 80"
          - "10.0.0.102 80"
          - "10.0.0.103 80"
  roles:
    - keepalived
```

## Advanced Configuration

### Multi-VRRP Instance Setup

```yaml
keepalived_vrrp_instances:
  # Web services VIP
  - name: "VI_WEB"
    state: "MASTER"
    interface: "eth0"
    virtual_router_id: 51
    priority: 150
    virtual_ipaddress:
      - "192.168.1.100/24 dev eth0"
    track_scripts:
      - "check_nginx"
  
  # Database services VIP
  - name: "VI_DB"
    state: "BACKUP"
    interface: "eth0"
    virtual_router_id: 52
    priority: 100
    virtual_ipaddress:
      - "192.168.1.101/24 dev eth0"
    track_scripts:
      - "check_mysql"
```

### Unicast Configuration

```yaml
keepalived_vrrp_instances:
  - name: "VI_UNICAST"
    state: "MASTER"
    interface: "eth0"
    virtual_router_id: 53
    priority: 150
    unicast_peer:
      - "192.168.1.11"
      - "192.168.1.12"
    virtual_ipaddress:
      - "192.168.1.200/24 dev eth0"
```

### Custom Notification Scripts

```yaml
keepalived_notify_scripts:
  - name: "notify_master"
    script: "/usr/local/bin/notify_master.sh"
  - name: "notify_backup"
    script: "/usr/local/bin/notify_backup.sh"
  - name: "notify_fault"
    script: "/usr/local/bin/notify_fault.sh"
```

## Monitoring and Troubleshooting

### Status Commands

```bash
# Check service status
systemctl status keepalived

# View VRRP status
keepalived --dump-data

# Check configuration syntax
keepalived --test --config-file /etc/keepalived/keepalived.conf

# View logs
journalctl -u keepalived -f

# Use built-in status script
/usr/local/bin/keepalived-status

# Get metrics
/usr/local/bin/monitor-keepalived
/usr/local/bin/monitor-keepalived --prometheus
```

### Common Issues

1. **Virtual IP not appearing**
   - Check interface configuration
   - Verify sysctl parameters: `net.ipv4.ip_nonlocal_bind=1`
   - Check firewall rules for VRRP (protocol 112)

2. **Authentication failures**
   - Ensure auth_pass is the same on all nodes
   - Use vault variables for passwords
   - Verify auth_type matches between nodes

3. **Health check failures**
   - Test scripts manually
   - Check script permissions (755)
   - Verify script paths are correct

## Security Considerations

- Use strong authentication passwords (store in vault)
- Enable script security with `enable_script_security`
- Consider non-root execution for production
- Configure firewall rules for VRRP traffic
- Monitor logs for authentication failures

## Integration with Other Roles

### With Docker/Traefik

```yaml
- hosts: docker_hosts
  roles:
    - role: docker_host
    - role: traefik
    - role: keepalived
      vars:
        keepalived_enabled: true
        keepalived_vrrp_instances:
          - name: "VI_TRAEFIK"
            state: "{{ 'MASTER' if inventory_hostname == 'docker01' else 'BACKUP' }}"
            virtual_ipaddress:
              - "10.0.0.50/24 dev eth0"
            track_scripts:
              - "check_traefik"
        keepalived_track_scripts:
          - name: "check_traefik"
            script: "curl -f http://localhost:8080/ping"
            interval: 2
```

## Testing

### Idempotence Testing

```bash
# Run playbook twice - second run should show no changes
ansible-playbook -i inventory.yaml playbook.yaml
ansible-playbook -i inventory.yaml playbook.yaml

# Check mode
ansible-playbook -i inventory.yaml playbook.yaml --check

# Syntax check
ansible-playbook -i inventory.yaml playbook.yaml --syntax-check
```

### Failover Testing

```bash
# Test failover by stopping keepalived on master
systemctl stop keepalived

# Verify VIP moves to backup
ip addr show

# Restart master service
systemctl start keepalived
```

## Performance Tuning

### System Parameters

```yaml
keepalived_sysctl_params:
  - name: "net.ipv4.ip_nonlocal_bind"
    value: 1
  - name: "net.core.rmem_max"
    value: 16777216
  - name: "net.core.wmem_max"
    value: 16777216
```

### Keepalived Optimization

```yaml
keepalived_global_defs:
  router_id: "{{ keepalived_router_id }}"
  script_user: "{{ keepalived_user }}"
  enable_script_security: true
  max_auto_priority: 20
  min_auto_priority: 1
```

## Backup and Recovery

### Configuration Backup

```yaml
keepalived_config_backup: true
```

### Manual Backup

```bash
# Backup configuration
cp /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.backup

# Export running configuration
keepalived --dump-data > /root/keepalived-state.txt
```

## License

MIT License

## Author Information

This role was created for the homelab infrastructure project following 2025 Ansible best practices.

## Contributing

Please follow the contribution guidelines in the project's CONTRIBUTING.md file. All changes must maintain idempotence and pass the validation tests.