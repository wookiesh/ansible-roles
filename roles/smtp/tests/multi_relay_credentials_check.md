# Design note: the credentials-completeness assert

`tasks/main.yml`'s validation task includes:

```yaml
- >-
  smtp_multi_relay_enabled | default(false) == false or
  (smtp_relay_domain_map | map(attribute='relayhost') | unique | list
  | difference(smtp_relay_credentials.keys() | list) | length == 0)
```

This fails the play if any `relayhost` referenced in `smtp_relay_domain_map`
does not have a matching key in `smtp_relay_credentials`.

## Why this exists

Before `smtp_multi_relay_enabled` existed, a production relay's per-domain
routing was hand-maintained across three separate files
(`sender_relay`, `sasl_passwd`, `sender_access`). A new domain was added to
two of the three files and forgotten in the third — the domain silently
failed to relay (rejected by the upstream provider with "Relay access
denied") until someone noticed and diagnosed it later that same day.

Modeling the mapping as a single `smtp_relay_domain_map` variable makes the
`sender_relay` and `sender_access` files structurally impossible to drift
from each other (both are generated from the same list, every run). This
assert closes the remaining gap: it can't stop someone from mistyping a
relayhost string, but it does stop the specific failure mode that actually
happened — a domain present in the routing map with no corresponding
credentials at all.

## Manually verified behavior (2026-08-23)

Rendered `main.cf`, `sender_relay`, `sasl_passwd`, and `sender_access` via
`ansible.builtin.template` against a scratch `localhost` play using the
exact variable values planned for `ana-infra`'s `smtp_relays` group —
output matched the live, hand-hardened configuration on
`ana-relay-postfix-01` byte-for-byte (aside from placeholder credential
values). Then re-ran the validation assert with one relayhost's credentials
entry deliberately omitted (reproducing the original incident) and
confirmed it fails with a clear message naming the missing entry, instead
of silently producing a broken `sasl_passwd`.

This was ad-hoc local verification, not a committed automated test — there
was no throwaway target available to run a real `ansible-playbook --check`
against, and the live relay hosts were explicitly out of scope to touch for
this change. If this role gets a proper CI/molecule setup later, encoding
both cases (valid map, and a map with a missing credential) as real test
fixtures would be worthwhile.
