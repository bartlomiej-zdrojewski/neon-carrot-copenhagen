import os
import hashlib
from typing import Optional


class Cache:

    class CacheException(Exception):
        def __init__(self, message: str, source_exception: Exception = None):
            self.source_exception = source_exception
            super().__init__(message)

    def __init__(self, base_path: str = 'cache/'):
        self.__base_path = base_path
        try:
            if not os.path.exists(self.__base_path):
                os.makedirs(self.__base_path)
        except OSError as e:
            raise Cache.CacheException(
                'Could not create the cache directory: {}'.format(base_path), e)

    def __get_file_path(self, id: str) -> str:
        hash = hashlib.sha1()
        hash.update(id.encode('utf-8'))
        return os.path.join(self.__base_path, hash.hexdigest())

    def read(self, id: str) -> Optional[str]:
        data = None
        file_path = self.__get_file_path(id)
        try:
            file = open(file_path, 'r')
            data = file.read()
            file.close()
        except FileNotFoundError:
            pass
        except OSError as e:
            raise Cache.CacheException(
                'Could not read from the file: {}'.format(file_path), e)
        return data

    def write(self, id: str, data: str):
        file_path = self.__get_file_path(id)
        try:
            file = open(file_path, 'w')
            file.write(data)
            file.close()
        except OSError as e:
            raise Cache.CacheException(
                'Could not write to the file: {}'.format(file_path), e)

    def clear(self):
        for file_name in os.listdir(self.__base_path):
            file_path = os.path.join(self.__base_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                raise Cache.CacheException(
                    'Could not delete the file: {}'.format(file_path), e)
