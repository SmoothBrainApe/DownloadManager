from download import DownloadManager
import pathlib


def main():
    try:
        download_dir = pathlib.Path("~/Downloads/DownloadManager").expanduser()
        dm = DownloadManager()
        if not download_dir.exists():
            download_dir.mkdir(parents=True)

        segments = int(input("Enter number of segments (default 16): ") or 16)
        max_connections = int(input("Enter max connections (default 16): ") or 16)
        max_concurrent_downloads = int(
            input("Enter max connections (default 3): ") or 3
        )
        dm.set_download_config(segments, max_connections, max_concurrent_downloads)

        urls = input("Enter the URLs to download: (seperated by spaces) ").split()
        dm.start_download_job(urls, download_dir)
    except ValueError as e:
        print(f"Invalid Input: {e}")
    except Exception as e:
        print(f"An error has occured: {e}")


if __name__ == "__main__":
    main()
