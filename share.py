from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from flask_login import LoginManager, login_user, \
    logout_user, UserMixin, current_user, login_required
# from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from urltils import validate_url, clean
import urltils
from flask_cors import CORS, cross_origin
from flask import jsonify
from urllib.parse import unquote


# Initialize app and such
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///browse_together.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret key'
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Create the login helper object
login = LoginManager(app)

# Create an object to allow external queries
cors = CORS(app, resources={r"/api/*": {"origins": "chrome"}})

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@socketio.on('message')
def handle_send_message(message):
    print('sending', message)

    split_msg = message.split('~')
    message = split_msg[0]
    to_username = split_msg[1]
    to_user = db.session.query(User).filter_by(username=to_username).all()[0]

    # Construct a cleaned URL
    message = clean(message)

    print('message', message)

    if message is None:
        print('hey')
        flash('Not a valid URL. Message not sent.')

    # Create a message and store it in the databse
    message = draft_message(message, to_user, current_user)

    # Send the new message's html representation across the network
    send(message, broadcast=True)


def draft_message(message_data, to, from_user):
    """
    Create a message, commit it to the database and get it ready to send across the network.
    """

    # Create the message and add it to the database
    message = Message(text=message_data, sender_id=from_user.id, receiver_id=to.id)
    db.session.add(message)
    db.session.commit()

    return message.serialize()


def load_messages(sender=None, receiver=None):
    """Load the messages for a given user (or all messages if user=None)"""
    last_messages = []
    if sender or receiver:
        last_messages = db.session.query(Message).filter_by(sender_id=sender.id, receiver_id=receiver.id)
    else:
        query = db.session.query(Message).all()
        if query is not None:
            last_messages = query

    return [message.get_html() for message in last_messages]


def load_history(user):
    """Load the browsing history for a given user"""
    last_messages = db.session.query(Message).filter_by(sender_id=user.id, receiver_id=user.id)
    return [message.get_html(light=True) for message in last_messages]



@app.route('/')
def index():
    return render_template('index.html', title='Friends', users=db.session.query(User).all())


@app.route('/user/<username>')
def user(username=None):

    users = db.session.query(User).filter_by(username=username).all()
    if len(users) < 1:
        flash('Could not find user {}.'.format(username))
        return redirect(url_for('index'))

    # Get the first user (we presume there is only 1 user allowed for each username)
    other_user = users[0]

    if current_user.is_authenticated:

        return render_template('user.html', title=username, sent_from=current_user, to=other_user,
                               from_messages=load_messages(sender=other_user, receiver=current_user),
                               to_messages=load_messages(sender=current_user, receiver=other_user))
    else:
        return render_template('index.html')


@app.route('/history')
@login_required
def history():
    history_urls = load_history(current_user)
    return render_template('history.html', history=history_urls)


# noinspection PyArgumentList
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Thanks for registering')
        return redirect(url_for('index', user=user))
    print('did not register')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            user = db.session.query(User).filter_by(username=form.username.data).all()[0]
            login_user(user)
            flash('Logged in successfully.')
            print('Could not log in {}'.format(form.username.data))
            return redirect(url_for('index'))
        except Exception:
            print('Could not log in {}'.format(form.username.data))
            flash('Could not log in {}'.format(form.username.data))
    return redirect('register')


@app.route("/switch_user")
def press_switch_login():
    if current_user.is_authenticated:
        return redirect(url_for('logout'))
    else:
        return redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/api/register_url_change/", methods=['POST'])
@cross_origin()
def register_url_change():
    """
    Endpoint for the Chrome extension to call. Adds browsing info to database.
    """

    # Process data from request
    data = request.get_data()

    # Clean the data
    data = str(data.decode('utf8')).split('&')
    url_token = 'new_url='
    urls = [term for term in data if term.startswith(url_token)]

    if len(urls) == 1:  # A new URL was navigated to
        status = 'yo'

        # Get the url string without quote escapes
        url = [term for term in urls][0]
        url = unquote(url)
        url = url.replace(url_token, '')

        # Create a message, persist it to the database
        message = draft_message(url, me, me)

        # Send the new message's html representation across the network
        print('sending')
        send(message, broadcast=True)

    else:
        status = 'naw'

    response = {'yo': status}
    return jsonify(response)

"""
Database stuff
"""

# User <-> Message table
sends = db.Table('sends',
    db.Column('msg_id', db.Integer, db.ForeignKey('message.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.String(500), nullable=False)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Load card templates
    message_template = open('templates/iframe_card.html').read()
    history_template = open('templates/history_card.html').read()

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.text, self.sender_id)

    def get_html(self, light=False):
        """Return the HTML representation of the message with  bootstrap formatting"""

        # Get the name of the user that posted it
        # posted_by = db.session.query(User).get(self.sender_id)

        text = urltils.truncate(self.text)
        href = self.text

        if light:
            html = Message.history_template.format(text=text, href=href)
        else:
            html = Message.message_template.format(text=text, href=href)

        print(html)
        return html

    def serialize(self):
        return str(self.sender_id) + '~' + self.get_html()


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.equal_to('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('RepeatPassword')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    messages = db.relationship('Message', secondary='sends',
                               backref=db.backref('messages', lazy='dynamic'))


db.create_all()

me = None
them = None

me_name = 'Alex'
them_name = 'Alice'

try:
    me = db.session.query(User).filter_by(username=me_name).all()[0]
    them = db.session.query(User).filter_by(username=them_name).all()[0]

except Exception:
    pass

if not (me and them):
    me = User(username=me_name, password=me_name)
    them = User(username=them_name, password=them_name)

    db.session.add(them)
    db.session.add(me)
    db.session.commit()
