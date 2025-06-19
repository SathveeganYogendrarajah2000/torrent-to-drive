# Torrent to Drive

A simple script to download torrents (magnet links or .torrent files) and automatically upload the downloaded files to Google Drive using rclone.

## Prerequisites

- **Python 3.7+**
- **libtorrent** Python binding
    - Install via pip (may require build tools):
      ```sh
      pip install python-libtorrent
      ```
    - Or use your OS package manager (e.g., `apt install python3-libtorrent`)
- **rclone**
    - [Download and install rclone](https://rclone.org/downloads/)
    - Configure rclone with your Google Drive remote (see [rclone Google Drive setup](https://rclone.org/drive/))
    - Example remote name in this script: `gdrive`
- **Google Drive**
    - You must have a Google Drive account and have set up rclone access as above

## Usage

1. **Clone this repository or copy the script files.**
2. **Install the prerequisites** (see above).
3. **Run the script:**
    ```sh
    python main.py
    ```
4. **When prompted, enter a magnet link or path to a .torrent file.**
5. The script will:
    - Download all files from the torrent to the `./downloads` folder
    - Automatically upload the downloaded folder to Google Drive under `Torrent Uploads/` using rclone

## Example rclone command used by the script

```
rclone copy "./downloads/<folder>" "gdrive:Torrent Uploads/<folder>" --progress
```

- Replace `<folder>` with the actual name of the downloaded torrent folder.
- You can change the remote name or path in the script if needed.

## Notes
- Make sure rclone is in your system PATH so the script can call it.
- The script shows download and upload progress in the terminal.
- For best torrent performance, ensure your firewall allows ports 6881-6891.

## Notes to configure rclone
1. rclone config
2. remote name: gdrive
3. Storage: drive or 22
4. client_id: 
5. client_secret: 
6. scope:
7. Service account file:
8. Edit advanced config:
9. Use web browser: no
10. config token: <paste the token here>
```bash
Option config_token.
For this to work, you will need rclone available on a machine that has
a web browser available.
For more help and alternate methods see: https://rclone.org/remote_setup/
Execute the following on the machine with the web browser (same rclone
version recommended):
        rclone authorize "drive"
Then paste the result.
Enter a value.
config_token>
```
