# Traefik Role

## Description

This role deploys and configures Traefik as a reverse proxy for Docker containers. It supports both Docker Compose and Docker Swarm deployment modes, providing automatic SSL certificate management through Let's Encrypt, dashboard monitoring, and dynamic service discovery.

## Requirements

- Ansible >= 2.15
- Docker Engine installed (use `docker_host` role)
- Root or sudo privileges
- Cloudflare DNS API token for SSL certificates
- Debian/Ubuntu based systems (tested on Ubuntu 20.04+, Debian 10+)

## Dependencies

- `docker_host` role (for Docker installation and service structure)

## Deployment Modes

### Docker Compose Mode (Default)
- Single-host deployment
- Bridge networking
- Simple container management
- Use `traefik_deployment_mode: "compose"`

### Docker Swarm Mode
- Multi-host high availability
- Overlay networking
- Service replication and load balancing
- Automatic failover and rolling updates
- Use `traefik_deployment_mode: "swarm"`

## Role Variables

### Main Configuration
- `traefik_version`: Traefik version to deploy (default: "v3.6.2")
- `traefik_domain`: Main domain for Traefik dashboard (default: "{{ vault_traefik_domain }}")
- `traefik_deployment_mode`: Deployment mode - "compose" or "swarm" (auto-detected based on Docker Swarm)

### Configuration Approach

This role uses a variable-based configuration approach for both static and dynamic Traefik configurations:

#### Static Configuration
The static configuration is controlled by `traefik_static_config` variable and includes:
- Entry points and ports
- Providers (Docker, file)
- Certificate resolvers
- API and dashboard settings
- Metrics and logging
- Security settings

You can override any static configuration setting:

```yaml
traefik_static_config:
  log:
    level: "DEBUG"
  entryPoints:
    web:
      address: ":8080"
  api:
    dashboard: false
  providers:
    docker:
      exposedByDefault: true
```

#### Dynamic Configuration  
The dynamic configuration is controlled by `traefik_dynamic_config` variable and includes:
- Routers and services
- Middlewares
- Custom service definitions

Example:
```yaml
traefik_dynamic_config:
  http:
    routers:
      myrouter:
        rule: "Host(`example.com`)"
        service: myservice
    services:
      myservice:
        loadBalancer:
          servers:
            - url: "http://backend:80"
```

### Docker Integration
- `traefik_docker_services_root`: Docker services root directory (default: "{{ docker_host_services_root }}")
- `traefik_docker_services_group`: Docker services group (default: "{{ docker_host_services_group }}")
- `traefik_install_dir`: Traefik installation directory (default: "{{ traefik_docker_services_root }}/traefik")
- `traefik_compose_file`: Compose file path (default: "{{ traefik_install_dir }}/compose.yaml")
- `traefik_swarm_file`: Swarm stack file path (default: "{{ traefik_install_dir }}/swarm.yaml")

### Network Configuration
- `traefik_network_name`: Docker network name (default: "traefik_public")
- `traefik_network_external`: Use external network (default: true)
- `traefik_network_driver`: Network driver (auto-detected: bridge/overlay)
- `traefik_network_attachable`: Network attachable (default: true for Swarm)

### Port Configuration
- `traefik_port_mode`: Port binding mode - "host" or "ingress" (default: "ingress")
  - "host": Direct port binding (80:80, 443:443, etc.)
  - "ingress": Dynamic port binding (Traefik-managed ports)

### Ports Configuration
- `traefik_http_port`: HTTP port (default: 80)
- `traefik_https_port`: HTTPS port (default: 443)
- `traefik_mqtts_port`: MQTT over TLS port (default: 8883)
- `traefik_metrics_port`: Metrics port (default: 8899)

### Features
- `traefik_whoami_enabled`: Enable whoami test service (default: true)
- `traefik_visualizer_enabled`: Enable Traefik visualizer service (default: false)
- `traefik_visualizer_domain`: Domain for visualizer service (default: "visualizer.{{ traefik_domain | regex_replace('^traefik\\.', '') }}")



### Access Log File (opt-in)

By default Traefik logs to stdout. To enable structured JSON access logs to a file (required for Alloy/Loki integration):

**1. Set the log path in your host_vars:**
```yaml
traefik_access_log_path: "/var/log/traefik"
```

> **Important (Swarm + GlusterFS):** use a **local** path (e.g. `/var/log/traefik`), not a path under a shared filesystem like GlusterFS. Each node runs its own Traefik instance and must write to its own log file independently.

This single variable enables:
- Host directory creation at the specified path
- Bind mount into the container (same path inside and outside)
- Logrotate configuration at `/etc/logrotate.d/traefik`

**2. Add `accessLog` to your `traefik_static_config`:**
```yaml
traefik_static_config:
  accessLog:
    filePath: "{{ traefik_access_log_path }}/access.log"
    format: json
```

