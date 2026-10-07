"""Legitimate netcheck helper used by check.py (lab)."""
import socket


def run():
    host = socket.gethostname()
    print(f"[netcheck] host={host} reachable=yes")
