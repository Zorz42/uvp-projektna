import requests
import os
import time
import hashlib

def _hash_string(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]

class Fetcher:
    def __init__(self, cache_dir: str = "cache", cache_timeout: int = 60 * 60):
        """
        Initializes the Fetcher with a cache directory and timeout.

        :param cache_dir: The directory where cached content will be stored.
        :param cache_timeout: The time in seconds after which the cache expires.
                             Default is 3600 seconds (1 hour).
        """
        self.cache_dir = cache_dir
        self.cache_timeout = cache_timeout

    def fetch(self, url: str) -> str:
        """
        Fetches the content from the given URL.
        If the URL is already cached, it retrieves
         the content from the cache. Cache is valid some time.
        If the cache is expired or does not exist,
        it fetches the content from the URL.

        :param url: The URL to fetch content from.
        :return: The content of the URL as a string.
        """
        hsh = _hash_string(url)
        cache_file = os.path.join(self.cache_dir, f"{hsh}.html")

        # Check if the cache file exists and is still valid
        if os.path.exists(cache_file):
            if time.time() - os.path.getmtime(cache_file) < self.cache_timeout:
                # Cache is valid, read from cache
                with open(cache_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                # Cache is expired, remove the old cache file
                os.remove(cache_file)

        content = requests.get(url).text

        os.makedirs(self.cache_dir, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(content)

        return content
