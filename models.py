from flask_login import UserMixin
from . import utils
from . import get_db, scraping
from datetime import datetime, timedelta

import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator

# Get an instance of the db from __init__
db = get_db()

def get_group(group_name):
    groups = db.session.query(Group).filter_by(name=group_name).all()
    if len(groups) < 1:
        print('Could not find group {}.'.format(group_name))
        return None

    group = groups[0]
    return group


# Time Utilities #
def now_string():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def string_to_datetime(string):
    datetime_object = datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    return datetime_object


def relative_date(earlier_datetime):
    delta = datetime.now() - earlier_datetime

    two_years = timedelta(days=365)
    year = timedelta(days=365)
    month = timedelta(weeks=4)
    day = timedelta(days=1)
    hour = timedelta(hours=1)
    min = timedelta(minutes=1)

    if delta < min:
        return 'just now'
    elif delta < hour:
        return str(int(delta.seconds / 60)) + ' minutes ago'
    elif delta < day:
        return str(int(delta.seconds / (60 * 60))) + ' hours ago'
    elif delta < month:
        return str(delta.days) + ' days ago'
    elif delta < year:
        return str(int(delta.days / 30.44)) + ' months ago'
    elif delta < two_years:
        return '> 1 year ago'
    else:
        return '> 2 years ago'

# End Time Utilities #


def store_url_browse_event(url, user, scrape=True):
    """
    Create a message, commit it to the database and get it ready to send across the network.
    """
    if scrape:
        info = scraping.get_airbnb_info(url)
    else:
        info = None

    # Create the message and add it to the database
    link = Link(url=url, originator=user, originator_id=user.id, posted_at=now_string(), info=info)

    # Get the correct session for the object (hacky solution) #TODO fix base problem
    session = db.session.object_session(link)

    # Persist the change
    session.add(link)
    session.commit()

    # If the user is currently sharing with a group, let them see the event
    group = session.query(Group).filter_by(id=user.sharing_browsing_with).first()
    if group is not None:
        group.messages.append(link)
        session.commit()

    # Return serialized message ready for Socket.io
    return link.serialize()


def load_messages(sender=None, receiver=None):
    """Load the messages for a given user (or all messages if user=None)"""
    last_messages = []
    if sender or receiver:
        last_messages = db.session.query(Link).filter_by(sender_id=sender.id, receiver_id=receiver.id)
    else:
        query = db.session.query(Link).all()
        if query is not None:
            last_messages = query

    return [message.get_html() for message in last_messages]


def load_history(user):
    """Load the browsing history for a given user"""
    history = db.session.query(Link).filter_by(originator_id=user.id)
    return [message.get_html(light=True) for message in history]


def create_group(name, member_names):
    new_group = Group(name=name)

    for member_name in member_names:
        if member_name != '':
            member = User.query.filter_by(username=member_name).first()
            new_group.members.append(member)

    db.session.add(new_group)
    db.session.commit()


def get_friends(user):
    other_users = User.query.filter(User.id != user.id).all()

    friends = [(user.username, user.username) for user in other_users]

    return friends


def get_groups(user):
    groups_user_member_of = Group.query.filter(Group.members.any(username=user.username))
    return groups_user_member_of


def get_active_group_list(groups, active_group):
    active_group_list = []
    for group in groups:
        if group == active_group:
            active_group_list.append('current_group')
        else:
            active_group_list.append('')
    return active_group_list


def set_send(user, group, send):
    """
    If send is True, set this group as the group the user is sharing data with.
    If send is False and this is the group the user is currently sharing with, disable sending entirely.

    """

    print(user, group, send)

    if send is False and user.sharing_browsing_with == group.id:
        user.sharing_browsing_with = None
    else:
        user.sharing_browsing_with = group.id

    print(user.sharing_browsing_with)
    db.session.commit()


def user_sharing_with_someone_else(user, group):
    sharing_with = user.sharing_browsing_with
    return sharing_with is not None and sharing_with != group.id


def user_is_sharing_with_group(user, group):
    """ Return true if the user is sharing their browsing history with the given group"""
    return user.sharing_browsing_with == group.id


# Group <-> Link table
group_links = db.Table('group_links',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('link_id', db.Integer, db.ForeignKey('link.id'))
)
localhost:5000
# Group <-> User table
members = db.Table('members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

# Not needed since this is a one to many not many to many
# # User <-> Link table
# history = db.Table('history',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('link_id', db.Integer, db.ForeignKey('link.id'))
# )


TEXT_DICT_SIZE = 1024


class TextDict(TypeDecorator):

    impl = sqlalchemy.Text(TEXT_DICT_SIZE)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    posted_at = db.Column(db.String(200), nullable=False)  # String representation of datetime
    info = db.Column(TextDict(), nullable=True)

    originator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    originator = db.relationship("User", back_populates='history')

    # Load card templates
    message_template = open('templates/card/advanced_card.html').read()
    history_template = open('templates/card/history_card.html').read()

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.url, self.originator)

    def get_html(self, light=False):
        """Return the HTML representation of the message with  bootstrap formatting"""

        user = self.originator.username
        url = utils.truncate(self.url)
        href = self.url
        time_posted = relative_date(string_to_datetime(self.posted_at))
        print(self.info)
        title = self.info['title'] if self.info.get('title') else ''

        if light:
            html = Link.history_template.format(url=url, href=href)
        else:
            html = Link.message_template.format(title=title, link=self, user=user, url=url, href=href, date=time_posted)

        return html

    def serialize(self):
        return str(self.originator) + '~' + self.get_html()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    # A user's browing history that we have stored
    history = db.relationship('Link', back_populates='originator')

    # The group the user is sending their browsing data to (or None)
    sharing_browsing_with = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    members = db.relationship('User', secondary='members',
                            backref=db.backref('members_of', lazy='dynamic'))

    messages = db.relationship('Link', secondary='group_links',
                            backref=db.backref('groups', lazy='dynamic'))
