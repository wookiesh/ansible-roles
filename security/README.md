# Security Mitigations

Targeted playbooks for CVE mitigations and security patches. Each playbook is self-contained and can be applied independently of `infrastructure.yaml`.

## Usage

```bash
# Dry-run against a group
ansible-playbook ../ansible-roles/security/<playbook>.yaml -i inventories/hosts.yaml --limit <group> --check --diff

# Apply to a single group
ansible-playbook ../ansible-roles/security/<playbook>.yaml -i inventories/hosts.yaml --limit swarm_infra

# Apply to a full inventory
ansible-playbook ../ansible-roles/security/<playbook>.yaml -i inventories/hosts.yaml
```

## Playbooks

### [cve-2026-31431.yaml](cve-2026-31431.yaml)

**CVE-2026-31431** — `algif_aead` kernel module privilege escalation.

Mitigation:
- Blacklists the module via `/etc/modprobe.d/disable-algif_aead.conf`
- Unloads the module if currently active
- Reboots hosts one at a time (`serial: 1`) to preserve Swarm quorum and service availability

Verify after applying:
```bash
ansible all -i inventories/hosts.yaml --limit swarm_infra -m command \
  -a "cat /etc/modprobe.d/disable-algif_aead.conf" --become
```
