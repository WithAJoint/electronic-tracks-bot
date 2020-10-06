from pytube import YouTube
from electronictracksbot.collection_storage import CollectionManager


class TracksCollector:

    def __init__(self, db_path, base_download_path):
        self._base_download_path = base_download_path
        self._collection_manager = CollectionManager(db_path)
        self._track = None

    def acquire_metadata(self, track_link) -> None:
        self._track = YouTube(track_link).streams \
            .filter(only_audio=True) \
            .order_by('abr').desc().first()
        self._extract_author_title()

    def _extract_author_title(self):
        author_title = self._track.title.split(sep='-', maxsplit=1)
        if len(author_title) > 0:
            self._author, self._title = map(lambda x: x.strip(), author_title)
        else:
            raise RuntimeError('Error occurred while retrieving track author and title')

    def get_author(self) -> str:
        return self._author

    def get_title(self):
        return self._title

    def get_track_filepath(self):
        return self._collection_manager.get_track_filepath(self._author, self._title)

# scan for duplicate
# download track and convert format
# send new track
