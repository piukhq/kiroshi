"""Basic Test for use in AIT to Confirm Kiroshi Image Server works."""

import hashlib
import json
import sys
from pathlib import Path

import requests

# Loop forever until the pod is ready
while True:
    try:
        requests.get("http://kiroshi/readyz", timeout=10).raise_for_status()
        break
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.HTTPError:
        pass

report = []

base_url = "http://kiroshi/content/"

images = [
    {"name": "bink.png", "md5": "a4c18cf88f80727a614bf476623c0644", "available": True},
    {"name": "holly.jpg", "md5": "b9d6a24fcaca936b8609ab772718deae", "available": True},
    {"name": "starbug.jpg", "md5": "df33e26308b049145ad54d442fdcc975", "available": True},
    {"name": "starbug1.jpg", "md5": "df33e26308b049145ad54d442fdcc75", "available": False},
]

for image in images:
    r = requests.get(
        base_url + image["name"],
        headers={"container": "kiroshi-test"},
        timeout=10,
    )
    test_success = False
    md5 = hashlib.md5(r.content).hexdigest()  # noqa: S324
    print(base_url + image["name"])  # noqa: T201
    print(md5)  # noqa: T201
    print(image["md5"])  # noqa: T201
    print(r.status_code)  # noqa: T201

    """Negative Test when an Image is not available and
     Happy Path Test when an Image is available"""

    if r.status_code == 404 and image["available"] is False:
        test_success = True

    elif md5 == image["md5"]:
        test_success = True

    report.append({"name": image["name"], "test_passed": test_success})

Path("/mnt/reports/report.json").write_text(json.dumps(report, indent=4))

for result in report:
    if result["test_passed"] is False:
        sys.exit(1)
