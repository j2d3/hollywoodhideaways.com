#!/usr/bin/env python3
"""Write availability.json from the two Airbnb iCal exports.

Usage: ICAL_DELONGPRE=... ICAL_CHEROKEE=... scripts/availability.py
Output: {"units": {"delongpre": {"blocked": [[start, end], ...], "window": [s, e] | null}, ...}, "fetched": iso}

End dates are the checkout day (exclusive), as in the feed. Airbnb emits everything past
its 9-month booking window as one "Not available" block running to the feed horizon; that
trailing range merges with any manual block inside it, so it is returned separately as
"window" and the page treats it as "inquire to hold" rather than "taken".
"""
import json, os, re, sys, urllib.request
from datetime import date, datetime, timezone

def parse(text):
    text = text.replace("\r\n ", "").replace("\n ", "")
    out = []
    for block in text.split("BEGIN:VEVENT")[1:]:
        s = re.search(r"^DTSTART(?:;VALUE=DATE)?:(\d{8})", block, re.M)
        e = re.search(r"^DTEND(?:;VALUE=DATE)?:(\d{8})", block, re.M)
        if s and e:
            f = lambda d: f"{d[:4]}-{d[4:6]}-{d[6:]}"
            out.append([f(s.group(1)), f(e.group(1))])
    return sorted(out)

def split_window(ranges):
    if not ranges:
        return ranges, None
    last, horizon = ranges[-1], max(e for _, e in ranges)
    if last[1] == horizon and date.fromisoformat(last[0]).toordinal() >= date.today().toordinal() + 240:
        return ranges[:-1], last
    return ranges, None

units = {}
for key in ("delongpre", "cherokee"):
    url = os.environ.get("ICAL_" + key.upper())
    if not url:
        sys.exit(f"missing ICAL_{key.upper()}")
    req = urllib.request.Request(url, headers={"User-Agent": "hollywoodhideaways-availability/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        blocked, window = split_window(parse(r.read().decode("utf-8", "replace")))
    units[key] = {"blocked": blocked, "window": window}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "availability.json")
json.dump({"units": units, "fetched": datetime.now(timezone.utc).isoformat(timespec="seconds")}, open(out, "w"), indent=1)
print(json.dumps({k: (len(v["blocked"]), v["window"]) for k, v in units.items()}))
