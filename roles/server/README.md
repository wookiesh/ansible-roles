---
# Server Role
# 
# This role configures basic server settings including hostname management,
# automatic updates, and optional security hardening.

## Requirements
- Ansible >= 2.9
- Root or sudo privileges
- Debian/Ubuntu based systems (tested on Ubuntu 20.04+, Debian 10+)

## Role Variables

### Hostname Management
- `server_hostname_manage`: Enable hostname management (default: true)
- `server_hostname_update_hosts`: Update /etc/hosts (default: true)
- `server_hostname_fqdn`: Fully qualified domain name (auto-generated from `inventory_hostname`)

### Automatic Updates
- `server_automatic_updates_enabled`: Enable unattended upgrades (default: true)
- `server_auto_update_config_file`: Path to config file (default: `/etc/apt/apt.conf.d/20auto-upgrades`)

### Apticron Notifications
- `server_apticron_enabled`: Enable apticron notifications (default: true)
- `server_apticron_email`: Email for notifications (default: root)



### Journald
- `server_journald_max_use`: Max disk space for journal logs (default: `200M`)

### Performance Tuning
- `server_performance_tuning_enabled`: Enable performance tuning (default: false)
- `server_performance_swappiness`: Swappiness value (default: 10)

## Dependencies
None

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: server
      vars:
        server_automatic_updates_enabled: true
        server_performance_tuning_enabled: true
```

## Example Inventory

```yaml
servers:
  hosts:
    web01.example.com:
      ansible_host: 192.168.1.10
      server_performance_tuning_enabled: true
```

## Tags
- `server_hostname`: Hostname management tasks
- `server_updates`: Automatic updates configuration
- `server_performance`: Performance tuning tasks

## Features Status
- [x] Hostname management
- [x] Unattended upgrades
- [x] Apticron notifications
- [x] Performance tuning (swappiness)
- [x] APT periodic cleanup
- [x] Journald size limit
- [ ] MOTD information
- [ ] Log rotation configuration
- [ ] Time synchronization (chrony)

## License
BSD

## Author Information
This role was created for the homelab infrastructure project.