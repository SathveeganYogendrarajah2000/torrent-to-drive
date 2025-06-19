import os
import time
import libtorrent as lt
from pydrive2.auth import GoogleAuth, ServiceAccountCredentials
from pydrive2.drive import GoogleDrive


def authenticate_gdrive(service_account_file: str) -> GoogleDrive:
    gauth = GoogleAuth()
    gauth.auth_method = 'service'
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return GoogleDrive(gauth)


def download_torrent_files(torrent_input: str, save_path: str) -> str:
    ses = lt.session()
    ses.listen_on(6881, 6891)

    if torrent_input.startswith("magnet:"):
        params = {"save_path": save_path}
        handle = lt.add_magnet_uri(ses, torrent_input, params)

        print("Downloading metadata...")
        while not handle.has_metadata():
            time.sleep(1)

        torrent_info = handle.get_torrent_info()
    else:
        torrent_info = lt.torrent_info(torrent_input)
        params = {"ti": torrent_info, "save_path": save_path}
        handle = ses.add_torrent(params)

    print("\nDownloading all files...")
    while not handle.is_seed():
        s = handle.status()
        print(
            f"\r{s.name} | {s.progress * 100:.2f}% | "
            f"{s.download_rate / 1000:.2f} kB/s | {s.state}", end=""
        )
        time.sleep(1)

    print(f"\n✅ Download complete.")
    return os.path.join(save_path, handle.name())


def upload_folder_to_drive(drive: GoogleDrive, local_folder: str, parent_folder_id: str = None):
    for root, _, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            f = drive.CreateFile({
                'title': file,
                'parents': [{'id': parent_folder_id}] if parent_folder_id else []
            })
            f.SetContentFile(file_path)
            f.Upload()
            print(f"☁️ Uploaded: {file}")


def main():
    # === Setup ===
    service_account_path = "service_account.json"
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)

    # === Auth ===
    print("🔐 Authenticating with Google Drive...")
    drive = authenticate_gdrive(service_account_path)

    # === Torrent Input ===
    torrent_input = input(
        "Enter magnet link or path to .torrent file: ").strip()

    # === Download ===
    downloaded_folder = download_torrent_files(
        torrent_input=torrent_input, save_path=download_dir)

    # === Upload ===
    print("\nUploading downloaded files to Google Drive...")
    upload_folder_to_drive(drive=drive, local_folder=downloaded_folder,
                           parent_folder_id="1Un8G9XSS_yUSv-396DPPQi-Y7NV0O2gJ")
    print("✅ All files uploaded successfully.")


if __name__ == "__main__":
    main()
