from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, User, Genre, Book

engine = create_engine('sqlite:///library.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Genres to populate library database
horror = Genre(genre='Horror')
session.add(horror)
session.commit()


scifi = Genre(genre='Science Fiction')
session.add(scifi)
session.commit()

actionAdventure = Genre(genre='Action and Adventure')
session.add(actionAdventure)
session.commit()

romance = Genre(genre='Romance')
session.add(romance)
session.commit()

mysteryCrime = Genre(genre='Mystery and Crime')
session.add(mysteryCrime)
session.commit()

travel = Genre(genre='Travel')
session.add(travel)
session.commit()

childrens = Genre(genre='Children\'s')
session.add(childrens)
session.commit()

history = Genre(genre='History')
session.add(history)
session.commit()

fantasy = Genre(genre='Fantasy')
session.add(fantasy)
session.commit()

thriller = Genre(genre='Thriller')
session.add(thriller)
session.commit()

drama = Genre(genre='Drama')
session.add(drama)
session.commit()

comics = Genre(genre='Comics and Graphic Novels')
session.add(comics)
session.commit()

biography = Genre(genre='Biography')
session.add(biography)
session.commit()

classic = Genre(genre='Classics')
session.add(classic)
session.commit()

print "Genres added to database!"



