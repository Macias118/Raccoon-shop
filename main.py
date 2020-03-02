from flask import Flask, render_template, request, flash, redirect, url_for, session
# from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from datetime import timedelta
import random
import string
import json
import mongoengine
from flask_mail import Mail, Message
from flask.json import JSONEncoder


app = Flask(__name__)
mongoengine.connect('book_library_database', host='localhost', port=27017)
app.secret_key = "book"
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Book(mongoengine.Document):
    title = mongoengine.StringField(required=True, max_length=100)
    author = mongoengine.StringField(required=True, max_length=200)
    genre = mongoengine.StringField(max_length=50)
    page_count = mongoengine.IntField(min_value=1)
    price = mongoengine.FloatField(min_value=0.01)

    def __str__(self):
        return f'{self.title} - {self.author}'


class User(mongoengine.Document):
    name = mongoengine.StringField(required=True, max_length=100)
    email = mongoengine.EmailField()
    email = mongoengine.StringField()
    password = mongoengine.StringField(required=True, max_length=200)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.name = kwargs['name']
        self.email = kwargs['email']
        self.password = kwargs['password']


# handle E-MAIL
# from resources.email import email_prop
# mail_settings = {
#     "DEBUG": True,
#     "MAIL_SERVER": "smtp.wp.pl",
#     "MAIL_PORT": 465,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": "maciej.rucinski6@wp.pl",
#     "MAIL_PASSWORD": "qwerty123"
# }
# app.config.update(mail_settings)
# mail = Mail(app)

@app.before_request
def before_request():
    # session.clear()
    if 'cart' not in session:
        session['cart'] = {}
    logged_in_user_id = session.get('user')
    if logged_in_user_id:
        session['username'] = User.objects.filter(id=logged_in_user_id).first().name

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['psswrd']
        if not user_name or not password:
            flash(f'User name or password empty!')
            return redirect(url_for('login'))

        found_user = User.objects.filter(name=user_name, password=password).first()

        if not found_user:
            flash(f'Incorrect user or password!')
            return redirect(url_for('login'))

        session['user'] = str(found_user.id)
        flash(f'Welcome {found_user.name}')

        return redirect(url_for('admin', users=User.objects.all()))

    if session.get('user'):
        return redirect(url_for('admin', users=User.objects.all()))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['psswrd']

        if not username or not email or not password:
            flash('Username, email and password can not be empty!')
            return render_template('signup.html')

        found_user = User.objects.filter(name=username)
        if found_user:
            flash('User already exists')
        else:
            new_user = User(
                name=username,
                email=email,
                password=password)
            new_user.save()
            flash('User created!')

    return render_template('signup.html')

@app.route('/admin')
def admin():
    if 'user' not in session:
        flash('You are not logged in')
        return redirect(url_for('login'))
    return render_template('admin.html', users=User.objects.all())

@app.route('/admin/delete/<user_id>', methods=['POST'])
def delete(user_id):
    User.objects.filter(id=user_id).delete()
    flash('User was removed!')
    if session.get('user') == user_id:
        logout()
        return redirect(url_for('login'))
    return redirect(url_for('admin', users=User.objects.all()))

def generate_random_string(n):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(n))

@app.route('/random/user', methods=['POST'])
def gen_user():
    n = 5
    username = generate_random_string(n)
    email = '{}@{}.com'.format(generate_random_string(5), generate_random_string(5))
    password = generate_random_string(5)
    new_user = User(
        name=username,
        email=email,
        password=password)
    new_user.save()
    flash('Random user generated!', 'info')
    return redirect(url_for('signup'))

@app.route('/admin/users/<user_id>', methods=['POST', 'GET'])
def user_detail(user_id):
    found_user = User.objects.filter(id=user_id).first()
    if not found_user:
        flash(f'There is not user with id: {user_name}')
        return redirect(url_for('admin', users=User.query.all()))
    if request.method == 'POST':
        found_user.name = request.form['name']
        found_user.email = request.form['email']
        found_user.password = request.form['psswrd']

        found_user.save()
    # return render_template('user_detail.html', user=found_user)
        return redirect(url_for('admin'))
    return render_template('user_detail.html', user=found_user)

@app.route('/logout')
def logout():
    username = session.get('username')
    flash(f'You have been logged out, {username}!', 'info')
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('login'))

def add_book(title, author, genre, page_count):
    b = Book(title, author, genre, page_count)
    b.save()

@app.route('/books')
def books():
    return render_template('books.html', books=Book.objects.all())

def get_keys_from_list_of_dicts(x: list) -> list:
    res = []
    for el in x:
        try:
            res.append(el.keys())
        except:
            return []
    return res

@app.route('/addToCart', methods=['POST'])
def addToCart():
    book_id = request.form['book_id']
    cart = session.get('cart')
    b = Book.objects.filter(id=book_id).first()
    if not b:
        flash(f'No book with id: {book_id}')
        return redirect(url_for('books'))

    cart[book_id] = cart.get(book_id, 0) + 1
    session['cart'] = cart

    return redirect(url_for('books'))

@app.route('/cart')
def show_cart():
    products = {}
    cart = session.get('cart')
    print(f'cart :: {cart}')
    for product_id, amount in cart.items():
        b = Book.objects.filter(id=product_id).first()
        products[b] = amount
    return render_template('cart.html', products=products)

@app.route('/cart/delete/<item_id>', methods=['POST'])
def remove_item_from_cart(item_id):
    cart = session.get('cart')
    if cart[item_id]:
        cart.pop(item_id, None)
        session['cart'] = cart
    return redirect(url_for('show_cart'))

@app.route('/send_order', methods=['GET'])
def send_order():
    flash('Functionality turned off... Soon available')
    return redirect(url_for('show_cart'))
    try:
        msg = Message(subject="Hello",
                      sender="maciej.rucinski6@wp.pl",
                      recipients=["maciej.rucinski118@gmail.com"], # replace with your email for testing
                      body="This is a test email I sent with Gmail and Python!")
        mail.send(msg)
    except Exception as e:
        print(f'error: {e}')

    return redirect(url_for('show_cart'))

if __name__ == '__main__':
    # load all books to database
    try:
        from resources.books import books
    except ModuleNotFoundError:
        err = 'There is no books in library'
        flash(err)
        print(err)
    else:
        for b in books:
            if not Book.objects.filter(title=b['title'], author=b['author']):
                new_book = Book(
                    title=b['title'],
                    author=b['author'],
                    genre=b['genre'],
                    page_count=b['page_count'],
                    price=b['price'])
                new_book.save()

    app.run(debug=True, threaded=True)
