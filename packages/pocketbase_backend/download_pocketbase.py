"""
Download or update the latest PocketBase binary for the current platform.
Places the binary at packages/pocketbase_backend/pocketbase_bin[.exe].
"""
import os
import sys
import platform
import requests
import shutil
import zipfile
import tempfile

def get_latest_release():
    url = "https://api.github.com/repos/pocketbase/pocketbase/releases/latest"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_asset_url(release, platform_name, arch):
    for asset in release["assets"]:
        name = asset["name"].lower()
        if platform_name in name and arch in name:
            return asset["browser_download_url"], asset["name"]
    raise RuntimeError(f"No PocketBase binary found for {platform_name} {arch}")

def download_and_place(url, asset_name, dest_path):
    if url.endswith('.zip'):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, asset_name)
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if member.endswith('.exe') or member == 'pocketbase':
                        zip_ref.extract(member, tmpdir)
                        src = os.path.join(tmpdir, member)
                        shutil.move(src, dest_path)
                        os.chmod(dest_path, 0o755)
                        return
            raise RuntimeError("No executable found in PocketBase zip archive.")
    else:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        os.chmod(dest_path, 0o755)

def main():
    release = get_latest_release()
    system = platform.system().lower()
    arch = platform.machine().lower()
    if system == "windows":
        platform_name = "windows"
        ext = ".exe"
    elif system == "linux":
        platform_name = "linux"
        ext = ""
    elif system == "darwin":
        platform_name = "darwin"
        ext = ""
    else:
        raise RuntimeError(f"Unsupported OS: {system}")
    arch = "amd64" if "64" in arch else arch
    asset_url, asset_name = get_asset_url(release, platform_name, arch)
    dest = os.path.join(os.path.dirname(__file__), f"pocketbase_bin{ext}")
    print(f"Downloading PocketBase from {asset_url} to {dest} ...")
    download_and_place(asset_url, asset_name, dest)
    print("PocketBase binary downloaded and ready.")

if __name__ == "__main__":
    main()
