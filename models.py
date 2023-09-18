from extensions import db
from sqlalchemy import ForeignKeyConstraint, Table, Column, LargeBinary, Integer, String, MetaData, ForeignKey
import sqlalchemy.types as types
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, MappedAsDataclass

club_tags = db.Table("club_tags", 
    Column("club_code", String, ForeignKey("Clubs.code")),
    Column("tags_tag", String, ForeignKey("Tags.tag")))

club_favorites = db.Table("club_favorites",
    Column("club_code", String, ForeignKey("Clubs.code")),
    Column("favorite", String, ForeignKey("Users.username")),
    )

club_members = db.Table("club_members",
    Column("club_code", String, ForeignKey("Clubs.code")),
    Column("members", String, ForeignKey("Users.username")),
    )

active_users = db.Table("active_users",
    Column("user_account", String, ForeignKey("Users.username")),
    Column("active_account", String, ForeignKey("ActiveUsers.current_user")),
    )

club_comments = db.Table("club_comments",
    Column("club", String, ForeignKey("Clubs.name")),
    Column("comments", String, ForeignKey("Comments.content")),
    )

user_comments = db.Table("user_comments",
    Column("user", String, ForeignKey("Users.username")),
    Column("comments", String, ForeignKey("Comments.content")),
    )

club_files = db.Table("club_files",
    Column("club", String, ForeignKey("Clubs.code")),
    Column("file", String, ForeignKey("files.id")),
    )

class User(db.Model):
    __tablename__ = "Users"
    pid: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    major: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

    def __lt__(self, other):
        return other

class Tags(db.Model):
    __tablename__ = "Tags"
    tag: Mapped[str] = mapped_column(String, primary_key=True)

class Club(db.Model):
    __tablename__ = "Clubs"
    code: Mapped[str] = mapped_column(String, primary_key=True, nullable = False)
    name: Mapped[str] = mapped_column(String, nullable = False)
    description: Mapped[str] = mapped_column(String, nullable = False)
    basic_info: Mapped[str] = mapped_column(String, default = '')
    contact_info: Mapped[str] = mapped_column(String, default = '')
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    tags = relationship(
        "Tags", secondary=club_tags, backref="clubs"
    )
    members = relationship(
        "User", secondary=club_members, backref="clubs_joined"
    )
    favorites = relationship(
        "User", secondary=club_favorites, backref="clubs_favorited"
    )
    comments = relationship(
        "Comment", secondary = club_comments, backref = "club"
    )

class ActiveUser(db.Model):
    __tablename__ = "ActiveUsers"
    current_user: Mapped[str] = mapped_column(String)
    login_time: Mapped[str] = mapped_column(String, default=0, primary_key = True)
    logout_time: Mapped[str] = mapped_column(String, default=0)
    user_account = relationship(
        "User", secondary=active_users, backref=db.backref("active_account", lazy = 'dynamic')
    )

class Comment(db.Model):
    __tablename__ = 'Comments'
    id: Mapped[str] = mapped_column(String, primary_key = True)
    parent_id = mapped_column(String, ForeignKey("Comments.id"), default="")
    content: Mapped[str] = mapped_column(String)
    children = relationship("Comment", back_populates="parent")
    parent = relationship("Comment", back_populates="children", remote_side=[id])
    commenter = relationship(
        "User", secondary = user_comments, backref = "comments", remote_side = [id]
        )
    
class File(db.Model):
    __tablename__ = 'files'
    id: Mapped[str] = mapped_column(String, primary_key = True)
    filename: Mapped[str] = mapped_column(String)
    data: Mapped[LargeBinary] = mapped_column(LargeBinary)
    club = relationship(
        "Club", secondary = club_files, backref = db.backref("files", lazy='dynamic')
    )

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
