# SMTP Role

## Description

This role configures Postfix as either a null client or relay host following 2025 Ansible best practices. It provides secure SMTP configuration with proper validation, idempotence, and flexible deployment options.

## Requirements

- Ansible >= 2.15
- Debian/Ubuntu based systems (tested on Ubuntu 20.04+, Debian 10+)
- Root or sudo privileges
- Postfix package repository access

## Role Variables

### Main Configuration
- `smtp_enabled`: Auto-detected from enabled mode (read-only, do not set)
- `smtp_mailname`: System mail name (default: `ansible_fqdn`)
- `smtp_domain`: Domain for email addresses (default: `ansible_domain`)
- `smtp_internal_domain`: Internal FQDN suffix used for address rewriting in relay mode (e.g. `lan.example.com`). Required when `smtp_relayhost_enabled: true`. (default: `""`)

### Null Client Configuration
- `smtp_null_client_enabled`: Configure as null client (default: `false`)
- `smtp_relayhost`: Relay host to forward all mail to (required if `smtp_null_client_enabled`) (default: `""`)
- `smtp_relayhost_port`: Port for relay host connection (default: `25`)

### Relay Host Configuration
- `smtp_relayhost_enabled`: Configure as relay host (default: `false`)
- `smtp_relay_domains`: List of domains to relay for (required if `smtp_relayhost_enabled`) (default: `[]`)
- `smtp_external_relayhost`: External relay for outgoing mail (default: `""`)
- `smtp_external_relayhost_port`: External relay port (default: `587`)

### Multi-Relay Configuration
- `smtp_multi_relay_enabled`: Configure as a sender-dependent multi-relay smart-host (default: `false`)
- `smtp_relay_domain_map`: List of `{domain, relayhost}` — single source of truth for `sender_relay`, `sender_access`, and (with `smtp_relay_credentials`) `sasl_passwd` (required if `smtp_multi_relay_enabled`) (default: `[]`)
- `smtp_relay_credentials`: Dict keyed by relayhost string → `{user, password}`; every relayhost used in `smtp_relay_domain_map` must have a matching key, enforced at validation time (default: `{}`)
- `smtp_myhostname`: Explicit `myhostname` override, required for this mode — see "Why `smtp_myhostname` is required" below (default: `""`, falls back to `ansible_fqdn` for other modes)
- `smtp_mynetworks`, `smtp_banner_text`, `smtp_inet_protocols`, `smtp_enable_long_queue_ids`, `smtp_soft_error_limit`, `smtp_sasl_mechanism_filter`: overridable base settings shared by all modes (see `defaults/main.yml`); unset behaves exactly as before this feature was added

### Prometheus Exporter (opt-in, any mode)
- `smtp_exporter_enabled`: Install `prometheus-postfix-exporter`, listening on `:9154` (default: `false`)
- Reads from the standard `/var/log/mail.log` (via a systemd `ExecStart` override in `tasks/exporter.yaml`), not the package's systemd/journal default — Postfix's master process isn't managed by `postfix@-.service` on these hosts (see the stub note above), so the journal-based default silently produces no metrics. No private log copy needed: `/var/log/mail.log` already exists, is rsyslog-rotated out of the box, and the `alloy_native` role tails the same file for log shipping.
- Pair with the `node_exporter` role (separate, generic — not part of this role) for host-level metrics on `:9100`.

### Security & TLS
- `smtp_use_tls`: Enable TLS for outgoing connections (default: `true`)
- `smtp_tls_security_level`: TLS security level (default: `"encrypt"`)
- `smtp_sasl_auth_enable`: Enable SASL authentication for outgoing connections (default: `false`)

### Authentication (use vault variables)
- `smtp_sasl_user`: SASL username (default: `vault_smtp_sasl_user | default('')`)
- `smtp_sasl_password`: SASL password (default: `vault_smtp_sasl_password | default('')`)

### System Aliases
- `smtp_root_alias`: Redirect root mail to an external address (default: `""`, optional)
- `smtp_aliases`: Additional system email aliases (default: postmaster/nobody/hostmaster/webmaster/www → root)

## Deployment Modes

### Null Client Mode
Forwards all local mail to a central relay host. Ideal for:
- Application servers
- Monitoring hosts  
- Workstations
- Any host that only needs to send mail

```yaml
# group_vars/app_servers.yaml
smtp_null_client_enabled: true
smtp_relayhost: "smtp.homelab.local"
smtp_relayhost_port: 25
```

### Relay Host Mode
Receives mail from null clients and forwards to external SMTP. Ideal for:
- Central mail gateways
- DMZ SMTP servers
- Mail aggregation points

```yaml
# group_vars/smtp_relays.yaml
smtp_relayhost_enabled: true
smtp_relay_domains: ["homelab.local", "app.homelab.local"]
smtp_external_relayhost: "smtp.provider.com"
smtp_external_relayhost_port: 587

# In vault.yml
vault_smtp_sasl_user: "user@provider.com"
vault_smtp_sasl_password: "secure_password"
```

