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


def list_torrent_files(torrent_info: lt.torrent_info):
    print("\nFiles in torrent:")
    for i, f in enumerate(torrent_info.files()):
        print(f"{i}: {f.path} ({f.size / (1024 ** 2):.2f} MB)")


def select_file_indices(num_files: int) -> list[int]:
    selected = input(
        "\nEnter comma-separated file numbers to download (e.g., 0,2,3): ").strip()
    return [int(i) for i in selected.split(',') if i.strip().isdigit() and 0 <= int(i) < num_files]


def download_selected_files(torrent_input: str, save_path: str, selected_indices: list[int]) -> str:
    ses = lt.session()
    ses.listen_on(6881, 6891)

    if torrent_input.startswith("magnet:"):
        print("⚠️ File selection not supported for magnet links before metadata is downloaded.")
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

    # Set file priorities
    file_priorities = [0] * torrent_info.num_files()
    for idx in selected_indices:
        file_priorities[idx] = 1
    handle.prioritize_files(file_priorities)

    print("\nDownloading selected files...")
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
    torrent_input = input("Enter magnet link or path to .torrent file: ").strip()

    if not torrent_input.startswith("magnet:"):
        torrent_info = lt.torrent_info(torrent_input)
        list_torrent_files(torrent_info)
        selected = select_file_indices(torrent_info.num_files())
    else:
        selected = []

    # === Download ===
    downloaded_folder = download_selected_files(
        torrent_input, download_dir, selected)

    # === Upload ===
    print("\nUploading downloaded files to Google Drive...")
    upload_folder_to_drive(drive, downloaded_folder)
    print("✅ All selected files uploaded successfully.")


if __name__ == "__main__":
    main()
