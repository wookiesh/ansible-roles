# Ansible Role: ssh_config_gen

Generates `~/.ssh/config` and a per-project host file under `~/.ssh/config.d/` from
the Ansible inventory. Designed to be used in a local play (connection: local) from
multiple projects, each writing its own profile file.

## Architecture

```
~/.ssh/config             ← global options + Include config.d/*
~/.ssh/config.d/project1  ← hosts from project1 inventory
~/.ssh/config.d/project2  ← hosts from project2 inventory
```

Each project sets `ssh_config_gen_output` to its own profile path. Running the local
play from each project updates only that profile without touching others.

## Requirements

- The play must run on `localhost` with `ansible_connection: local`
- `gather_facts: true` (default) required for the macOS conditional in `ssh_config.j2`

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_config_gen_output` | `""` | Path to the per-project host file (required) |
| `ssh_config_gen_main` | `"~/.ssh/config"` | Path to the main SSH config file |
| `ssh_config_gen_extra_hosts` | `[]` | Additional host entries not in the inventory (see below) |

## Per-host/group Variables

These are set in the inventory, not in role defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_config_gen_forward_agent` | `false` | Add `ForwardAgent yes` for this host/group |
| `ssh_config_gen_proxy_jump` | `""` | Add `ProxyJump <value>` for this host/group |

Hosts without `ansible_host` (placeholder entries) are skipped.

## Extra hosts

`ssh_config_gen_extra_hosts` handles hosts that exist in the infrastructure but should
not be Ansible targets — typically VIPs (keepalived, load balancer) or bastion aliases.
Set it on the `local_machines` group so it is scoped to the local play.

```yaml
local_machines:
  vars:
    ssh_config_gen_output: "~/.ssh/config.d/project2"
    ssh_config_gen_extra_hosts:
      - name: infra
        hostname: "10.219.206.36"
        forward_agent: true
      - name: bastion
        hostname: "bastion.example.com"
        forward_agent: true
      - name: internal-host
        hostname: "10.0.1.50"
        proxy_jump: bastion
```

Supported keys per entry: `name` (required), `hostname` (required), `forward_agent`, `proxy_jump`, `strict_host_key_checking`.

Use `strict_host_key_checking: accept-new` for floating IPs (keepalived VIPs) whose
host key may change depending on which node currently holds the address.

## Known hosts

Inventory hosts that have never been connected to will fail with `StrictHostKeyChecking yes`.
Populate `~/.ssh/known_hosts` before first use:

```bash
# Single host
ssh-keyscan -H <ip> >> ~/.ssh/known_hosts

# All hosts in a group (example)
ssh-keyscan -H 10.110.206.95 10.111.206.20 >> ~/.ssh/known_hosts
```

## Example

```yaml
# inventories/project1/hosts.yaml
local_machines:
  vars:
    ssh_config_gen_output: "~/.ssh/config.d/project1"
  hosts:
    localhost:
      ansible_connection: local

admin_workstations:
  vars:
    ssh_config_gen_forward_agent: true
  hosts:
    bastion:
      ansible_host: 10.0.0.1

# playbook
- name: Generate SSH config
  hosts: local_machines
  roles:
    - ssh_config_gen
```

## Generated output

`~/.ssh/config` (global, written once per run):
```
Include config.d/*

Host *
StrictHostKeyChecking yes
ServerAliveInterval 300
...
AddKeysToAgent yes   # macOS only
UseKeychain yes      # macOS only
```

`~/.ssh/config.d/<profile>` (per-project, sorted by hostname):
```
Host bastion
HostName 10.0.0.1
IdentitiesOnly yes
ForwardAgent yes

Host web01
HostName 10.0.0.10
IdentitiesOnly yes
ProxyJump bastion
```

## License

MIT
