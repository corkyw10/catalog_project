from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, User, Genre, Book

engine = create_engine('sqlite:///library.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

'''
If you'd like to populate the database with some books and a dummy user already, run `python populate_with_books.py`
in your python shell.
'''
user = User(name="Carson", username="McCullers46", email="theheart@lonelyhunter.com",
	profile_image="https://images.gr-assets.com/authors/1335451237p8/3506.jpg")
session.add(user)
session.commit()

theShining = Book(title="The Shining", author="Stephen King", synopsis="""Jack Torrance's new job at the Overlook
	Hotel is the perfect chance for a fresh start. As the off-season caretaker at the atmospheric old
	hotel, he'll have plenty of time to spend reconnecting with his family and working on his writing.
	But as the harsh winter weather sets in, the idyllic location feels ever more remote...and more sinister.
	And the only one to notice the strange and terrible forces gathering around the Overlook is Danny Torrance,
	a uniquely gifted five-year-old.""",
	cover_image="http://t3.gstatic.com/images?q=tbn:ANd9GcQd4A-1XPHd_4yqwcMfT86ExMyAo4u5t9kg8reVSg2zVmBqVreR", genre_id="1", user_id="1")
session.add(theShining)
session.commit()

androids = Book(title="Do Androids Dream of Electric Sheep?", author="Philip K. Dick", synopsis="""It was January 2021,
	and Rick Deckard had a license to kill. Somewhere among the hordes of humans out there, lurked several rogue androids.
	Deckard's assignment--find them and then..."retire" them. Trouble was, the androids all looked exactly like humans,
	and they didn't want to be found!""",
	cover_image="https://images.gr-assets.com/books/1357936711l/6696927.jpg", genre_id="2", user_id="1")
session.add(androids)
session.commit()

treasureIsland = Book(title="Treasure Island", author="Robert Louis Stevenson", synopsis="""Who can outsmart a pack
	of pirates and the murderous Long John Silver? Who is fearless enough to single-handedly board a ship and
	steal it back? Who else but the most daring lad of all -- young Jim Hawkins! Get ready for excitement and terror
	-- from the moment Jim finds a treasure map to the final hunt for buried gold.""",
	cover_image="https://images.gr-assets.com/books/1485248909l/295.jpg", genre_id="3", user_id="1")
session.add(treasureIsland)
session.commit()


print "Books added!"
