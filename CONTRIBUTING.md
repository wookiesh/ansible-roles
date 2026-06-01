# Contributing to ansible-roles

Generic Ansible roles consumed by any inventory via `roles_path`.

## Getting started

```bash
# Clone alongside the consumer repos
git clone https://github.com/wookiesh/ansible-roles ../ansible-roles

# Roles are picked up automatically via ansible.cfg roles_path in each project
```

## Role development standards

See [docs/ROLE_DEVELOPMENT.md](docs/ROLE_DEVELOPMENT.md) for the full guide covering structure, idempotence, variable naming, and meta requirements.

See [docs/TESTING.md](docs/TESTING.md) for testing standards: linting, idempotence, Molecule, and CI.

## Role design principles

- **No `xxx_enabled` gate flag.** Roles run unconditionally. The caller controls targeting via `hosts:` in the playbook.
- **Feature flags are fine** for optional behaviour within a role (`docker_host_swarm_enabled`, `traefik_acme_enabled`, etc.) — they don't gate the role, they select a code path.
- **`become: true` at task level only**, never at play level. Only the tasks that actually write root-owned files or install packages need it.
- **Service directory ownership**: `owner: root, group: docker, mode: 2775`.

### Per-application roles (Docker services)

New Docker application roles follow the `portainer`/`beszel`/`uptimekuma` pattern:
- Auto-detect deployment mode from `docker_host_swarm_enabled` in defaults
- Two templates: `compose.yaml.j2` (standalone) and `stack.yaml.j2` (swarm)
- Stack deploy task uses `run_once: true, delegate_to: "{{ docker_swarm_manager }}"`
- No `xxx_enabled` flag — the role is assigned via `hosts:` in site.yaml

## Adding or modifying a role

1. Follow the structure in `docs/ROLE_DEVELOPMENT.md`
2. Ensure the role has no project-specific defaults — all org/project values belong in the consumer's inventory
3. Validate with ansible-lint before opening a PR
4. Run the role's test playbook twice and confirm 0 changes on the second run

```bash
ansible-lint roles/role_name
ansible-playbook roles/role_name/tests/test.yml
ansible-playbook roles/role_name/tests/test.yml  # must show 0 changes
```

## Commit style

[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(docker_host): add swarm overlay network config option
fix(traefik): correct TLS secret name variable reference
docs(smtp): document smtp_internal_domain variable
refactor(keepalived): extract notify scripts to dedicated task file
```

## Versioning

Semantic git tags: `v1.0.0`, `v1.1.0`, etc.
- Breaking change in a role's interface → minor or major bump
- Bug fix or additive change → patch bump

## PR checklist

- [ ] Role passes `ansible-lint`
- [ ] Idempotence confirmed (second run = 0 changes)
- [ ] No project-specific values in defaults
- [ ] `README.md` updated
- [ ] `CHANGELOG.md` entry added (if applicable)
