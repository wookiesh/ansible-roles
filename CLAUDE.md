# ansible-roles — guidelines for Claude

## Ansible conventions

### `become: true`
Use `become` at the **task level only**, never imported from a calling play.
Each task that needs root (writing to system paths, setting root ownership, apt install) carries its own `become: true`.
Tasks that don't need root (docker socket calls, URI, delegate_to: localhost, getent) must not escalate.

```yaml
# correct — task-level become
- name: Create service directory
  ansible.builtin.file:
    path: /opt/docker/myservice
    state: directory
    owner: root
    group: docker
    mode: "2775"
  become: true

- name: Start service
  community.docker.docker_compose_v2:
    project_src: /opt/docker/myservice
    state: present
  # no become — docker group is sufficient
```

### Service directory ownership
Directories under `/opt/docker/` follow the pattern `owner: root, group: docker, mode: 2775`.
This is consistent across all roles (alloy, traefik, docker_stacks, dns_server).

### No `xxx_enabled` flags
New roles must not have an enabled/disabled flag as a role-level gate.
The play's `hosts:` field is the gate — the role runs unconditionally when assigned.
Feature flags that control behaviour *within* a role (e.g. `smtp_null_client_enabled`) are fine.