Logrotate uses `copytruncate` — no signal to the container needed.

**Logrotate defaults** (override in host_vars as needed):
- `traefik_log_rotate_frequency`: `daily`
- `traefik_log_rotate_keep`: `7`
- `traefik_log_rotate_maxsize`: `100M`

### Swarm Configuration (when traefik_deployment_mode == "swarm")
- `traefik_swarm_mode`: Deployment mode - "replicated" or "global" (default: "replicated")
- `traefik_swarm_replicas`: Number of replicas (default: 2)
- `traefik_swarm_placement_constraints`: Placement constraints list (default: [])
- `traefik_swarm_placement_preferences`: Placement preferences list (default: [])
- `traefik_swarm_update_config`: Update configuration (see defaults for full structure)
- `traefik_swarm_restart_policy`: Restart policy (see defaults for full structure)
- `traefik_swarm_resources`: Resource limits and reservations (see defaults for full structure)

## Example Playbook

### Docker Compose Mode
```yaml
- hosts: dns_servers
  roles:
    - role: traefik
      vars:
        traefik_domain: "traefik.example.com"
```

### Docker Swarm Mode
```yaml
- hosts: swarm_managers
  roles:
    - role: traefik
      vars:
        traefik_deployment_mode: "swarm"
        traefik_swarm_mode: "replicated"
        traefik_swarm_replicas: 3
        traefik_swarm_placement_constraints:
          - "node.role == manager"
        traefik_domain: "traefik.example.com"
```

### Port Mode Configuration

#### Host Mode (Direct Port Binding)
```yaml
- hosts: swarm_managers
  roles:
    - role: traefik
      vars:
        traefik_port_mode: "host"
        traefik_domain: "traefik.example.com"
```

#### Ingress Mode (Default)
```yaml
- hosts: swarm_managers
  roles:
    - role: traefik
      vars:
        traefik_port_mode: "ingress"
        traefik_domain: "traefik.example.com"
```

### Global Mode (One Traefik per Swarm Node)
```yaml
- hosts: swarm_managers
  become: true
  roles:
    - role: traefik
      vars:
        traefik_enabled: true
        traefik_deployment_mode: "swarm"
        traefik_swarm_mode: "global"
        traefik_domain: "traefik.example.com"
```

## Example Inventory

### Docker Compose Mode
```yaml
web_servers:
  hosts:
    web01:
      ansible_host: 192.168.1.10
      traefik_domain: "traefik.example.com"
    web02:
      ansible_host: 192.168.1.11
      traefik_domain: "traefik.example.com"
```

### Docker Swarm Mode
```yaml
swarm_managers:
  hosts:
    manager01:
      ansible_host: 10.0.1.10
      docker_host_swarm_role: "manager"
      traefik_deployment_mode: "swarm"
      traefik_domain: "traefik.example.com"
    manager02:
      ansible_host: 10.0.1.11
      docker_host_swarm_role: "manager"
```

## Tags

- `traefik_validate`: Validate configuration variables
- `traefik_install`: Install Traefik and create directories
- `traefik_configure`: Configure and deploy Traefik

## Directory Structure

### Compose Mode
```
/opt/docker/
├── traefik/
│   ├── compose.yaml              # Docker Compose configuration
│   └── traefik/
│       ├── static.yaml           # Static Traefik configuration
│       └── dynamic.yaml          # Dynamic configuration (routers, services)
├── shared/
│   ├── networks/
│   └── volumes/
└── services/
    └── [your applications]
```

### Swarm Mode
```
/opt/docker/
├── traefik/
│   ├── swarm.yaml                # Docker Stack configuration
│   └── traefik/
│       ├── static.yaml           # Static Traefik configuration
│       └── dynamic.yaml          # Dynamic configuration (routers, services)
├── shared/
│   ├── networks/                 # Overlay networks
│   └── volumes/
└── services/
    └── [your applications]
```

## Usage Examples

### Docker Compose Service

```yaml
version: '3.8'
services:
  myapp:
    image: nginx:latest
    labels:
      - traefik.enable=true
      - traefik.http.routers.myapp.rule=Host(`myapp.example.com`)
      - traefik.http.routers.myapp.tls.certresolver=myresolver
      - traefik.http.services.myapp.loadbalancer.server.port=80
    networks:
      - {{ traefik_network_name }}

networks:
  {{ traefik_network_name }}:
    external: true
```

### Docker Stack Service (Swarm Mode)

```yaml
version: '3.8'
services:
  myapp:
    image: nginx:latest
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
    labels:
      - traefik.enable=true
      - traefik.http.routers.myapp.rule=Host(`myapp.example.com`)
      - traefik.http.routers.myapp.tls.certresolver=myresolver
      - traefik.http.services.myapp.loadbalancer.server.port=80
    networks:
      - {{ traefik_network_name }}

networks:
  {{ traefik_network_name }}:
    external: true
```

