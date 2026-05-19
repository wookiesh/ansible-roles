# Docker Host Role
# 
# This role installs and configures Docker on host systems, including Docker Engine
# and Docker Compose for containerized services.

## Requirements
- Ansible >= 2.15
- Python >= 3.11
- Root or sudo privileges
- Debian/Ubuntu based systems (tested on Ubuntu 20.04+, Debian 10+)
- Docker SDK for Python (automatically installed by the role)

## Role Variables

### Docker Installation
- `docker_host_install_method`: Installation method - script or repository (default: "script")
- `docker_host_version`: Docker version to install (default: "latest")
- `docker_host_auto_update`: Allow automatic updates (default: false)

### Docker Configuration
- `docker_host_user`: User to add to docker group (default: "{{ admin_user_name }}")
- `docker_host_add_user_to_group`: Add user to docker group (default: true)
- `docker_host_daemon_config`: Docker daemon configuration (see defaults)
- `docker_host_systemd_override`: Create systemd override (default: true)

**Note**: The role performs a single Docker daemon restart after all configuration changes to ensure stability.

### Docker Compose
- `docker_host_compose_install`: Install Docker Compose (default: true)
- `docker_host_compose_install_method`: plugin or standalone (default: "plugin")
- `docker_host_compose_version`: Compose version (default: "latest")

### Container Management
- `docker_host_services_root`: Root directory for services (default: "/opt/docker")
- `docker_host_services_group`: Group for service directories (default: "docker")
- `docker_host_auto_start_containers`: Auto-start containers (default: false)



## Dependencies
- `admin_user` role (for docker user configuration)

## Example Playbook

```yaml
- hosts: swarm_nodes
  roles:
    - role: docker_host
```

## Example Inventory

```yaml
docker_hosts:
  hosts:
    web01:
      ansible_host: 192.168.1.10
    db01:
      ansible_host: 192.168.1.11
```

## Tags
- `docker_install`: Docker engine installation
- `docker_compose`: Docker Compose installation
- `docker_config`: Docker daemon configuration
- `docker_users`: Docker user management
- `docker_swarm`: Docker Swarm setup (includes init, join, configure, validate)
- `swarm_init`: Swarm cluster initialization
- `swarm_join`: Node joining operations
- `swarm_configure`: Node configuration and labeling
- `swarm_validate`: Cluster validation and health checks

## Features Status
- [x] Docker Engine installation (official script)
- [x] Docker Compose installation
- [x] User and group management
- [x] Docker daemon configuration
- [x] Systemd service optimization
- [x] Network and volume management
- [x] Security hardening
- [x] **Single daemon restart for stability**
- [x] **Sequential Swarm initialization**
- [x] **Automatic dependency management (Python SDK)**
- [ ] Container auto-start management
- [ ] Backup and restore utilities

## Integration with Traefik
For reverse proxy functionality, use the separate `traefik` role:

```yaml
- hosts: docker_hosts
  roles:
    - role: docker_host
    - role: traefik
      vars:
        traefik_enabled: true
        traefik_domain: "traefik.example.com"
```

## Security Notes
- Services run with `no-new-privileges:true`
- Only expose necessary ports
- Use environment variables for sensitive data
- Regularly update Docker versions

## Directory Structure
```
/opt/docker/
├── shared/
│   ├── networks/
│   └── volumes/
└── services/
    └── [application directories]
```

## License
BSD

