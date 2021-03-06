import shelve
import math

from datetime import datetime


class StoreMeta(type):
    _instances = {}

    def __call__(cls, name, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[name] = super(StoreMeta, cls).__call__(name, *args, **kwargs)

        return cls._instances[name]


class MemoryStore(metaclass=StoreMeta):
    __store = {}

    def __init__(self, name):
        self.name = name

    def __iter__(self):
        yield from self.__store

    def __setitem__(self, key, value):
        self.__store[key] = value

    def __getitem__(self, item):
        return self.__store.get(item)


class FileStore(metaclass=StoreMeta):
    path = ".aioli"

    def __init__(self, name, lifetime_secs=math.inf):
        self._name = name
        self._lifetime_secs = lifetime_secs

        with self._get_db() as db:
            if name not in db:
                db[self._name] = {}

    def _get_db(self, *args, **kwargs):
        return shelve.open(self.path, *args, writeback=True, **kwargs)

    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self, key):
        with self._get_db() as db:
            state = db[self._name]

            if key in state:
                update_time, data = state[key]
                if self._lifetime_secs > (datetime.now() - update_time).total_seconds():
                    return data

            return {}

    def __setitem__(self, key, value):
        with self._get_db() as db:
            state = db[self._name]

            if key not in state:
                state[key] = {}

            state[key] = datetime.now(), value
