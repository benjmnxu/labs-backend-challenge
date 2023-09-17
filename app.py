import random
import string
from flask import Flask, request, jsonify
from time import gmtime, strftime
from extensions import db
from dotenv import load_dotenv
import os
import openai

load_dotenv()
# lol pls dont steal api key
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db.init_app(app)
app.app_context().push()

from models import *

@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route('/api/clubs')
def clubs():
    clubs = Club.query.all()
    content = {}

    for club in clubs:
        members = []
        tags = []
        file_names = []
        comments = []
        for member in club.members:
            members.append(member.username)
        for tag in club.tags:
            tags.append(tag.tag)
        for file in club.files:
            file_names.append(file.filename)
        for comment in club.comments:
            comments.append(comment.content)
        content[club.name] = {
            "favorites": club.favorite_count,
            "members": members,
            "tags": tags,
            "comments": comments,
            "files": file_names
        }
    print(content)
    return jsonify(content)

@app.route('/api/get_user', methods = ['GET'])
def get_user():
    user = request.get_json()
    try:
        current_user = User.query.filter_by(username=user["current_user"]).first()
        if current_user == None or current_user.active_account.filter_by(current_user=user['current_user']).first() == None:
            return jsonify({"message": "login required"})
        user = User.query.filter_by(username=user["username"]).first()
        profile = {}
        clubs = []
        for club in user.clubs_joined:
            clubs.append(club.name)
        profile[user.username] = {
            "year" : user.year,
            "major": user.major,
            "clubs joined": clubs
        }
        return jsonify(profile)
    except Exception as e:
        return jsonify({"message": repr(e)})
    
@app.route('/api/search_clubs', methods = ['GET'])
def get_club():
    club = request.get_json()
    try:
        clubs = Club.query.filter(Club.name.contains(club["name"])).all()
        content = []
        for club in clubs:
            content.append(club.name)
        return jsonify({
            "clubs": content
        })
    except Exception as e:
        return jsonify({"message": repr(e)})

@app.route('/api/add_club', methods = ['POST'])
def add():
    try:
        new_club = request.get_json()
        current_user = User.query.filter_by(username=new_club["current_user"]).first()
        if current_user == None or current_user.active_account.filter_by(current_user=new_club['current_user']).first() == None:
            return jsonify({"message": "login required"})
        
        code = new_club["code"]
        name = new_club["name"]
        description = new_club["description"]
        tags = new_club.get("tags", "")
        club = Club(code=code, name=name, description=description)
        db.session.add(club)
        if type(tags) is not list:
            t = []
            t.append(tags)
            tags = t
        for tag in tags:
            t = Tags.query.filter(Tags.tag == tag).first()
            if t is None:
                club.tags.append(Tags(tag = tag))
            else:
                club.tags.append(t)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": repr(e)})
    return jsonify({"message": "new club added"})

@app.route('/api/favorite_club', methods = ['GET'])
def favorites():
    try:
        new_club = request.get_json()
        current_user = User.query.filter_by(username=new_club["current_user"]).first()
        if current_user == None or current_user.active_account.filter_by(current_user=new_club['current_user']).first() == None:
            return jsonify({"message": "login required"})
        code = new_club["code"]
        username = new_club["username"]
        person = User.query.filter_by(username=username).first()
        club = Club.query.filter_by(code=code).first()
        if club in person.clubs_favorited:
            return jsonify({"message": "This club has already been favorited"})
        club.favorite_count += 1
        person.clubs_favorited.append(club)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": repr(e)})
    return jsonify({"message": "added new favorite club"})

@app.route('/api/modify_club', methods = ['POST'])
def modify_club():
    try:
        new_information = request.get_json()
        current_user = User.query.filter_by(username=new_information["current_user"]).first()
        if current_user == None or current_user.active_account.filter_by(current_user=new_information['current_user']).first() == None:
            return jsonify({"message": "login required"})
        code = new_information["code"]
        club = Club.query.filter_by(code=code).first()
        if club is None:
            return({"message": "Club does not exist"})
        actions_message = []
        
        desc = new_information.get("description", None)
        print(desc)
        if desc is not None:
            club.description = desc
            actions_message.append("changed description")
        
        name = new_information.get("name", None)
        if name is not None:
            club.name = name
            actions_message.append("changed name")
        
        errors = []
        add_m = new_information.get("add_members", None)
        if add_m is not None:
            members = []
            people = []
            if type(add_m) is not list:
                members.append(add_m)
            else:
                members = add_m
            for m in members:
                person = User.query.filter_by(username=m).first()
                if person in club.members:
                    actions_message.append(m + " is already in the club")
                else:
                    if person is not None:
                        club.members.append(person)
                        people.append(m)
                    else:
                        errors.append(m)
            if(len(people) > 0):
                actions_message.append("added members: " + ",".join(people))
            if(len(errors)> 0):
                actions_message.append("The following do not have accounts:" + ",".join(errors))
        
        add_t = new_information.get("add_tags", None)
        if add_t is not None:
            tags = []
            if type(add_t) is not list:
                tags.append(add_t)
            else:
                tags = add_t

            for t in tags:
                tag = Tags.query.filter_by(tag = t).first()
                if tag in club.tags:
                    actions_message.append("The tag: <" + t + "> is already applied to the club")
                if tag is not None:
                    club.tags.append(tag)
                else:
                    tg = Tags(tag = t)
                    db.session.add(tg)
                    club.tags.append(tg)
            actions_message.append("added: " + ",".join(tags))

        errors = []
        remove_m = new_information.get("remove_members", None)
        if remove_m is not None:
            members = []
            people = []
            if type(remove_m) is not list:
                members.append(remove_m)
            else:
                members = remove_m
            for m in members:
                person = User.query.filter_by(username=m).first()
                if person is not None:
                    club_members.remove(person)
                    people.append(m)
                else:
                    errors.append(m)
            if(len(people) > 0):
                actions_message.append("removed: " + ",".join(people))
            if(len(errors)> 0):
                actions_message.append("The following do not exist in the club: " + ",".join(errors))

        remove_t = new_information.get("remove_tags", None)
        print(remove_t)
        if remove_t is not None:
            tags = []
            if type(remove_t) is not list:
                tags.append(remove_t)
            else:
                tags = remove_t
            for t in tags:
                print(t)
                tag = Tags.query.filter_by(tag=t).first()
                if tag:
                    club.tags.remove(tag)
            actions_message.append("removed: " + ",".join(remove_t))
        
        db.session.commit()

    except Exception as e:
        return jsonify({"message": repr(e)})
    return jsonify({"message": actions_message})

