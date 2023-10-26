from peewee import *

database = PostgresqlDatabase(
    database="test_fastapi",
    user='postgres',
    password='postgress123',
    host='localhost',
    port=5433
)

class User(Model):
    username = CharField(max_length=50)
    email = CharField(max_length=50)

    def __str__(self):
        return self.username
    
    class Meta:
        database = database
        table_name = 'users'

class Persona(Model):
    nombre = TextField()
    globalId = TextField()
    x = DoubleField()
    y = DoubleField()
    
    class Meta:
        database = database
        table_name = 'personas'
        

class Integrante(Model):
    integrante = TextField()
    persona = ForeignKeyField(Persona, backref='integrantes')
    
    class Meta:
        database = database
        table_name = 'integrantes'

class Foto(Model):
    url =TextField()
    integrante = ForeignKeyField(Integrante, backref='fotos')
    
    class Meta:
        database = database
        table_name = 'fotos'