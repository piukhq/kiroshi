"""Basic Test for use in AIT to Confirm Kiroshi Image Server works."""

import hashlib
import json
import sys
from pathlib import Path

import requests

report = []

base_url = "http://kiroshi/content/"

known_images = [
    {"name": "bink.png", "md5": "a4c18cf88f80727a614bf476623c0644"},
    {"name": "holly.jpg", "md5": "b9d6a24fcaca936b8609ab772718deae"},
    {"name": "starbug.jpg", "md5": "df33e26308b049145ad54d442fdcc975"},
]

for image in known_images:
    r = requests.get(
        base_url + image["name"],
        headers={"container": "kiroshi-test"},
        timeout=10,
    )
    test_success = False
    if hashlib.md5(r.content).hexdigest == image["md5"]:  # noqa: S324
        test_success = True
    report.append({"name": image["name"], "test_passed": test_success})

report_file = Path("/mnt/reports/report.json")
report_file.touch()
report_file.open()
report_file.write(json.dumps(report, indent=4))
report_file.close()

for result in report:
    if result["test_passed"] is False:
        sys.exit(1)
