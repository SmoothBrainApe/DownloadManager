import yt_dlp
import aria2p
import time
from tqdm import tqdm


class DownloadManager:
    def __init__(self, segments=8, max_connections=8, max_concurrent_downloads=3):
        self.aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret="",
            )
        )
        self.segments = segments
        self.max_connections = max_connections
        self.max_concurrent_downloads = max_concurrent_downloads
        self.video_platforms = ["youtube.com", "vimeo.com", "dailymotion.com"]

    def download_file(self, url, download_dir):
        if not url:
            raise ValueError("URL cannot be empty")
        options = {
            "split": str(self.segments),
            "max-connection-per-server": str(self.max_connections),
            "min-split-size": "1M",
            "dir": str(download_dir),
            "continue": "true",
            "max-concurrent-downloads": str(self.max_concurrent_downloads),
            "check-integrity": "true",
            "file-allocation": "falloc",
            "max-overall-download-limit": "0",
            "max-download-limit": "0",
            "disable-ipv6": "true",
            "auto-file-renaming": "true",
            "connect-timeout": "60",
            "max-tries": "5",
            "retry-wait": "10",
            "disk-cache": "64M",
            "allow-overwrite": "true",
            "allow-piece-length-change": "true",
            "async-dns": "false",
            "always-resume": "true",
            "content-disposition-default-utf8": "true",
        }
        try:
            download = self.aria2.add_uris([url], options=options)
            self.download_progress_display(download)
            print("download completed")
            return download
        except Exception as e:
            print(f"Error occured: {e}")

    def download_video(self, url, download_dir):
        if not url:
            raise ValueError("URL cannot be empty")
        ydl_opts = {
            "format": "bestaudio/best",
            "external_downloader": "aria2c",
            "external_downloader_args": [
                f"--split={self.segments}",
                f"--max-connection-per-server={self.max_connections}",
                "--min-split-size=1M",
                f"--max-concurrent-downloads={self.max_concurrent_downloads}",
                "--continue=true",
                "--check-integrity=true",
                "--file-allocation=falloc",
                "--max-overall-download-limit=0",
                "--max-download-limit=0",
                "--disable-ipv6=true",
                "--auto-file-renaming=true",
                "--connect-timeout=60",
                "--max-tries=5",
                "--retry-wait=10",
                "--disk-cache=64M",
                "--allow-overwrite=true",
                "--allow-piece-length-change=true",
                "--always-resume=true",
                "--async-dns=false",
                "--content-disposition-default-utf8=true",
            ],
            "outtmpl": f"{str(download_dir)}/%(title)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            download = ydl.download(url)
            self.download_progress_display(download)
            print("download completed")

    def start_download_job(self, url, download_dir):
        try:
            time.sleep(2)
            if self.is_video_url(url):
                self.download_video(url, download_dir)
            else:
                self.download_file(url, download_dir)
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    def is_video_url(self, url):
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        return any(platform in url for platform in self.video_platforms)

    def type_check(self, arg, attr_name):
        if arg is not None:
            if not isinstance(arg, int) or arg <= 0:
                raise ValueError(f"{arg} must be a positive integer")
            setattr(self, attr_name, arg)

    def set_download_config(
        self, segments=None, max_connections=None, max_concurrent_downloads=None
    ):
        self.type_check(segments, "segments")
        self.type_check(max_connections, "max_connections")
        self.type_check(max_concurrent_downloads, "max_concurrent_downloads")

    def download_progress_display(self, download):
        gid = download.gid
        pbar = tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading",
            bar_format="{desc}: {n_fmt}/{total_fmt} ({percentage:.1f}%) {rate_fmt}",
        )
        last_update_time = time.time()
        last_downloaded_size = 0
        while True:
            status = self.aria2.get_download(gid)
            total_size = status.total_length
            downloaded_size = status.completed_length

            if status.status == "complete":
                pbar.update(total_size - pbar.n)
                pbar.n = pbar.total
                pbar.set_postfix_str("(100%)")
                break

            if total_size > 0:
                if pbar.total is None:
                    pbar.total = total_size

                current_time = time.time()
                elapsed_time = current_time - last_update_time

                if elapsed_time > 0:
                    download_speed = (
                        downloaded_size - last_downloaded_size
                    ) / elapsed_time
                    pbar.set_postfix_str(f"(100%) {download_speed:.2f}B/s")
                last_update_time = current_time
                last_downloaded_size = downloaded_size

                pbar.update(downloaded_size - pbar.n)
                pbar.refresh()
                time.sleep(0.5)
            else:
                continue
        pbar.close()
