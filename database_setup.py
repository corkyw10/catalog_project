from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
	""" Registered users.

	All users are registered using google+ accounts 

	Attributes:
		id: unique id number
		name: string of users first name
		username: string of username, index and required information
		email: string of user email address, index and required information
		profile_image: string of url of users google profile image
	"""
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	username = Column(String, index=True, nullable=False)
	email = Column(String, index=True, nullable=False)
	profile_image = Column(String)


class Genre(Base):
	"""	Genre categories.

	A category of genres for books from table 'books' to be listed under.

	Attributes:
		id: unique ID integer, primary key
		genre: genre title string for books to be listed under

	API Data:
			id, genre
	"""
	__tablename__ = 'genres'

	id = Column(Integer, primary_key=True)
	genre = Column(String)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'genre': self.genre
		}
	

class Book(Base):
	""" Books contained in the library.
		
		Books contained in the library. Each book is linked 
		table 'genres' and to the user who created it in the table 'users'

		Attributes:
			id: unique id integer, primary key
			title: string of book title
			author: string of book author
			synopsis: string of book plot summary
			cover_image: string of url for image of book cover
			genre_id: foreign key integer relating to genre category the book is listed under
			genre: relationship declaration to 'genres' table
			user_id: foreign key integer relating to user who created book
			user: relationship declaration to 'users' table
		
		API Data:
			id, title, author, synopsis, cover_image, user_id, creator_username, genre

	"""
	__tablename__ = 'books'

	id = Column(Integer, primary_key=True)
	title = Column(String)
	author = Column(String)
	synopsis = Column(String)
	cover_image = Column(String)
	genre_id = Column(Integer, ForeignKey('genres.id'))
	genre = relationship(Genre)
	user_id = Column(Integer, ForeignKey('users.id'))
	creator = relationship(User)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'title': self.title,
			'author': self.author,
			'synopsis': self.synopsis,
			'cover_image': self.cover_image,
			'user_id': self.user_id,
			'creator': self.creator.username,
			'genre': self.genre.genre

		}	


engine = create_engine('sqlite:///library.db')

Base.metadata.create_all(engine)
