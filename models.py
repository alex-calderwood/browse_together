from flask_login import UserMixin
from . import urltils
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def draft_new_link_message(url, originator):
    """
    Create a message, commit it to the database and get it ready to send across the network.
    """

    # Create the message and add it to the database
    link = Link(url=url, originator=originator, originator_id=originator.id)
    db.session.object_session(link).add(link)  # TODO fix this hacky solution
    db.session.object_session(link).commit()

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


class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    url = db.Column(db.String(500), nullable=False)

    originator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    originator = db.relationship("User", back_populates='history')

    # Load card templates
    message_template = open('templates/iframe_card.html').read()
    history_template = open('templates/history_card.html').read()

    def __repr__(self):
        return '{} {} {}'.format(self.id, self.url, self.originator)

    def get_html(self, light=False):
        """Return the HTML representation of the message with  bootstrap formatting"""

        # Get the name of the user that posted it
        # posted_by = db.session.query(User).get(self.sender_id)

        text = urltils.truncate(self.url)
        href = self.url

        if light:
            html = Link.history_template.format(text=text, href=href)
        else:
            html = Link.message_template.format(text=text, href=href)

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


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)

    members = db.relationship('User', secondary='members',
                            backref=db.backref('members_of', lazy='dynamic'))

    messages = db.relationship('Link', secondary='group_links',
                            backref=db.backref('groups', lazy='dynamic'))
