import requests
import os
import time
import hashlib

# Convert a string to a short hash
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
        self.session = requests.Session()
        self.num_requests = 0

    def fetch(self, url: str, cache_timeout: int = None) -> str:
        """
        Fetches the content from the given URL.
        If the URL is already cached, it retrieves
         the content from the cache. Cache is valid some time.
        If the cache is expired or does not exist,
        it fetches the content from the URL.

        :param url: The URL to fetch content from.
        :param cache_timeout: Optional timeout for this specific fetch call.
                              If None, uses the instance's cache_timeout.
        :return: The content of the URL as a string.
        """
        cache_timeout = cache_timeout if cache_timeout is not None else self.cache_timeout
        hsh = _hash_string(url)
        cache_file = os.path.join(self.cache_dir, f"{hsh}.html")

        # Check if the cache file exists and is still valid
        if os.path.exists(cache_file):
            if time.time() - os.path.getmtime(cache_file) < cache_timeout:
                # Cache is valid, read from cache
                with open(cache_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                # Cache is expired, remove the old cache file
                os.remove(cache_file)

        try:
            # Fetch the content from the URL
            content = self.session.get(url).text
            print("Fetching url", url)
            self.num_requests += 1
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(content)
        except requests.exceptions.ConnectionError as e:
            # If there was a connection error, just read the old file (if it exists)

            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                raise e

        return content

    def get_num_requests(self) -> int:
        """
        Returns the number of requests made by this Fetcher instance.

        :return: The number of requests.
        """
        return self.num_requests