### Multi-Relay Mode
For a pure send-only smart-host relay serving **several independent sender
domains**, each routed to its own external relay/provider with its own SASL
credentials — e.g. one internal domain goes out via one ESP, a partner
domain goes out via a dedicated relay a partner organization provided you.
Not the same as Relay Host Mode above, which assumes one external relayhost
for everything.

```yaml
# group_vars/smtp_relays.yaml
smtp_multi_relay_enabled: true
smtp_mynetworks: "127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128, 192.168.0.0/16, 172.16.0.0/12, 10.0.0.0/8"
smtp_inet_protocols: "ipv4"
smtp_tls_security_level: "may" # or "encrypt" if every sender speaks STARTTLS
smtp_sasl_auth_enable: true
smtp_sasl_mechanism_filter: "plain"

smtp_relay_domain_map:
  - { domain: "example.com", relayhost: "smtp.provider.com" }
  - { domain: "partner.example", relayhost: "[203.0.113.9]:587" }

smtp_relay_credentials:
  "smtp.provider.com": { user: "{{ vault_smtp_provider_user }}", password: "{{ vault_smtp_provider_password }}" }
  "[203.0.113.9]:587": { user: "{{ vault_smtp_partner_user }}", password: "{{ vault_smtp_partner_password }}" }

# host_vars/<hostname>.yaml — one per relay node, REQUIRED for this mode
smtp_myhostname: "<hostname>.<real-fqdn-domain>"
```

**Why `smtp_myhostname` is required for this mode**: every other mode falls
back to `ansible_fqdn`, which is convenient but silently wrong if the box's
`/etc/hosts`/DNS is misconfigured — `ansible_fqdn` will happily resolve to a
name that only works locally, is easy to miss in review, and quietly breaks
EHLO identity / deliverability. Not worth the risk on a mail relay: set it
explicitly per host instead.

**Sender-only routing, not recipient-based**: `smtp_relay_domain_map` keys
on the envelope SENDER domain. Mail addressed *to* a domain in the map does
not get special routing — it's routed based on whoever is sending it. If you
need routing based on the sender being a *specific* partner domain even when
addressing a third party, add that partner's domain to the map; don't expect
recipient-side matching.

**One relay's own access control isn't yours to fix**: a relay you route to
may enforce its own sender allowlist independently of this role (e.g. a
partner-provided relay account scoped to specific envelope senders on their
side). SASL auth succeeding does not guarantee they'll accept every sender
you point at them — check their logs for a `554 ... Sender address
rejected` that mentions *their* relay, not yours, if that happens.

See `tests/multi_relay_credentials_check.md` (design note, not an automated
test) for how the credentials-completeness validation works and why it
matters — this exact class of bug (a domain added to the routing map but its
credentials forgotten) caused a real same-day outage before this role
feature existed.

## Example Playbook

### Null Client Deployment
```yaml
- hosts: app_servers
  become: true
  roles:
    - role: smtp
      vars:
        smtp_null_client_enabled: true
        smtp_relayhost: "relay.homelab.local"
        smtp_domain: "homelab.local"
```

### Relay Host Deployment
```yaml
- hosts: smtp_gateways
  become: true
  roles:
    - role: smtp
      vars:
        smtp_relayhost_enabled: true
        smtp_relay_domains: ["homelab.local"]
        smtp_internal_domain: "homelab.local"
        smtp_external_relayhost: "smtp.provider.com"
        smtp_sasl_auth_enable: true
        smtp_sasl_user: "{{ vault_smtp_sasl_user }}"
        smtp_sasl_password: "{{ vault_smtp_sasl_password }}"
```

## Example Inventory

```yaml
all:
  children:
    smtp_relays:
      hosts:
        smtp-01:
          ansible_host: 192.168.1.10
          smtp_relayhost_enabled: true
          smtp_relay_domains: ["homelab.local"]
          smtp_external_relayhost: "smtp.provider.com"
    app_servers:
      hosts:
        app-01:
          ansible_host: 192.168.1.20
          smtp_null_client_enabled: true
          smtp_relayhost: "smtp-01.homelab.local"
        app-02:
          ansible_host: 192.168.1.21
          smtp_null_client_enabled: true
          smtp_relayhost: "smtp-01.homelab.local"
```

## Tags

- `smtp_install`: Install Postfix and dependencies
- `smtp_configure`: Configure Postfix settings
- `smtp_null_client`: Configure null client mode
- `smtp_relayhost`: Configure relay host mode
- `smtp_multi_relay`: Configure multi-relay mode
- `smtp_exporter`: Configure the opt-in Postfix Prometheus exporter
- `smtp_validate`: Validate configuration variables

## Directory Structure

```
/etc/postfix/
├── main.cf                 # Main Postfix configuration
├── master.cf              # Service definitions (managed by package)
├── sasl_passwd            # SASL authentication (relay mode and multi-relay mode)
├── sasl_passwd.db         # Compiled SASL database
├── header_checks          # Header rewriting rules
├── sender_canonical       # Sender address rewriting
├── recipient_canonical    # Recipient address rewriting
├── sender_relay           # Multi-relay mode only: sender domain → relayhost (hash: map)
├── sender_relay.db        # Compiled sender_relay database
├── sender_access          # Multi-relay mode only: sender allowlist (regexp: map, not compiled)
└── aliases.db            # System aliases database
```

