"""Shared design data for lab 2: GUID -> components, pins and nets.

GUID is generated deterministically from the student's full name with
uuid5 (SHA-1 hash, namespace DNS), so it can always be reproduced.
"""
import uuid
from collections import OrderedDict

FULL_NAME = "Микитич Михайло Васильович"
GUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, FULL_NAME))
GROUPS = GUID.split("-")


def components():
    """[(ref, chars, side_mm)]"""
    return [(f"U{i}", g, len(g)) for i, g in enumerate(GROUPS, 1)]


def pin_map():
    """char -> list of (ref, pin_number)"""
    m = OrderedDict()
    for ref, chars, _ in components():
        for n, ch in enumerate(chars, 1):
            m.setdefault(ch, []).append((ref, n))
    return m


def nets():
    """Returns (connected, free).

    connected: OrderedDict net_name -> [(ref, pin)] for characters that occur
               at least twice (same character = equivalent / connected pins).
    free:      list of (char, ref, pin) for characters that occur only once;
               they are routed to the edge connector J1.
    """
    connected, free = OrderedDict(), []
    for ch, pins in sorted(pin_map().items()):
        if len(pins) > 1:
            connected[f"N_{ch.upper()}"] = pins
        else:
            free.append((ch, *pins[0]))
    return connected, free


def all_nets():
    """net_name -> [(ref, pin)], including the J1 nets of free pins."""
    connected, free = nets()
    result = OrderedDict(connected)
    for j, (ch, ref, pin) in enumerate(free, 1):
        result[f"FREE_{ch.upper()}"] = [(ref, pin), ("J1", j)]
    return result


if __name__ == "__main__":
    print("Full name:", FULL_NAME)
    print("GUID     :", GUID)
    for ref, chars, side in components():
        print(f"{ref}: group '{chars}' -> {len(chars)} chars -> {side} x {side} mm, {len(chars)} pins")
    connected, free = nets()
    print("\nConnected nets:")
    for n, pins in connected.items():
        print(f"  {n:6} {', '.join(f'{r}.{p}' for r, p in pins)}")
    print("\nFree pins -> J1:")
    for j, (ch, ref, pin) in enumerate(free, 1):
        print(f"  '{ch}' {ref}.{pin} -> J1.{j}")
