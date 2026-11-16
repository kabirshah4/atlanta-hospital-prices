"""Download the hospitals' price files (about 3.2 GB) into data/raw/.

Each hospital lists its machine-readable price file in /cms-hpt.txt on its website, as
required by CMS. We read those index files and download the 18 hospitals we use.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
SITES = ["emoryhealthcare.org", "piedmont.org", "wellstar.org", "gradyhealth.org"]
HOSPITALS = [line.strip() for line in (ROOT / "data" / "index" / "selected.txt").read_text().splitlines()
             if line.strip() and not line.startswith("Northside")]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def index_entries(site):
    text = get(f"https://www.{site}/cms-hpt.txt").decode("utf-8", "ignore").replace("\r", "")
    name = None
    for line in text.splitlines():
        if line.startswith("location-name:"):
            name = line.split(":", 1)[1].strip()
        elif line.startswith("mrf-url:") and name:
            yield name, line.split(":", 1)[1].strip()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for site in SITES:
        for name, url in index_entries(site):
            if name not in HOSPITALS:
                continue
            out = RAW / (name.replace(" ", "_").replace("'", "") + ".csv")
            if out.exists():
                continue
            print("downloading", name)
            body = get(url)
            if body[:2] == b"PK":  # zipped
                with zipfile.ZipFile(io.BytesIO(body)) as z:
                    body = z.read([n for n in z.namelist() if n.endswith(".csv")][0])
            out.write_bytes(body)


if __name__ == "__main__":
    main()
