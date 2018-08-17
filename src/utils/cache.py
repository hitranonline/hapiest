import errno
import time
from datetime import timedelta
from typing import Callable, Any, Union, Optional

import json

from utils.log import err_log
from utils.metadata.config import Config


class Cache:
    """
    This is a small utility class for caching web results. When caching for the first time, it will download the a file
    by calling the web_fetch_routine (that is, you still have to write that part yourself). This result (if everything
    went smoothly) will then be stored in a file and given a timestamp that represents the unix-timestamp when that
    cache item should be re-downloaded.

    This is not meant to be an extremely time-precise cache. It is going to be used for things that should be
    re-downloaded daily.
    """

    ##
    # Where all cached files are stored. This is to be a subdirectory in the data directory as defined in
    # the use Config.
    CACHE_ROOT = ".cache"

    def __init__(self, path: str, web_fetch_routine: Callable[[], Union[str, bytes, Any]], lifetime: timedelta):
        """

        :param path: The path, starting from the cache root, of the file that the cache should be located or stored.
        :param web_fetch_routine: A function which will return a string on success, and something else otherwise. The
                something else can be retrieved using the err function. web_fetch_routine should not throw any
                exceptions, and should return a string or bytes on success, and anything else will be considered a
                failure.
        :param lifetime: A duration, after which, the cached results should be thrown out and re-retrieved. Therefore it
                is the lifetime of the cached data!
        """

        self.path = "{}/{}/{}".format(Config.data_folder, Cache.CACHE_ROOT, path)
        self.web_fetch_routine = web_fetch_routine
        self.cached: Optional[str] = None
        self.lifetime: int = lifetime.total_seconds()
        self.__err = None

        if not self.__load_from_file() and not self.__load_from_web():
            if self.__err is None:
                self.__err = Exception("Failed to initialize cache from file and web.")

    def __load_from_file(self) -> bool:
        """
        Attempts to load the cache from a file. If the containing directories don't exist they're created, and then the
        __load_from_web function will be called.
        :return: Returns False if the function failed to load the file. This either means it doesn't exist or something
                weird happened
        """
        import os.path

        path, _ = os.path.split(self.path)

        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Encountered unrecoverable exception in utils.cache.py: __load_from_file")
                return False
        if os.path.exists(self.path) and os.path.isfile(self.path):
            try:
                with open(self.path, 'r') as file:
                    text = file.read()  # This reads whole contents of the file.
                parsed = json.loads(text)
                # This means the lifetime of the cache has expired (parsed['timestamp'] contains the unix timestamp of
                # when the file was written added to the number of seconds before expiration).
                if int(time.time()) > parsed['timestamp']:
                    return False
                self.cached = parsed['cached']
            except Exception as e:
                err_log("Encountered exception '{}'".format(str(e)))
                return False
        else:
            return False

        return True

    def __load_from_web(self) -> bool:
        """
        Attempts to run the web fetch routine, and store the results in a file with a timestamp.
        :return: True if the data was successfully retrieved, False otherwise.
        """
        res = self.web_fetch_routine()
        if type(res) in [str, bytes]:
            self.cached = res
            if type(res) == bytes:
                self.cached = res.decode()
        else:
            self.__err = res
            return False
        try:
            with open(self.path, 'w+') as file:
                file.write(json.dumps({
                    'timestamp': int(time.time()) + self.lifetime,
                    'cached': self.cached
                }))
        except Exception as e:
            print('Failed to write to CrossSectionMeta cache: {}'.format(str(e)))
        return True

    def err(self) -> Any:
        """
        :return: None if there is no error to report, otherwise it returns the error.
        """
        return self.__err

    def ok(self) -> bool:
        """
        :return: True if there was no error when loading the cache.
        """
        return self.__err is None

    def data(self) -> str:
        """
        :return: The cached data, if it exists. If `self.ok()` returns true this should return a str. Otherwise, it
                will return None.
        """
        return self.cached


class JsonCache(Cache):
    """
    Just like `Cache`, except it parses the data as if it were JSON before returning it.
    """

    def __init__(self, path: str, web_fetch_routine: Callable[[], Union[str, Any]], lifetime: timedelta):
        Cache.__init__(self, path, web_fetch_routine, lifetime)

    def data(self) -> Any:
        """
        :return: The cached data as parsed JSON. Will return None if there is no cached data (i.e. something went wrong)
        or if the data is invalid JSON.
        """
        try:
            res = json.loads(self.cached)
            return res
        except:
            return None