### Deployment Commands

#### Compose Mode
```bash
# Deploy application
docker compose -f myapp.yaml up -d

# Check status
docker compose -f myapp.yaml ps
```

#### Swarm Mode
```bash
# Deploy stack
docker stack deploy -c myapp.yaml myapp

# Check services
docker stack services myapp

# Check service logs
docker service logs myapp_myapp
```

### Custom Middlewares

```yaml
traefik_middlewares:
  auth:
    basicAuth:
      users:
        - "admin:$apr1$6a9t...j2W"  # htpasswd generated
  compression:
    compress: {}
  security:
    headers:
      frameDeny: true
      browserXssFilter: true
```

### Custom Services and Routers

```yaml
traefik_services:
  external_api:
    loadBalancer:
      servers:
        - url: "https://api.example.com"

traefik_routers:
  api_proxy:
    rule: "Host(`api.example.com`)"
    service: external_api
    tls:
      certResolver: myresolver
```

## Security Notes

- Docker socket is mounted read-only for Traefik
- Services run with security options enabled
- Only expose necessary ports
- Use environment variables for sensitive data
- Regularly update Traefik version
- Enable basic authentication for dashboard in production
- In Swarm mode, use placement constraints to control where Traefik runs
- Resource limits are automatically applied in Swarm mode

## Monitoring

Traefik provides several monitoring endpoints:

- **Dashboard**: https://{{ traefik_domain }} (when enabled)
- **Metrics**: http://localhost:8899/metrics (Prometheus format)
- **Ping**: http://localhost:8899/ping
- **API**: https://{{ traefik_domain }}/api (when enabled)

### Swarm-Specific Monitoring

```bash
# Check Traefik services
docker stack services traefik

# Check service replicas
docker service ps traefik_proxy

# Check service logs
docker service logs traefik_proxy

# Scale Traefik in Swarm
docker service scale traefik_proxy=3
```

## Additional Services

### Traefik Visualizer

The role includes an optional Traefik visualizer service that provides a simple web interface to visualize incoming requests:

```yaml
# Enable visualizer
traefik_visualizer_enabled: true
traefik_visualizer_domain: "visualizer.traefik.example.com"
```

**Access**: https://visualizer.traefik.example.com

**Features**:
- Shows incoming HTTP requests
- Displays headers and metadata
- Useful for debugging and monitoring
- Uses same SSL certificates as Traefik

**Note**: The visualizer uses the same `traefik/whoami` image but with different routing configuration.

## SSL Certificate Management

The role automatically handles SSL certificates through Let's Encrypt:

1. **DNS Challenge**: Uses Cloudflare DNS API token for wildcard certificates
2. **Automatic Renewal**: Certificates are renewed before expiration
3. **Storage**: Certificates stored in Docker volume `letsencrypt`

### Required Vault Variables

```yaml
# In your vault.yml
vault_cloudflare_dns_api_token: "your_cloudflare_dns_api_token"
vault_letsencrypt_email: "your_email@example.com"
vault_traefik_domain: "traefik.example.com"
```

## Troubleshooting

### Common Issues

1. **Certificate Generation Fails**
   - Verify Cloudflare API token permissions
   - Check DNS propagation
   - Ensure domain points to server

2. **Services Not Accessible**
    - Verify containers are on `{{ traefik_network_name }}` network
   - Check Traefik labels in Docker Compose
   - Review Traefik logs: `docker compose -f /opt/docker/traefik/compose.yaml logs proxy`
   - **Swarm**: `docker service logs traefik_proxy`

3. **Dashboard Not Loading**
   - Check if dashboard is enabled in `traefik_static_config.api.dashboard`
   - Verify domain DNS records
   - Check firewall rules for HTTPS port

4. **Swarm-Specific Issues**
   - **Services not starting**: Check placement constraints
   - **Network issues**: Verify overlay network exists: `docker network ls`
   - **Replica failures**: Check resource limits and node capacity
   - **Stack deployment fails**: Check YAML syntax and required resources

### Debug Commands

#### Compose Mode
```bash
# Check Traefik status
docker compose -f /opt/docker/traefik/compose.yaml ps

# View logs
docker compose -f /opt/docker/traefik/compose.yaml logs proxy

# Test configuration
docker compose -f /opt/docker/traefik/compose.yaml exec proxy traefik config check

# Reload configuration
docker compose -f /opt/docker/traefik/compose.yaml exec proxy traefik reload
```

#### Swarm Mode
```bash
# Check Traefik stack
docker stack services traefik

# Check service status
docker service ps traefik_proxy

# View logs
docker service logs traefik_proxy

# Test configuration
docker service logs traefik_proxy | grep config

# Scale service
docker service scale traefik_proxy=3

# Remove stack
docker stack rm traefik
```

## License

MIT

## Author Information

This role was created for the homelab infrastructure project following 2025 Ansible best practices.