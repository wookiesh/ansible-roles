# Contributing to ansible-roles

Generic Ansible roles consumed by homelab and ana-infra via `roles_path`.

## Getting started

```bash
# Clone alongside the consumer repos
git clone https://github.com/wookiesh/ansible-roles ../ansible-roles

# Roles are picked up automatically via ansible.cfg roles_path in each project
```

## Role development standards

See [docs/ROLE_DEVELOPMENT.md](docs/ROLE_DEVELOPMENT.md) for the full guide covering structure, idempotence, variable naming, testing, and meta requirements.

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
