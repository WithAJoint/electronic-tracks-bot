from peewee import SqliteDatabase, Model, CharField, ForeignKeyField


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(None)


class Author(BaseModel):
    name = CharField(unique=True)
    formatted_name = CharField()


class Track(BaseModel):
    title = CharField()
    formatted_title = CharField()
    author = ForeignKeyField(Author, backref='tracks')
    filepath = CharField()


class CollectionManager:

    def __init__(self, db_path):
        self.__database = BaseModel._meta.database
        self.__database.init(db_path)
        self.__database.connect()
        self.__database.create_tables([Author, Track])

    def add_track(self, author, title):
        author_id = Author.get_or_create(name=author);
        Track.create(title=title, author=author_id, filepath='test')

    def contains_track

