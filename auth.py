# from app import app
# from flask import request, jsonify
# from models import *
# from time import gmtime, strftime

# @app.route('/api/login')
# def login():
#     user_input = request.get_json()
#     account = User.query.filter(User.username==user_input['username']).first()
#     if account is None:
#         return jsonify({"message": "incorrect username or password"})
#     if account.password == user_input['password']:
#         activeuser = ActiveUser(username = user_input['username'], login_time = strftime("%Y-%m-%d %H:%M:%S", gmtime()))
#         account.active_account.append(activeuser)
#         db.session.commit()
#         return jsonify({"message": "logged in"})
#     else:
#         return jsonify({"message": "incorrect username or password"})
    
# @app.route('/api/logout')
# def logout():
#     user_input = request.get_json()
#     try:
#         activeuser = ActiveUser.query.filter(ActiveUser.username==user_input['username']).first_or_404()
#         account = User.query.filter(User.username==user_input['username']).first()
#         account.active_account.remove(activeuser)
#         activeuser.logout_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
#     except Exception as e:
#         return jsonify({"messages": repr(e)})


# @app.route('/api/signup')
# def signup():
#     user_input = request.get_json()
#     try:
#         username = user_input['username']
#         if User.query.filter(User.username==username).first():
#             return
#         password = user_input['password']
#         pid = user_input['pid']
#         year = user_input['year']
#         major = user_input['major']
#         db.session.add(User(username = username, pid = pid, year = year, major = major, password = password))
#         db.session.commit()
#         return jsonify({"message": "account created"})
#     except Exception as e:
#         return jsonify({"messages": repr(e)})