@app.route('/api/tags')
def tags():
    tags = Tags.query.all()
    content = {}
    for tag in tags:
        club_list = tag.clubs
        content_list = []
        for club in club_list:
            content_list.append(club.name)
        content[tag.tag] = content_list
    return content

@app.route('/api/comment', methods = ['POST'])
def comment():
    try:
        comment = request.get_json()
        current_user = User.query.filter_by(username=comment["current_user"]).first()
        if current_user == None or current_user.active_account.filter_by(current_user=comment['current_user']).first() == None:
            return jsonify({"message": "login required"})
        
        club = Club.query.filter_by(code=comment["code"]).first()
        content = comment["content"]
        responding_to = comment.get('responding_to', "")
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        c = Comment(id=id, parent_id=responding_to, content=content)
        db.session.add(c)
        club.comments.append(c)
        current_user.comments.append(c)
        db.session.commit()
    except Exception as e:
        return e
        return jsonify({"message": repr(e)})
    return jsonify({"message": "new comment created"})


@app.route('/api/login')
def login():
    user_input = request.get_json()
    try:
        account = User.query.filter(User.username==user_input['username']).first()
        if account is None:
            return jsonify({"message": "incorrect username or password"})
        if account.password == user_input['password']:
            activeuser = ActiveUser(current_user = user_input['username'], login_time = strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            account.active_account.append(activeuser)
            db.session.commit()
            return jsonify({"message": "logged in"})
        else:
            return jsonify({"message": "incorrect username or password"})
    except Exception as e:
        return jsonify({"message": repr(e)})
    
@app.route('/api/logout')
def logout():
    user_input = request.get_json()
    try:
        activeuser = ActiveUser.query.filter(ActiveUser.current_user==user_input['current_user']).first_or_404()
        account = User.query.filter(User.username==user_input['current_user']).first()
        account.active_account.remove(activeuser)
        activeuser.logout_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        db.session.commit()
        return jsonify({"messages": "logged out"})
    except Exception as e:
        return jsonify({"messages": repr(e)})


@app.route('/api/signup')
def signup():
    user_input = request.get_json()
    try:
        username = user_input['username']
        if User.query.filter(User.username==username).first():
            return
        password = user_input['password']
        pid = user_input['pid']
        year = user_input['year']
        major = user_input['major']
        db.session.add(User(username = username, pid = pid, year = year, major = major, password = password))
        db.session.commit()
        return jsonify({"message": "account created"})
    except Exception as e:
        return jsonify({"messages": repr(e)})

@app.route('/api/recommend_tags')
def recommend_tags():
    user_input = request.get_json()
    try:
        club_name = user_input.get("club", "")
        club_description = user_input.get("description", "")
        if club_name != "":
            description = Club.query.filter_by(name=club_name).first().description
        elif club_description != "":
            description = club_description
        raw_tags = Tags.query.all()
        tags = []
        for raw_tag in raw_tags:
            tags.append(raw_tag.tag)
        tgs = ','.join(tags)
        messages = [
            {
                "role" : "system", "content": "You are an expert synthesizer helping goven the student clubs at the University of Pennsylvania"
            },
            {
                "role": "user", 
                "content": 
                f"""
                    Here is the description of a club at Penn:
                    {description}
                    Also, here is a list of pre-existing tags that describe Penn clubs:
                    {tgs}
                    Keeping the tag list in mind, pick either tags from the list
                    or generate your own to match the given description.
                    Be specific and fit the form of the tags given in the list.
                    Output only your list of tags.
                """
            }
        ]
        response = openai.ChatCompletion.create(
            model = "gpt-4",
            messages = messages,
            temperature = 0.25
        )
        return jsonify({"message": response['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"messages": e})
    
@app.route("/api/upload_file", methods=['POST'])
def upload():
    raw_club = request.form
    raw_file = request.files
    code = raw_club["code"]
    club = Club.query.filter_by(code = code).first()
    file = raw_file['file']

    upload = File(id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),filename=file.filename, data = file.read())
    club.files.append(upload)
    db.session.add(upload)
    db.session.commit()

    return jsonify({"message": f"Uploaded: {file.filename}"})
    
if __name__ == '__main__':
    app.run()
