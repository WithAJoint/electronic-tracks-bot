from peewee import SqliteDatabase, Model, CharField, ForeignKeyField


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(None)


class Author(BaseModel):
    name = CharField(unique=True)
    formatted_name = CharField(null=True)


class Track(BaseModel):
    title = CharField()
    formatted_title = CharField()
    author = ForeignKeyField(Author, backref='tracks')
    filepath = CharField()

    class Meta:
        indexes = (
            (('title', 'author_id'), True),
        )


class DatabaseManager:
    _cached_track = None

    def __init__(self, db_path):
        self._database = BaseModel._meta.database
        self._database.init(db_path)
        self._database.connect()
        self._database.create_tables([Author, Track])

    def insert_track(self, author_name, title, filepath):
        query_response = Author.get_or_create(name=author_name.lower())
        author = query_response[0]
        self._cached_track = Track.create(title=title.lower(), formatted_title=title, author=author, filepath=filepath)
        author.formatted_name = author_name
        author.save()

    def update_track(self, author_name, title, new_author, new_title):
        pass

    def exists_track(self, author_name, title) -> bool:
        try:
            author = Author.get(name=author_name.lower())
            track = Track.get(title=title.lower(), author=author)
        except (Author.DoesNotExist, Track.DoesNotExist):
            return False
        self._cached_track = track
        return True

    def retrieve_track_filepath(self, author_name=None, title=None) -> str:
        if author_name and title:
            if not self.exists_track(author_name, title):
                return ''
        return self._cached_track.filepath
