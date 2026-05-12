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
- `smtp_validate`: Validate configuration variables

## Directory Structure

```
/etc/postfix/
├── main.cf                 # Main Postfix configuration
├── master.cf              # Service definitions (managed by package)
├── sasl_passwd            # SASL authentication (relay mode only)
├── sasl_passwd.db         # Compiled SASL database
├── header_checks          # Header rewriting rules
├── sender_canonical       # Sender address rewriting
├── recipient_canonical    # Recipient address rewriting
└── aliases.db            # System aliases database
```

## Security Notes

- SASL passwords are stored in `/etc/postfix/sasl_passwd` with 0600 permissions
- TLS is enforced by default for all connections
- Null clients only listen on localhost (127.0.0.1)
- Relay hosts use proper recipient restrictions
- All sensitive data should use vault variables

## Testing

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

### Debug Commands

```bash
# Check Postfix status
systemctl status postfix

# View mail queue
mailq

# Check configuration
postconf -n

# Test mail delivery
echo "Test message" | mail -s "Test" admin@example.com

# View detailed logs
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