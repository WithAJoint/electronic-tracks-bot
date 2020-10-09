from .collection_storage import DatabaseManager
from .tracks_collector import TracksCollector


class Track:

    def __init__(self, author, title, filepath=None, is_new=False):
        self._author = author
        self._title = title
        self._filepath = filepath
        self._is_new = is_new

    def get_author(self):
        return self._author

    def get_title(self):
        return self._title

    def get_filepath(self):
        return self._filepath

    def is_new(self):
        return self._is_new


class CollectionManager:

    def __init__(self, db_path, download_path):
        self._tracks_collector = TracksCollector(download_path)
        self._database_manager = DatabaseManager(db_path)

    def collect_from_youtube(self, track_link) -> Track:
        self._tracks_collector.acquire_metadata(track_link)
        author = self._tracks_collector.get_author()
        title = self._tracks_collector.get_title()
        if self._database_manager.exists_track(author, title):
            filepath = self._database_manager.retrieve_track_filepath(author, title)
            return Track(author, title, filepath)
        self._tracks_collector.collect_acquired()
        filepath = self._tracks_collector.get_filepath()
        self._database_manager.insert_track(author, title, filepath)
        return Track(author, title, filepath, is_new=True)
