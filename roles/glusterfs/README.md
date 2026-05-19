# GlusterFS Role

## Description

This role installs and configures GlusterFS distributed storage with automatic cluster setup, volume management, and best practices for replica mode deployment.

## Requirements

- Ansible >= 2.15
- Python >= 3.11
- Root or sudo privileges
- Debian/Ubuntu based systems (tested on Ubuntu 20.04+, Debian 10+)
- Minimum 2 nodes for replica mode
- At least 2GB RAM per node
- 10GB free disk space on root partition

## Role Variables

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_cluster_name` | string | `"gluster_cluster"` | Name of GlusterFS cluster |
| `glusterfs_volume_name` | string | `"gv_swarm"` | Name of GlusterFS volume |
| `glusterfs_group_name` | string | `""` (required) | Ansible group containing cluster nodes |

### Installation Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_version` | string | `"latest"` | GlusterFS version to install |
| `glusterfs_install_method` | string | `"package"` | Installation method: package or repository |
| `glusterfs_auto_start` | boolean | `true` | Enable automatic service start |

### Storage Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_brick_dir` | string | `"/data/glusterfs/brick"` | Directory for GlusterFS bricks |
| `glusterfs_mount_dir` | string | `"/mnt/glusterfs"` | Mount point for the volume |
| `glusterfs_replica_count` | integer | `{{ groups[glusterfs_group_name] | length }}` | Number of replicas (auto-set to cluster size) |

### Network Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_bind_interface` | string | `"{{ ansible_default_ipv4.interface }}"` | Network interface for GlusterFS |
| `glusterfs_bind_address` | string | `"{{ hostvars[inventory_hostname]['ansible_' + glusterfs_bind_interface]['ipv4']['address'] }}"` | IP address for GlusterFS |

### Performance Tuning

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_performance_enabled` | boolean | `true` | Enable performance optimizations |
| `glusterfs_volume_options` | dict | See defaults | Volume performance options |

### Security Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `glusterfs_enable_auth` | boolean | `true` | Enable authentication |
| `glusterfs_allow_insecure` | boolean | `false` | Allow insecure connections |
| `glusterfs_firewall_enabled` | boolean | `true` | Configure firewall rules |

## Example Playbook

### Basic Setup

```yaml
---
- name: Deploy GlusterFS Cluster
  hosts: glusterfs_nodes
  become: true
  vars:
    glusterfs_cluster_name: "storage_cluster"
    glusterfs_volume_name: "shared_storage"
    glusterfs_group_name: "glusterfs_nodes"
  roles:
    - glusterfs
```

### Advanced Configuration

```yaml
---
- name: Deploy GlusterFS with Custom Settings
  hosts: glusterfs_nodes
  become: true
  vars:
    glusterfs_cluster_name: "production_storage"
glusterfs_volume_name: "gv_swarm"
    glusterfs_group_name: "glusterfs_nodes"  # Explicit group name
    glusterfs_brick_dir: "/data/glusterfs/brick"
    glusterfs_mount_dir: "/mnt/shared"
    glusterfs_replica_count: 3
    glusterfs_volume_options:
      performance.readdir-ahead: "on"
      performance.read-ahead: "on"
      performance.io-cache: "on"
      performance.quick-read: "on"
      performance.stat-prefetch: "on"
      client.event-threads: "8"
      server.event-threads: "8"
      network.frame-timeout: "1800"
      performance.write-behind: "on"
  roles:
    - glusterfs
```

### Using with Group Variables

You must define variables in `group_vars/your_group.yaml`:

```yaml
# group_vars/swarm_infra.yaml
glusterfs_enabled: true
glusterfs_group_name: "swarm_infra"  # Required: set explicitly
glusterfs_cluster_name: "swarm_storage"
glusterfs_volume_name: "gv_swarm"
glusterfs_mount_dir: "/opt/docker"
```

## Example Inventory

```yaml
# inventory.yaml
glusterfs_nodes:
  hosts:
    gluster-01:
      ansible_host: 192.168.1.10
    gluster-02:
      ansible_host: 192.168.1.11
    gluster-03:
      ansible_host: 192.168.1.12
```

## Tags

- `glusterfs_validate`: Validate configuration and system requirements
- `glusterfs_install`: Install GlusterFS packages and dependencies
- `glusterfs_configure`: Configure GlusterFS service and directories
- `glusterfs_cluster`: Set up cluster peers and volumes
- `glusterfs_firewall`: Configure firewall rules

## Deployment Commands

```bash
# Complete deployment
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs

# Step-by-step deployment
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs_validate
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs_install
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs_configure
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs_cluster

# Reconfigure only
ansible-playbook -i inventory.yaml playbook.yaml --tags glusterfs_cluster
```

## Directory Structure

After deployment, the role creates the following structure:

```
/data/glusterfs/
├── brick/
│   └── gv_swarm/              # GlusterFS brick storage
├── logs/                 # GlusterFS logs
└── config/               # Configuration files

/mnt/glusterfs/           # Mounted GlusterFS volume
/etc/glusterfs/           # GlusterFS configuration
/var/log/glusterfs/       # Service logs
```

## Volume Management

### Check Volume Status

```bash
# Check volume information
gluster volume info

# Check volume status
gluster volume status

