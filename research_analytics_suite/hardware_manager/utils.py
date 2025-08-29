"""
Utility functions for the hardware manager.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import re


def _to_gib(mem_val) -> float:
    """
    Convert various memory representations to GiB (float).
    Accepts:
      - int/float assumed to be bytes, KiB, or MiB (best-effort heuristic)
      - strings like '8192 MB', '8 GB', '1048576 KiB', '8589934592 bytes'
    """
    if isinstance(mem_val, (int, float)):
        # Heuristic: decide unit by magnitude
        if mem_val > 1024**4:      # > TiB in bytes? extremely unlikely for VRAM
            return mem_val / (1024**4)
        elif mem_val > 1024**3:    # looks like bytes
            return mem_val / (1024**3)
        elif mem_val > 1024**2:    # looks like KiB
            return mem_val / (1024**2)
        else:                       # treat as MiB if smallish
            return mem_val / 1024.0

    if isinstance(mem_val, str):
        s = mem_val.strip().lower()
        m = re.match(r'^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-z]+)?', s)
        if m:
            num = float(m.group(1))
            unit = (m.group(2) or '').strip()
            if unit in ('g', 'gb', 'gib'):
                return num
            if unit in ('m', 'mb', 'mib'):
                return num / 1024.0
            if unit in ('k', 'kb', 'kib'):
                return num / (1024.0**2)
            if unit in ('b', 'byte', 'bytes'):
                return num / (1024.0**3)
            # Unknown or missing unit: assume MiB if plausible
            return num / 1024.0
        # Fallback if unparsable
        raise ValueError(f"Unrecognized memory format: {mem_val!r}")

    raise TypeError(f"Unsupported memory type: {type(mem_val)}")
