# Docker Stacks Role

> **DEPRECATED** — This role is replaced by per-application roles (`portainer`, `beszel`, `uptimekuma`, `dns_server`).
> Each application now has its own role following the `dns_server` pattern.
> This role will be removed once all stacks have been migrated to per-app roles.

## Description

Simplified role for deploying existing Docker Compose and Docker Swarm stack files. This role focuses on copying and deploying pre-existing YAML stack files rather than generating complex templates.

## Requirements

- Ansible >= 2.15
- Docker Engine installed (use `docker_host` role)
- Docker Swarm initialized (for Swarm mode)
- Root or sudo privileges
- Debian/Ubuntu based systems

## Role Variables

### Main Configuration
- `docker_stacks_enabled`: Enable Docker stacks management (default: false)
- `docker_stacks_base_dir`: Base directory for stacks (default: "{{ docker_host_services_root | default('/opt/docker') }}/stacks")
- `docker_swarm_manager`: Host where stacks should be deployed (default: "{{ groups[group_names | select('match', '^swarm_') | first][0] | default('localhost') }}")

### Stack Configuration
- `docker_stacks`: List of stacks to deploy (default: [])

## Stack Configuration Structure

Each stack in `docker_stacks` list supports this simplified structure:

```yaml
docker_stacks:
  - name: beszel                    # Required: Stack name
    stack_template: stacks/infra/beszel.yaml.j2  # Required: Path to Jinja2 template file
    target_hosts: swarm-manager-01  # Required: Target host where to deploy
```

## Example Playbook

```yaml
- name: Deploy Docker stacks
  hosts: all
  become: true
  vars:
    docker_stacks_enabled: true
docker_stacks:
  - name: monitoring
    stack_template: inventories/myproject/stacks/infra/monitoring.yaml.j2
    target_hosts: swarm-manager-01
      - name: webapp
        compose_file: inventories/myproject/stacks/dmz/webapp.yaml
        target_hosts: swarm-edge-01
  roles:
    - role: docker_stacks
```

## Example Inventory

### Group Variables
```yaml
# group_vars/swarm_infra.yaml
docker_stacks_enabled: true
docker_swarm_manager: "swarm-manager-01"
docker_stacks:
  - name: reverse_proxy
    stack_template: stacks/dmz/reverse_proxy.yaml.j2
    target_hosts: swarm-edge-01
```

## Directory Structure

The role creates this structure:

```
/opt/docker/stacks/
├── beszel/                    # Stack directory
│   └── stack.yaml            # Copied compose file
├── monitoring/
│   └── stack.yaml
└── webapp/
    └── stack.yaml
```

## Usage Examples

### Deploy All Stacks
```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --tags stacks
```

### Deploy on Specific Host
```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --tags stacks --limit swarm-manager-01
```

### Check Mode (Dry Run)
```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --tags stacks --check
```

## How It Works

1. **Validation**: Checks basic configuration requirements
2. **Directory Creation**: Creates base directory and stack-specific directories
3. **File Copy**: Copies existing compose files to stack directories as `stack.yaml`
4. **Deployment**: Deploys stacks using `docker stack deploy`
5. **Reporting**: Shows deployment status and results

## Stack Template Requirements

Stack templates should be:
- Valid Docker Compose or Docker Swarm YAML files with Jinja2 templating
- Use Ansible variables for dynamic values (e.g., `{{ server_domain }}`)
- Self-contained (include all necessary networks, volumes, secrets)
- Ready for deployment after Ansible variable resolution

Example stack template:
```yaml
version: '3.8'
services:
  app:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - frontend
    environment:
      APP_URL: https://app.{{ server_domain }}
networks:
  frontend:
    driver: overlay
```

## Deployment Behavior

- **Only runs on designated deploy host**: Controlled by `docker_swarm_manager`
- **Idempotent**: Only deploys when compose file changes
- **Swarm mode**: Uses `docker stack deploy` command
- **File management**: Copies files to standardized locations

## Troubleshooting

### Common Issues

**Stack deployment fails:**
- Check Docker Swarm status: `docker node ls`
- Verify compose file syntax: `docker compose config`
- Check file permissions and paths

**File not found:**
- Verify `compose_file` path is correct
- Check file exists on control node
- Ensure relative paths are from playbook directory

**Permission denied:**
- Ensure Ansible user has sudo privileges
- Check Docker daemon permissions
- Verify directory permissions

### Debug Commands

```bash
# Check Docker Swarm status
docker node ls
docker stack ls

# Validate compose file
docker compose config -f <stack_file>

# Check stack services
docker stack services <stack_name>
docker service ps <stack_name>

# View logs
docker service logs <stack_name>
```

## Integration with Other Roles

This role works well with:
- `docker_host`: For Docker installation and Swarm setup
- `traefik`: For reverse proxy (stacks can reference Traefik networks)
- `monitoring`: For monitoring stack services

## Security Notes

- Stack files should not contain sensitive data in plain text
- Use Docker secrets for sensitive configuration
- Ensure proper file permissions on stack files
- Run with appropriate user privileges

## Performance Considerations

- Deploy stacks on dedicated manager nodes
- Use resource limits in compose files
- Monitor stack resource usage
- Consider network topology for multi-host stacks

## License

MIT

## Author

Simplified role for homelab infrastructure deployment.