#!/usr/bin/python3

"""Ansible module for testing email delivery through the local MTA."""

import subprocess
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = {
        "to": {"type": "str", "required": True},
        "from_addr": {"type": "str", "default": ""},
        "subject": {"type": "str", "default": "Test Email from Ansible"},
        "body": {"type": "str", "default": "This is a test email sent by Ansible."},
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    to = module.params["to"]
    from_addr = module.params["from_addr"]
    subject = module.params["subject"]
    body = module.params["body"]

    cmd = ["mail", "-s", subject]
    if from_addr:
        cmd += ["-r", from_addr]
    cmd.append(to)

    message = f"{body}\n\nSent on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        proc = subprocess.run(
            cmd,
            input=message.encode(),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            module.fail_json(
                msg=f"mail command failed: {proc.stderr.decode().strip()}",
                changed=False,
            )
    except subprocess.TimeoutExpired:
        module.fail_json(msg="mail command timed out after 30s", changed=False)
    except FileNotFoundError:
        module.fail_json(msg="'mail' command not found — mailutils not installed?", changed=False)

    from_info = f" from {from_addr}" if from_addr else ""
    module.exit_json(changed=False, msg=f"Test email sent to {to}{from_info}")


if __name__ == "__main__":
    run_module()
