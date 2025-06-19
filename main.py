import os
import time
import libtorrent as lt
import subprocess


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
    }
    ses.apply_settings(settings)
    ses.listen_on(6881, 6891)
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


def main():
    # === Setup ===
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)

    # === Torrent Input ===
    torrent_input = input(
        "Enter magnet link or path to .torrent file: ").strip()

    # === Download ===
    downloaded_folder = download_torrent_files(
        torrent_input=torrent_input, save_path=download_dir)
    print(f"\nAll files downloaded to: {downloaded_folder}")

    # === Rclone Upload ===
    folder_name = os.path.basename(downloaded_folder)
    remote_path = f"gdrive:Torrent Uploads/{folder_name}"
    print(f"\nUploading to Google Drive using rclone...")
    rclone_cmd = [
        "rclone", "copy", downloaded_folder, remote_path, "--progress"
    ]
    subprocess.run(rclone_cmd)
    print("✅ Upload to Google Drive complete.")


if __name__ == "__main__":
    main()
