#!/usr/bin/python3
"""
Observ scheduled host health check.

Run (as configured in sudoers) by the developer account:
    sudo /usr/bin/python3 /opt/health/check.py

NOTE (lab): this is owned by root and not writable by developer. However the
sudo rule preserves PYTHONPATH, and this script imports the `netcheck`
helper module -- so a module of that name found earlier on the Python path
will be loaded with root privileges.
"""
import netcheck


def main():
    print("[observ] running host health check...")
    netcheck.run()
    print("[observ] health check complete.")


if __name__ == "__main__":
    main()