## Author Information
This role was created for the homelab infrastructure project.
### Docker Swarm Configuration
- `docker_host_swarm_enabled`: Enable Docker Swarm functionality (default: false)
- `docker_host_swarm_role`: Node role - "worker" or "manager" (default: "worker")
- `docker_host_swarm_advertise_addr`: Address advertised to other nodes (default: "{{ ansible_host }}")
- `docker_host_swarm_listen_addr`: Listen address for Swarm traffic (default: "0.0.0.0:2377")
- `docker_host_swarm_default_addr_pool`: Default address pool for overlay networks (default: "10.250.0.0/16")
- `docker_host_swarm_subnet_size`: Subnet size for networks (default: "24")
- `docker_host_swarm_node_labels`: Custom labels for the node (default: {})
- `docker_host_swarm_heartbeat_period`: Node heartbeat period (default: "30s")
- `docker_host_swarm_election_tick`: Election timeout in ticks (default: 10)
- `docker_host_swarm_snapshot_interval`: Raft snapshot interval (default: 10000)
- `docker_host_swarm_keepalive_old`: Keepalive timeout for old nodes (default: "60s")
- `docker_host_swarm_log_entries_for_slow_follower`: Log entries limit (default: 500)
- `docker_host_swarm_heartbeat_tick`: Heartbeat tick interval (default: 1)

**Note**: Advanced Swarm parameters are applied after cluster initialization to ensure stability.

## Swarm Usage Example

```yaml
# inventory/hosts.yaml
swarm_cluster:
  vars:
    docker_host_swarm_enabled: true
    docker_host_swarm_default_addr_pool: "10.250.0.0/16"
  hosts:
    manager-01:
      docker_host_swarm_role: "manager"
      docker_host_swarm_node_labels:
        role: "manager"
        priority: "primary"
    worker-01:
      docker_host_swarm_role: "worker"
      docker_host_swarm_node_labels:
        role: "worker"
        workload: "general"
```

## Swarm Deployment

```bash
# Deploy complete Docker and Swarm setup
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags docker

# Deploy only Swarm components (after Docker is installed)
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags docker_swarm

# Initialize cluster (first manager only)
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags swarm_init

# Join nodes to cluster
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags swarm_join

# Configure nodes
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags swarm_configure

# Validate cluster
ansible-playbook -i inventory/hosts.yaml infrastructure.yaml --tags swarm_validate
```

**Important**: The role now performs sequential Swarm initialization to avoid race conditions and ensure cluster stability.

## Swarm Features Status
- [x] Docker Engine installation (official script)
- [x] Docker Compose installation
- [x] User and group management
- [x] Docker daemon configuration
- [x] Systemd service optimization
- [x] Network and volume management
- [x] Security hardening
- [x] **Docker Swarm initialization**
- [x] **Docker Swarm node management**
- [x] **Docker Swarm configuration**
- [x] **Docker Swarm validation**
- [ ] Container auto-start management
- [ ] Backup and restore utilities

## Integration with Docker Swarm

For Docker Swarm functionality, this role now supports:
- Automatic cluster initialization
- Node role assignment (manager/worker)
- Token-based node joining
- Node labeling and configuration
- Cluster validation and health checks
- Overlay network management (RFC1918 compliant)

## Security Notes

- Docker Swarm management traffic is always encrypted
- Application data traffic encryption optional per network
- Node certificates automatically managed
- Join tokens should be treated as secrets
- Regularly update Docker versions for Swarm security

## Troubleshooting

### Common Issues

**Swarm initialization fails:**
- Ensure Docker daemon is running: `systemctl status docker`
- Check network connectivity between nodes
- Verify firewall allows ports 2377, 7946, 4789
- Use `--tags docker_swarm --start-at-task "Initialize Swarm on first manager"`

**Nodes cannot join Swarm:**
- Verify tokens are valid and not expired
- Check `docker_host_swarm_advertise_addr` configuration
- Ensure manager is stable before joining workers
- Use `docker swarm leave` to clean up failed joins

**Configuration conflicts:**
- Avoid `live-restore` with Swarm (not compatible)
- Use `userland-proxy: false` for better performance
- Restart Docker daemon only once after all configuration changes

### Debug Commands

```bash
# Check Swarm status
docker node ls

# Check Swarm info
docker info | grep -A 10 "Swarm:"

# Check daemon logs
journalctl -u docker.service -f

# Validate configuration
docker swarm init --dry-run
```

## License
MIT

## Author Information
This role was created for the homelab infrastructure project with Docker Swarm support.
