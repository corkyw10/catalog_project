import json
import httplib2
import requests

from flask import make_response, Flask, jsonify, request, flash
from flask import url_for, render_template, redirect
from flask import session as login_session

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from database_setup import Base, User, Genre, Book

# connect to database with sqlalchemy
ENGINE = create_engine('sqlite:///library.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = ENGINE
DBSession = sessionmaker(bind=ENGINE)
session = DBSession()

# initialise flask
app = Flask(__name__)

# client ID for Google signin
CLIENT_ID = json.loads(open(
            'client_secrets.json', 'r').read())['web']['client_id']


@app.route('/genres/<int:genre_id>/<int:book_id>/JSON', methods=['GET'])
def bookJSON(genre_id, book_id):
    '''Return JSON of individual book information.'''
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=[book.serialize])


@app.route('/login')
def login():
    '''Google Signin Link.'''
    return render_template('login.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''Authentication code handling for Google Signin.'''
    auth_code = request.data
    # exchange auth_code for token
    try:
        # upgrade auth_code for credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(json.dumps(
                   'Failed to upgrade the authorization code'))
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

# Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(json.dumps(
                   "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
                   "Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_google_id = login_session.get('google_id')
    if stored_credentials is not None and google_id == stored_google_id:
        response = make_response(json.dumps(
                   'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # get user info
    h = httplib2.Http()
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # populate login_session with user information
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['first_name'] = data['given_name']
    login_session['google_id'] = data['id']
    login_session['access_token'] = access_token

    # create a new user if user doesn't exist.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return "Welcome %s" % login_session['first_name']


# Helper functions to get and create users
def createUser(login_session):
    '''Add new user to User database. Returns user.id'''
    user = User(username=login_session['username'],
                email=login_session['email'],
                profile_image=login_session['picture'],
                name=login_session['first_name'])
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    '''Return user information based on user_id'''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    '''Return user.id or none based on email stored in User database.'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    '''Wipe loginsession when user logs out.'''
    access_token = login_session.get('access_token')
    if access_token is None:
        print "Access token is none"
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['first_name']
        response = make_response(json.dumps(
                   'Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                   'Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/genres', methods=['GET'])
def getGenres():
    '''Returns template that shows all genres in catalog.'''
    genres = session.query(Genre).all()
    return render_template('genres.html', genres=genres,
                           login_session=login_session)


@app.route('/genres/<int:genre_id>', methods=['GET'])
def getBooksInGenre(genre_id):
    '''
    Return template that shows all books in a genre in catalog.
    If a user is not logged in return template without create option.
    '''
    books = session.query(Book).filter_by(genre_id=genre_id).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return render_template('publicbooks.html', books=books, genre=genre,
                               login_session=login_session)
    else:
        return render_template('books.html', books=books, genre=genre,
                               login_session=login_session)


@app.route('/genres/<int:genre_id>/new', methods=['GET', 'POST'])
def createBook(genre_id):
    '''
    Return template to create new book in catalog. If user not logged in
    redirects to login page.
    '''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            newBook = Book(title=request.form['title'],
                           author=request.form['author'],
                           synopsis=request.form['synopsis'],
                           cover_image=request.form['cover_image'],
                           genre_id=genre_id, user_id=login_session['user_id'])
            session.add(newBook)
            session.commit()
            flash("You added " + newBook.title + " to your library!")
            return redirect(url_for('getBook',
                                    genre_id=genre.id,
                                    book_id=newBook.id,
                                    login_session=login_session))
        else:
            return render_template('createbook.html', genre=genre,
                                   login_session=login_session)


@app.route('/genres/<int:genre_id>/<int:book_id>', methods=['GET'])
def getBook(genre_id, book_id):
    '''
    Return template to show a particular book in catalog with edit/delete
    options. If user not logged in return template without edit/delete
    options.
    '''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    book = session.query(Book).filter_by(id=book_id).first()
    creator = getUserInfo(book.user_id)
    if 'username' not in login_session or creator.id != login_session[
                                                        'user_id']:
        return render_template('publicbook.html',
                               book=book, genre=genre,
                               login_session=login_session,
                               creator=creator)
    else:
        return render_template('book.html', book=book, creator=creator,
                               genre=genre, login_session=login_session)


@app.route('/genres/<int:genre_id>/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(genre_id, book_id):
    '''
    Return template to edit a particular book in catalog. If user not
    logged in or user not creator of book, return alert saying user
    is not authorised.
    '''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    bookToEdit = session.query(Book).filter_by(id=book_id).first()
    if bookToEdit.user_id != login_session[
                             'user_id'] or 'username' not in login_session:
        return """<script>function myFunction() {alert('You are not authorised
                to edit this book. Please sign in.');} </script><body
                onload='myFunction()'>"""
    if request.method == 'POST':
        if request.form['title']:
            bookToEdit.title = request.form['title']
        if request.form['author']:
            bookToEdit.author = request.form['author']
        if request.form['synopsis']:
            bookToEdit.synopsis = request.form['synopsis']
        if request.form['cover_image']:
            bookToEdit.cover_image = request.form['cover_image']
        session.add(bookToEdit)
        session.commit
        flash("You edited " + bookToEdit.title + ".")
        return redirect(url_for('getBook', genre_id=genre_id, book_id=book_id,
                                login_session=login_session))
    else:
        return render_template('editbook.html', book=bookToEdit, genre=genre,
                               login_session=login_session)


@app.route('/genres/<int:genre_id>/<int:book_id>/delete',
           methods=['GET', 'POST'])
def deleteBook(genre_id, book_id):
    '''
    Return template to delete a particular book in catalog. If user not
    logged in or user not creator of book, return alert saying user
    is not authorised.
    '''
    genre = session.query(Genre).filter_by(id=genre_id).one()
    bookToDelete = session.query(Book).filter_by(id=book_id).first()
    if bookToDelete.user_id != login_session[
                               'user_id'] or 'username' not in login_session:
        return """<script>function myFunction() {alert('You are not authorised
                to delete this book. Please sign in.');} </script><body
                onload='myFunction()'>"""
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash("You have deleted " + bookToDelete.title + ".")
        return redirect(url_for('getGenres', login_session=login_session))
    else:
        return render_template('deletebook.html', deleteBook=bookToDelete,
                               login_session=login_session, genre=genre)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
app.run(host='0.0.0.0', port=8000)
