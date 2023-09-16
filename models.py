from extensions import db
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, MappedAsDataclass

club_tags = db.Table("club_tags", 
    Column("club_code", String, ForeignKey("Clubs.code")),
    Column("tags_tag", String, ForeignKey("Tags.tag")))

# club_user = db.Table("club_user",
#     Column("club_code", String, ForeignKey("Clubs.code")),
#     Column("penn_id", Integer, ForeignKey("User.id")))

class Club(db.Model):
    __tablename__ = "Clubs"
    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    tags = relationship(
        "Tags", secondary=club_tags, backref="clubs"
    )

class Tags(db.Model):
    __tablename__ = "Tags"
    tag: Mapped[str] = mapped_column(String, primary_key=True)
    
class User(db.Model):
    __tablename__ = "Users"
    pennid: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    major: Mapped[str] = mapped_column(String)

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
