from flask import Flask, render_template, redirect, url_for, request, flash
from flask_socketio import SocketIO, send
from flask_login import LoginManager, login_user, \
    logout_user, current_user, login_required
from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, validators
from flask_cors import CORS, cross_origin
from flask import jsonify
from urllib.parse import unquote
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Process

# Initialize app and such
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///browse_together.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'super secret keysssss'
socketio = SocketIO(app)
db = SQLAlchemy(app)


# Provide a way for models.py (and any other files that needs it) to get access to the database
def get_db():
    return db


# Now you can import models.py because it can use this database
from . import utils, models
from .models import User, Group, get_groups, create_group, \
    store_url_browse_event, load_history, load_messages


app.app_context().push()

# Create the login helper object
login = LoginManager(app)

# Create an object to allow external queries
cors = CORS(app, resources={r"/api/*": {"origins": "chrome-extension"}})

stoplist = ['/']

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
    message = utils.clean(message)

    if message is None:
        flash('Not a valid URL. Message not sent.')

    # Create a new link and store it in the databse
    # message = store_url_browse_event(message, current_user)

    # Send the new message's html representation across the network
    send(message, broadcast=True)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('not_signed_in.html')

    groups = get_groups(current_user)
    agl = models.get_active_group_list(groups, None)
    return render_template('index.html', groups=groups, active_group_list=agl)


@app.route('/new_group/', methods=['GET', 'POST'])
def new_group():
    if not current_user.is_authenticated:
        return redirect('register')

    # Instantiate a WTForms form
    form = NewGroupForm(request.form)

    # Set list of available users to add to the group
    form.member1.choices = \
        form.member2.choices = \
        form.member3.choices = \
        [('', '')] + models.get_friends(current_user)

    if request.method == 'POST' and form.validate():

        name = form.group_name.data
        groups = db.session.query(Group).filter_by(name=name).all()
        error = False

        if not utils.validate_group_name(name, stoplist):
            form.group_name.errors.append('Name cannot include the following characters ' + str(stoplist))
            error = True

        if len(groups) >= 1:
            form.group_name.errors.append('A group with that name already exists.')
            error = True

        if form.member1.data == '':
            form.member1.errors.append('Required')
            error = True

        if error:
            groups = get_groups(current_user)
            agl = models.get_active_group_list(groups, None)
            return render_template('create_group.html', form=form, groups=groups, active_group_list=agl)
        else:
            # Create a new Group with the specified name and members
            members_to_add = [current_user.username, form.member1.data, form.member2.data, form.member3.data]
            create_group(name, members_to_add)
            return redirect(url_for('group_page', group_name=name))

    else:  # method = GET so render the page

        groups = get_groups(current_user)
        agl = models.get_active_group_list(groups, None)
        return render_template('create_group.html', form=form, groups=groups, active_group_list=agl)


@app.route('/group/<group_name>')
def group_page(group_name=None):

    group = models.get_group(group_name)
    if group is None:
        return redirect(url_for('index'))

    is_sending = models.user_is_sharing_with_group(current_user, group)

    groups = get_groups(current_user)
    agl = models.get_active_group_list(groups, group)

    return render_template('group.html', group=group, groups=groups, active_group_list=agl, sending=is_sending)


@app.route('/toggle_send_browsing/<group_name>', methods=["POST"])
@login_required
def toggle_send_browsing(group_name=None):

    # Whether the user turned on or off sending their browsing history to this group
    send = request.values['should_send'] == 'true'

    group = models.get_group(group_name)
    if group is None:
        return redirect(url_for('index'))

    # Record the change on the backend
    models.set_send(current_user, group, send)

    # Determine if the user is sending their browsing data to this group (for rendering the checkbox)
    is_sending = models.user_is_sharing_with_group(current_user, group)

    groups = get_groups(current_user)
    agl = models.get_active_group_list(groups, group)

    return render_template('group.html', group=group, groups=groups, active_group_list=agl, sending=is_sending)

@app.route('/user/<username>')
@login_required
def user(username=None):

    users = db.session.query(User).filter_by(username=username).all()
    if len(users) < 1:
        flash('Could not find user {}.'.format(username))

        groups = get_groups(current_user)
        agl = models.get_active_group_list(groups, None)
        return render_template('index.html', title='Your Groups', groups=groups, active_group_list=agl)

    # Get the first user (we presume there is only 1 user allowed for each username)
    other_user = users[0]

    if current_user.is_authenticated:

        return render_template('user.html', title=username, sent_from=current_user, to=other_user,
                               from_messages=load_messages(sender=other_user, receiver=current_user),
                               to_messages=load_messages(sender=current_user, receiver=other_user))
    else:
        groups = get_groups(current_user)
        agl = models.get_active_group_list(groups, None)
        return render_template('index.html', title='Your Groups', groups=groups, active_group_list=agl)


@app.route('/history')
@login_required
def history():
    history_urls = load_history(current_user)

    groups = get_groups(current_user)
    agl = models.get_active_group_list(groups, None)
    return render_template('history.html', history=history_urls, groups=groups, active_group_list=agl)


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

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            user = db.session.query(User).filter_by(username=form.username.data).all()[0]
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        except Exception:
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
    url_token = 'url='
    urls = [term for term in data if term.startswith(url_token)]

    print('api', urls)

    if len(urls) == 1:  # A new URL was navigated to
        status = 'success'

        # Get the url string without quote escapes
        url = [term for term in urls][0]
        url = str(unquote(url))
        url = url.replace(url_token, '')

        if not utils.url_in_stoplist(url):
            # Create a message, persist it to the database

            # Parallel call to the database
            p = Process(target=store_url_browse_event, args=(url, me))
            p.start()
            # message = store_url_browse_event(url, me)

            # TODO : GET THIS WORKING (WITH emit)
            # Send the new message's html representation across the network
            # try:
            # send(message, broadcast=True)
                # print('Success', url)
            # except Exception:
            #     print('Failed', url)
            #     pass
    else:
        status = 'failure'

    response = {'status': status}
    return jsonify(response)

@app.route('/register_vote')
def register_vote():
    pass


# Define Forms (from WTForms) #
class NewGroupForm(Form):
    group_name = StringField('Group Name', [validators.Length(min=3, max=50)])
    member1 = SelectField('Member 1')
    member2 = SelectField('Member 2 (optional)', [validators.optional()])
    member3 = SelectField('Member 3 (optional)', [validators.optional()])

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.equal_to('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

# End WTForms #


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

