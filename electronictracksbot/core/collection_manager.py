from .collection_storage import DatabaseManager
from .tracks_collector import GenericTrack, TrackCollector


class CollectionTrack(GenericTrack):

    def __init__(self, author, title, filepath, is_new=False):
        super().__init__(author, title, filepath)
        self._is_new = is_new

    def is_new(self):
        return self._is_new

    def edit(self, *, author=None, title=None):
        if author:
            self._author = author
        elif title:
            self._title = title

    @staticmethod
    def create_from_generic(track: GenericTrack, is_new=True):
        return CollectionTrack(track.get_author(), track.get_title(), track.get_filepath(), is_new)


class CollectionManager:

    def __init__(self, db_path, download_path):
        self._tracks_collector = TrackCollector(download_path)
        self._database_manager = DatabaseManager(db_path)

    def preview_details(self, track_link) -> CollectionTrack:
        track = self._tracks_collector.acquire_metadata(track_link)
        return CollectionTrack.create_from_generic(track)

    def collect_if_new(self, track: CollectionTrack, duplication=False) -> CollectionTrack:
        if self._database_manager.exists_track(track.get_author(), track.get_title()) and not duplication:
            filepath = self._database_manager.retrieve_track_filepath(track.get_author(), track.get_title())
            return CollectionTrack(track.get_author(), track.get_title(), filepath)
        self._tracks_collector.collect_acquired()
        self._database_manager.insert_track(track.get_author(), track.get_title(), track.get_filepath())
        return track
