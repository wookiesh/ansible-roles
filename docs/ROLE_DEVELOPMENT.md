# Role Development Guide

## Overview

Standards and best practices for developing Ansible roles in this repository. **Idempotence is mandatory** — every role must produce the same result whether run once or ten times.

## Role Structure

```
roles/role_name/
├── README.md              # Role documentation (required)
├── defaults/main.yml      # Default variables (required)
├── tasks/
│   ├── main.yaml          # Entry point (required)
│   ├── install.yaml
│   ├── configure.yaml
│   └── validate.yaml
├── handlers/main.yml
├── vars/main.yml          # OS-specific or fixed variables
├── templates/             # Jinja2 templates
├── files/                 # Static files
├── meta/main.yml          # Role metadata (required)
└── tests/
    ├── inventory
    └── test.yml           # Test playbook (required)
```

**File naming**: `.yaml` extension, `snake_case`. Task files should be descriptive (`install_docker.yaml`, `configure_sshd.yaml`).

## Development Standards

### Idempotence (mandatory)

Use module state rather than commands when possible:

```yaml
# Bad — always reports changed
- name: Restart service
  ansible.builtin.service:
    name: nginx
    state: restarted

# Good — only restarts when notified
- name: Update configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart nginx
```

### Variable validation (mandatory)

```yaml
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - role_name is defined and role_name | length > 0
      - role_port is number and role_port > 0 and role_port < 65536
    fail_msg: "Missing required variable for {{ role_name }}"
```

### Fully Qualified Collection Names

```yaml
# Bad
- user:
    name: "{{ app_user }}"

# Good
- ansible.builtin.user:
    name: "{{ app_user }}"
```

### Secret management

```yaml
# Good — reference vault variables
role_database_password: "{{ vault_role_database_password }}"

# Bad — never hardcode secrets
role_database_password: "supersecret123"
```

## Variable Naming

Use `role_prefix_variable_name` consistently:

```yaml
# defaults/main.yml
docker_enabled: true
docker_version: "latest"
docker_log_driver: "json-file"
```

## Meta information

```yaml
# meta/main.yml
---
galaxy_info:
  author: ""
  description: ""
  license: MIT
  min_ansible_version: "2.15"
  platforms:
    - name: Debian
      versions: [bullseye, bookworm]
    - name: Ubuntu
      versions: [jammy, noble]
  galaxy_tags: []
dependencies: []
```

## Testing

```bash
# Syntax check
ansible-playbook roles/role_name/tests/test.yml --syntax-check

# Dry-run
ansible-playbook roles/role_name/tests/test.yml --check

# Idempotence — run twice, second run must show 0 changes
ansible-playbook roles/role_name/tests/test.yml
ansible-playbook roles/role_name/tests/test.yml
```

## Checklist before submitting

- [ ] All tasks are idempotent
- [ ] All variables validated with `assert`
- [ ] FQCN used throughout (`ansible.builtin.*`)
- [ ] No hardcoded secrets
- [ ] `changed_when` / `failed_when` set where needed
- [ ] `README.md` documents all variables with defaults and examples
- [ ] `meta/main.yml` complete
- [ ] Tests pass and confirm idempotence
