import sys
import os
import requests

from utils.file import chdir_project_root
import shutil
import subprocess
import zipfile
import hashlib

chdir_project_root()

release_url = "https://raw.githubusercontent.com/bangumi/Archive/refs/heads/master/aux/latest.json"
release = requests.get(release_url).json()
print(f"Latest dump file: {release['name']}")

download_url = release["browser_download_url"]
print(f"Downloading dump file from {download_url} ...")
dest_dir = "bangumi/dump_converter"
os.makedirs(dest_dir, exist_ok=True)
dest_path = os.path.join(dest_dir, release["name"])

for file in os.listdir(dest_dir):
    if file.endswith(".zip"):
        if file != release["name"]:
            print(f"Removing old dump file {file} ...")
            os.remove(os.path.join(dest_dir, file))

if (
    os.path.exists(dest_path)
    and "sha256:" + hashlib.sha256(open(dest_path, "rb").read()).hexdigest()
    == release["digest"]
):
    print(f"Dump file already exists at {dest_path}, skipping download.")
else:
    aria2 = shutil.which("aria2c") or shutil.which("aria2c.exe")
    if aria2:
        print("aria2c found, using aria2c for downloading...")
        try:
            subprocess.run(
                [
                    aria2,
                    "-x",
                    "16",
                    "-s",
                    "16",
                    "-o",
                    release["name"],
                    "-d",
                    dest_dir,
                    download_url,
                    "--allow-overwrite=true",
                ],
                check=True,
            )
        except Exception:
            # fallback to requests if aria2c fails
            file = requests.get(download_url, stream=True)
            with open(dest_path, "wb") as f:
                for chunk in file.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    else:
        file = requests.get(download_url, stream=True)
        with open(dest_path, "wb") as f:
            for chunk in file.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    if os.path.exists(dest_path):
        print(f"Dump file downloaded to {dest_path}")
    else:
        print("Download failed!", file=sys.stderr)
        sys.exit(1)

with zipfile.ZipFile(dest_path, 'r') as zip_ref:
    for file in zip_ref.namelist():
        if file in [
            "character.jsonlines",
            "subject-characters.jsonlines",
            "subject.jsonlines",
        ]:
            print(f"Extracting {file} ...")
            zip_ref.extract(file, dest_dir)

# os.remove(dest_path)
