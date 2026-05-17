# Role Testing Guide

## Overview

Testing standards for Ansible roles in this repository. **Idempotence testing is mandatory** — every role must produce 0 changes on a second run.

## Testing Levels

### 1. Linting (Static Analysis)

```bash
# Syntax check
ansible-playbook roles/role_name/tests/test.yml --syntax-check

# Style and quality
ansible-lint roles/role_name/

# YAML validation
yamllint roles/role_name/
```

### 2. Basic Role Testing

Each role must have a `tests/test.yml` playbook and a `tests/inventory` file.

```bash
# Run once — expect changes
ansible-playbook -i roles/role_name/tests/inventory roles/role_name/tests/test.yml

# Run again — must show 0 changes
ansible-playbook -i roles/role_name/tests/inventory roles/role_name/tests/test.yml
```

### 3. Molecule (Optional but Recommended)

```
roles/role_name/
└── molecule/
    └── default/
        ├── converge.yml    # Main test playbook
        ├── verify.yml      # Verification tasks
        └── molecule.yml    # Molecule configuration
```

#### molecule.yml

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: debian-12
    image: debian:12
    pre_build_image: true
    groups:
      - test_hosts
  - name: ubuntu-24.04
    image: ubuntu:24.04
    pre_build_image: true
    groups:
      - test_hosts
provisioner:
  name: ansible
  inventory:
    group_vars:
      all:
        ansible_user: root
  playbooks:
    converge: converge.yml
    verify: verify.yml
verifier:
  name: ansible
lint: |
  set -e
  ansible-lint
  yamllint .
```

#### converge.yml

```yaml
---
- name: Converge
  hosts: all
  become: true
  vars:
    role_enabled: true
  tasks:
    - name: Include role
      ansible.builtin.include_role:
        name: "{{ lookup('env', 'MOLECULE_PROJECT_DIRECTORY') | basename }}"
```

#### verify.yml

```yaml
---
- name: Verify
  hosts: all
  become: true
  tasks:
    - name: Check service is running
      ansible.builtin.systemd:
        name: "{{ role_service_name }}"
      register: service_state
      failed_when: service_state.status.ActiveState != "active"
      when: role_service_name is defined

    - name: Check config file exists
      ansible.builtin.stat:
        path: "{{ role_config_file }}"
      register: config_stat
      failed_when: not config_stat.stat.exists
      when: role_config_file is defined
```

## Security Testing

### File permissions

```yaml
- name: Verify file permissions
  ansible.builtin.stat:
    path: "{{ role_config_file }}"
  register: security_check

- name: Assert secure permissions
  ansible.builtin.assert:
    that:
      - security_check.stat.mode in ['0600', '0640']
      - security_check.stat.pw_name == role_user
    fail_msg: "Insecure file permissions on {{ role_config_file }}"
```

### No hardcoded secrets

```yaml
- name: Verify no hardcoded secrets
  ansible.builtin.lineinfile:
    path: "{{ role_config_file }}"
    regexp: '(password|secret|key)\s*:\s*["\']?[a-zA-Z0-9]+'
    state: absent
  check_mode: true
  register: secret_check
  failed_when: secret_check.changed
```

## Test Variables

```yaml
# roles/role_name/tests/vars/main.yml
---
role_enabled: true
role_test_mode: true
role_test_domain: "test.example.com"
role_test_port: 8080
# Mock vault vars for testing only
vault_role_test_password: "test_password_not_for_prod"
```

## Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Ansible Roles

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install tools
        run: pipx install ansible-lint yamllint
      - name: Lint
        run: ansible-lint && yamllint .

  molecule:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role:
          - docker_host
          - traefik
          - keepalived
    steps:
      - uses: actions/checkout@v4
      - name: Install Molecule
        run: pipx install molecule[docker] ansible
      - name: Run Molecule
        run: molecule test
        working-directory: roles/${{ matrix.role }}
```

## Checklist Before Submitting

- [ ] Syntax check passes
- [ ] `ansible-lint` passes
- [ ] Idempotence confirmed (second run = 0 changes)
- [ ] File permissions and secrets validated where applicable
- [ ] Molecule tests pass (if present)