## Security Notes

- SASL passwords are stored in `/etc/postfix/sasl_passwd` with 0600 permissions
- TLS is enforced by default for all connections
- Null clients only listen on localhost (127.0.0.1)
- Relay hosts use proper recipient restrictions
- All sensitive data should use vault variables

## Testing

### Live email delivery — `test_mail` module

The role ships a custom `test_mail` module (`library/test_mail.py`) that sends a real email through the host's local MTA and fails if delivery is rejected.

Use the bundled playbook (run from the infra repo):

```bash
ansible-playbook ../ansible-roles/roles/smtp/tests/test_mail.yml \
  -l <host> \
  -e "test_mail_to=you@example.com"
```

Optional extra vars:
- `test_mail_from` — sender address (defaults to system default)
- `test_mail_subject` — subject line

**Prerequisite** — the infra repo's `ansible.cfg` must declare the library path:

```ini
[defaults]
library = ../ansible-roles/roles/smtp/library
```

### Syntax Check
```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --tags smtp --syntax-check
```

### Dry Run
```bash
ansible-playbook -i inventory.yaml infrastructure.yaml --tags smtp --check
```

### Idempotence Test
```bash
# Run twice - second run should show no changes
ansible-playbook -i inventory.yaml infrastructure.yaml --tags smtp
ansible-playbook -i inventory.yaml infrastructure.yaml --tags smtp
```

### Configuration Validation
```bash
# On target host
postfix check
postconf -n  # Show effective configuration
```

## Troubleshooting

### Common Issues

**Null client cannot send mail:**
- Verify relay host is reachable: `telnet {{ smtp_relayhost }} {{ smtp_relayhost_port }}`
- Check Postfix logs: `journalctl -u postfix -f`
- Verify relay host accepts connections from your IP

**Relay host authentication fails:**
- Check SASL credentials in vault
- Verify external relay host settings
- Test authentication manually: `testsaslauthd`

**Mail delivery delays:**
- Check DNS resolution for domains
- Verify firewall allows port 25/587
- Review Postfix queue: `mailq`

**Multi-relay mode: sender gets an immediate `554 ... Access denied`:**
- That sender's domain isn't in `smtp_relay_domain_map` — check `/etc/postfix/sender_access` on the host. This is intentional: only mapped domains may relay at all (see `smtpd_sender_restrictions` in the "Multi-Relay Mode" section above), even from `mynetworks`.
- A raw hostname-based sender (e.g. `root@some-host.internal.example.com`) is the most common real cause — fix that host's mail sender config to use a mapped domain rather than widening the allowlist.

**Multi-relay mode: one relay rejects a sender even though SASL auth succeeds:**
- That's the *relay's own* access control, not this role's — see "One relay's own access control isn't yours to fix" in the "Multi-Relay Mode" section above. Check whether the sender is actually meant to go through that specific relay at all; it may correctly belong to a different entry in `smtp_relay_domain_map` instead.

**Postfix exporter (`smtp_exporter_enabled`): `postfix_*` metrics stay empty / journal `Permission denied`:**
- `/var/log/mail.log` is `syslog:adm` mode `0640` — the exporter (and `alloy_native`) read it via the `adm` supplementary group added in their respective systemd overrides/user config, not via file ownership. Don't `chown` it to `prometheus`/`alloy`; rsyslogd runs unprivileged as `syslog:adm` and would fail to write to a file it no longer owns.

### Debug Commands

```bash
# Check Postfix status
systemctl status postfix
```

⚠️ On Debian/Ubuntu, `postfix.service` ships as `Type=oneshot,
ExecStart=/bin/true` — Postfix supervises its own master process outside
systemd, so `systemctl status/restart postfix` does not reliably reflect or
control the real daemon (`active (exited)` is the normal state regardless of
whether the master is actually running). Use instead:

```bash
# Actually control the daemon
postfix reload   # config changes that don't affect socket binding
postfix stop; postfix start   # inet_protocols / inet_interfaces / master.cf changes — reload alone won't rebind sockets
postfix check    # validate config without applying

# Actually verify it's up
ps aux | grep master
ss -tlnp | grep :25

# View mail queue
mailq

# Check configuration
postconf -n

# Test mail delivery
echo "Test message" | mail -s "Test" admin@example.com

# View detailed logs (may be empty/misleading for the reasons above — prefer mail.log)
journalctl -u postfix -f
tail -f /var/log/mail.log
```

## Integration with Other Roles

This role integrates well with:
- `monitoring` roles (for alert delivery)
- `application` roles (for notification emails)
- `backup` roles (for backup reports)

## License

MIT

## Author Information

This role was created for the homelab infrastructure project following 2025 Ansible best practices with emphasis on security, idempotence, and maintainability.