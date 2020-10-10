from pytube import YouTube
import logging


def strip_nonprintable(text):
    printable_text = text.encode('ascii', 'ignore')
    return printable_text.strip().decode('utf-8')


class GenericTrack:

    def __init__(self, author, title, filepath):
        self._author = author
        self._title = title
        self._filepath = filepath

    def get_author(self):
        return self._author

    def get_title(self):
        return self._title

    def get_filepath(self):
        return self._filepath


class TrackCollector:

    def __init__(self, base_download_path):
        self._base_download_path = base_download_path
        self._track_stream = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def acquire_metadata(self, track_link) -> GenericTrack:
        try:
            self._track_stream = YouTube(track_link).streams \
                .filter(only_audio=True) \
                .order_by('abr').desc().first()
        except KeyError as ex:
            self._logger.warning(ex)  # timestamp, classname, error, track_link
            raise ex
        return self._pack_details()

    def _pack_details(self) -> GenericTrack:
        author_title = self._track_stream.title.split(sep='-', maxsplit=1)
        author, title = map(strip_nonprintable, author_title)
        filepath = self._base_download_path + self._track_stream.default_filename
        return GenericTrack(author, title, filepath)

    def collect_acquired(self) -> None:
        self._track_stream.download(self._base_download_path)
