from backend.download import DownloadManager
import pathlib
import subprocess


def main():
    command = ["aria2c", "--enable-rpc", "--rpc-listen-all"]
    with subprocess.Popen(command) as process:
        try:
            download_dir = pathlib.Path("~/Downloads/DownloadManager").expanduser()
            dm = DownloadManager()
            if not download_dir.exists():
                download_dir.mkdir(parents=True)

            segments = int(input("Enter number of segments (default 8): ") or 8)
            max_connections = int(input("Enter max connections (default 8): ") or 8)
            max_concurrent_downloads = int(
                input("Enter max connections (default 3): ") or 3
            )
            dm.set_download_config(segments, max_connections, max_concurrent_downloads)

            urls = input("Enter the URLs to download: ")
            dm.start_download_job(urls, download_dir)
            pass
        except ValueError as e:
            print(f"Invalid Input: {e}")
            process.terminate()
        except Exception as e:
            print(f"An error has occured: {e}")
            process.terminate()


if __name__ == "__main__":
    main()
