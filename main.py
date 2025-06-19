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

    # Configure session for better performance
    settings = {
        'enable_dht': True,
        'enable_lsd': True,
        'enable_upnp': True,
        'enable_natpmp': True,
        'announce_to_all_trackers': True,
        'announce_to_all_tiers': True,
        'connection_speed': 200,
        'max_out_request_queue': 500,
        'max_allowed_in_request_queue': 200,
        'max_failcount': 3,
        'min_reconnect_time': 2,
        'send_buffer_watermark': 500000,
        'send_buffer_low_watermark': 100000,
        'connection_speed': 200,
        'max_out_request_queue': 500,
        'max_allowed_in_request_queue': 200,
        'max_failcount': 3,
        'min_reconnect_time': 2,
        'send_buffer_watermark': 500000,
        'send_buffer_low_watermark': 100000,
    }
    ses.apply_settings(settings)

    # Listen on multiple ports for better connectivity
    ses.listen_on(6881, 6891)

    # Add DHT routers for better peer discovery
    dht_routers = [
        ('router.bittorrent.com', 6881),
        ('router.utorrent.com', 6881),
        ('dht.transmissionbt.com', 6881),
    ]
    for router, port in dht_routers:
        ses.add_dht_router(router, port)

    if torrent_input.startswith("magnet:"):
        params = {"save_path": save_path}
        handle = lt.add_magnet_uri(ses, torrent_input, params)

        print("Downloading metadata...")
        while not handle.has_metadata():
            time.sleep(1)
            s = handle.status()
            print(f"\rWaiting for metadata... State: {s.state}", end="")

        torrent_info = handle.get_torrent_info()
        print(f"\n✅ Metadata received: {torrent_info.name()}")
    else:
        torrent_info = lt.torrent_info(torrent_input)
        params = {"ti": torrent_info, "save_path": save_path}
        handle = ses.add_torrent(params)

    print("\nDownloading all files...")
    while not handle.is_seed():
        s = handle.status()
        peers = s.num_peers
        seeds = s.num_seeds
        print(
            f"\r{s.name} | {s.progress * 100:.2f}% | "
            f"{s.download_rate / 1000:.2f} kB/s | "
            f"Peers: {peers} | Seeds: {seeds} | State: {s.state}", end=""
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
