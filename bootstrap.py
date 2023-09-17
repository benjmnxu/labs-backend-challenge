import os
from app import DB_FILE
from extensions import db
import json
from sqlalchemy import select

def create_user():
    from models import User
    db.session.add(User(pid = 0, username = "josh", year = 0, major = "CIS", password = "password"))
    db.session.commit()


def load_data():
    from models import Club, Tags, User
    session = db.session
    with open("clubs.json") as f:
        data = json.load(f)
        for clubs in data:
            c = Club(code = clubs["code"], name = clubs["name"], description = (clubs["description"]))
            session.add(c)
            for tag in clubs["tags"]:
                tag_obj = session.execute(select(Tags).where(Tags.tag == tag)).scalar_one_or_none()
                print(tag_obj)
                if tag_obj is None:
                    t = Tags(tag=tag)
                    session.add(t)
                    c.tags.append(t)
                else:
                    c.tags.append(tag_obj)
                session.commit()
    session.remove()



# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
