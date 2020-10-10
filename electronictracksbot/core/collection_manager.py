from .collection_storage import DatabaseManager
from .tracks_collector import GenericTrack, TrackCollector


class CollectionTrack(GenericTrack):

    def __init__(self, author, title, filepath, is_new=False):
        super().__init__(author, title, filepath)
        self._is_new = is_new
        self._new_author = self._new_title = None

    def is_new(self):
        return self._is_new

    def edit_author(self, author):
        self._new_author = author

    def edit_title(self, title):
        self._new_title = title

    @staticmethod
    def create_from_generic(track: GenericTrack, is_new=True):
        return CollectionTrack(track.get_author(), track.get_title(), track.get_filepath(), is_new)


class CollectionManager:

    def __init__(self, db_path, download_path):
        self._tracks_collector = TrackCollector(download_path)
        self._database_manager = DatabaseManager(db_path)

    def collect_from_youtube(self, track_link) -> CollectionTrack:
        track = self._tracks_collector.acquire_metadata(track_link)
        if self._database_manager.exists_track(track.get_author(), track.get_title()):
            filepath = self._database_manager.retrieve_track_filepath(track.get_author(), track.get_title())
            return CollectionTrack(track.get_author(), track.get_title(), filepath)
        self._tracks_collector.collect_acquired()
        self._database_manager.insert_track(track.get_author(), track.get_title(), track.get_filepath())
        return CollectionTrack.create_from_generic(track)

    def update_track_details(self, track: CollectionTrack):
        pass