# Check peer status
gluster peer status
```

### Manual Volume Operations

```bash
# Create additional volume
gluster volume create data replica 3 \
  gluster-01:/data/glusterfs/brick/data \
  gluster-02:/data/glusterfs/brick/data \
  gluster-03:/data/glusterfs/brick/data

# Start volume
gluster volume start data

# Mount volume
mount -t glusterfs gluster-01:data /mnt/data
```

## Performance Tuning

### Recommended Volume Options

```yaml
glusterfs_volume_options:
  # Read performance
  performance.readdir-ahead: "on"
  performance.read-ahead: "on"
  performance.io-cache: "on"
  performance.quick-read: "on"
  performance.stat-prefetch: "on"
  
  # Thread optimization
  client.event-threads: "8"
  server.event-threads: "8"
  
  # Network optimization
  network.frame-timeout: "1800"
  network.ping-timeout: "42"
  
  # Write performance
  performance.write-behind: "on"
  performance.flush-behind: "on"
```

### System Optimization

```bash
# Add to /etc/sysctl.conf
echo 'vm.dirty_ratio = 15' >> /etc/sysctl.conf
echo 'vm.dirty_background_ratio = 5' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure = 50' >> /etc/sysctl.conf
sysctl -p
```

## Security Considerations

### Firewall Configuration

The role automatically configures firewall rules for GlusterFS:

- TCP 111 (Portmapper)
- UDP 111 (Portmapper)
- TCP 24007 (Gluster Daemon)
- TCP 24008 (Gluster Management)
- TCP 24009 (Gluster Brick)
- TCP 38465-38469 (Gluster Brick Range)
- TCP 49152-49161 (Gluster Brick Range)

### Authentication

- Authentication is enabled by default
- Only trusted network access should be allowed
- Consider using VPN or private networks for cluster communication

## Monitoring and Logging

### Log Locations

- Service logs: `/var/log/glusterfs/`
- Volume logs: `/var/log/glusterfs/bricks/`
- Audit logs: `/var/log/glusterfs/geo-replication/`

### Monitoring Commands

```bash
# Check service status
systemctl status glusterd

# Check cluster health
gluster peer status
gluster volume status

# Monitor volume performance
gluster volume profile gv_swarm start
gluster volume profile gv_swarm info

# Check heal status (for replica volumes)
gluster volume heal gv_swarm info
```

## Troubleshooting

### Common Issues

1. **Peer probe fails**
   - Check network connectivity between nodes
   - Verify firewall rules are configured
   - Ensure DNS resolution works
   - Check time synchronization

2. **Volume creation fails**
   - Verify brick directories exist and have proper permissions
   - Check available disk space
   - Ensure all peers are connected

3. **Mount fails**
   - Check if volume is started: `gluster volume status`
   - Verify network connectivity to GlusterFS servers
   - Check firewall rules on client and server

4. **Performance issues**
   - Enable performance options in volume settings
   - Check network latency between nodes
   - Monitor disk I/O and memory usage

### Debug Commands

```bash
# Enable debug logging
gluster volume set gv_swarm diagnostics.client-log-level DEBUG
gluster volume set gv_swarm diagnostics.brick-log-level DEBUG

# Check logs
tail -f /var/log/glusterfs/glusterd.log
tail -f /var/log/glusterfs/bricks/gv_swarm.log

# Test connectivity
telnet gluster-01 24007
gluster peer status
```

## Backup and Recovery

### Volume Backup

```bash
# Create snapshot
gluster snapshot create snap1 gv_swarm

# List snapshots
gluster snapshot list

# Restore from snapshot
gluster snapshot restore snap1
```

### Configuration Backup

The role automatically backs up configuration files when `glusterfs_backup_config: true`.

## Scaling the Cluster

### Adding New Nodes

1. Add the new node to your inventory
2. Run the role on the new node
3. Probe the new node from an existing cluster member:
   ```bash
   gluster peer probe new-node-ip
   ```
4. Expand volumes if needed (requires volume recreation)

### Removing Nodes

1. Migrate data off the node
2. Remove the node from the cluster:
   ```bash
   gluster peer detach node-ip
   ```

## Integration with Docker

### Using GlusterFS as Docker Volume Driver

```bash
# Install GlusterFS plugin
docker plugin install gluster/glusterfs-volume-plugin

# Create volume
docker volume create -d glusterfs -o opt=gv_swarm my-gluster-volume

# Use volume
docker run -v my-gluster-volume:/data nginx
```

### Docker Swarm Integration

```yaml
version: '3.8'
services:
  app:
    image: nginx
    volumes:
      - glusterfs_data:/usr/share/nginx/html
    deploy:
      replicas: 3

volumes:
  glusterfs_data:
    driver: glusterfs
    driver_opts:
      opt: "gv_swarm"
```

## Best Practices

1. **Network**: Use dedicated network interfaces for GlusterFS traffic
2. **Storage**: Use SSD storage for better performance
3. **Replica count**: Use odd numbers (3, 5) for quorum-based decisions
4. **Monitoring**: Set up monitoring for cluster health and performance
5. **Backup**: Regularly backup important data and configuration
6. **Testing**: Test failover scenarios in non-production environment

## License

MIT

## Author Information

This role was created for the homelab infrastructure project following 2025 Ansible best practices.