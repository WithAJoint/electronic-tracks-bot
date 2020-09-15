from peewee import SqliteDatabase, Model, CharField, ForeignKeyField


class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(None)


class Author(BaseModel):
    name = CharField(unique=True)


class Track(BaseModel):
    title = CharField()
    author = ForeignKeyField(Author, backref='author')
    filepath = CharField()


class CollectionManager:

    def __init__(self, db_path):
        self.__database = BaseModel._meta.database
        self.__database.init(db_path)
        self.__database.connect()
        self.__database.create_tables([Author, Track])

    
