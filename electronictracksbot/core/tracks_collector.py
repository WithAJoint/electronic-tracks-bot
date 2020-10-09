from pytube import YouTube
import logging


def strip_nonprintable(text):
    printable_text = text.encode('ascii', 'ignore')
    return printable_text.strip().decode('utf-8')


class TracksCollector:

    def __init__(self, base_download_path):
        self._base_download_path = base_download_path
        self._track = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def acquire_metadata(self, track_link) -> None:
        try:
            self._track = YouTube(track_link).streams \
                .filter(only_audio=True) \
                .order_by('abr').desc().first()
        except KeyError as ex:
            self._logger.warning(ex)  # timestamp, classname, error, track_link
            raise ex
        self._extract_author_title()

    def _extract_author_title(self):
        author_title = self._track.title.split(sep='-', maxsplit=1)
        self._author, self._title = map(strip_nonprintable, author_title)

    def collect_acquired(self):
        self._track.download(self._base_download_path)

    def get_author(self) -> str:
        return self._author

    def get_title(self):
        return self._title

    def get_filepath(self):
        return self._base_download_path + self._track.default_filename
