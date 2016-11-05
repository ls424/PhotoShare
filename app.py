######################################
# author Shuo Lin
######################################
# Some code adapted from 
# ben lawson <balawson@bu.edu> 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask.ext.login import current_user
import datetime

# - for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# - These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '940424'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# - begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()



def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	# - The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	# - check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	# - information did not match
	return '''
	<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>
			'''
@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out', photos = getAllPhotos()) 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

# - you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		birthday = request.form.get('birthday')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
	except:
		print "couldn't find all tokens1" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	print email
	print password
	print firstname
	print lastname
	print birthday
	print hometown
	print gender
	if test and email and password and firstname and lastname and birthday and hometown and gender:
		print cursor.execute("INSERT INTO Users (email, password, firstname, lastname, birthday, hometown, gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(email, password, firstname, lastname, birthday, hometown, gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!', photos = getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())
	else:
		print "couldn't find all tokens2"
		return flask.redirect(flask.url_for('register'))
#end login code

# - 
def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, likes, user_id FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

# - 
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, likes, user_id FROM Pictures")
	return cursor.fetchall()

# - 
def getAlbumPhotos(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, likes, user_id, album_id FROM Pictures WHERE album_id = '{0}'".format(albumid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

# - 
def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

# - 
def getFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user2_id FROM Follow_to WHERE user1_id = '{0}'".format(uid)) 
	return cursor.fetchall()

# - 
def Follow(uid1, uid2):
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Follow_to (user1_id, user2_id) VALUES ('{0}', '{1}')".format(uid1, uid2))
	conn.commit()
	return

# - 
def getAllUsers(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, firstname, lastname FROM Users WHERE user_id != '{0}'".format(uid))
	return cursor.fetchall()

#- 
def getUserInfo(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT email, firstname, lastname, birthday, hometown, gender FROM Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

# -
def getAlbumInfo(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

# -
def getAlbumName(albumid):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE album_id = '{0}'".format(albumid))
	return cursor.fetchall()

# - 
def getAlbumId(albumname):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE name = '{0}'".format(albumname))
	return cursor.fetchall()

# - 
def getUserTags(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT tag_name FROM Taged_by t JOIN Pictures p ON t.picture_id = p.picture_id JOIN Users u ON p.user_id = u.user_id WHERE u.user_id = '{0}'".format(uid))
	return cursor.fetchall()

# - 
def getAllTags():
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT tag_name, picture_id FROM Taged_by")
	return cursor.fetchall()

# - 
def getPopTags():
	topfivetag =[]
	cursor = conn.cursor()
	cursor.execute("SELECT T.tag_name from Taged_by T, Pictures P WHERE P.picture_id = T.picture_id GROUP BY T.tag_name ORDER BY count(T.picture_id) DESC LIMIT 5")
	for x in cursor:
		topfivetag.append(x[0])
	return topfivetag
# - 
def getPhotoId(tagname):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Taged_by WHERE tag_name = '{0}'".format(tagname))
	return cursor.fetchall()

# - 
def getUserPhotoId(tagname, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Taged_by WHERE tag_name = '{0}'".format(tagname))
	return cursor.fetchall()


# - get all user's photos for certain tag
def getUserTagPhotos(tagname, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT p.imgdata, p.picture_id, p.caption, p.likes, p.user_id FROM Pictures p JOIN Taged_by t ON p.picture_id = t.picture_id  WHERE tag_name = '{0}' AND user_id = '{1}'".format(tagname, uid))
	return cursor.fetchall()

# - get all photos for certian tag
def getAllTagPhotos(tagname):
	cursor = conn.cursor()
	# cursor.execute("SELECT p.imgdata, p.picture_id, p.caption FROM Pictures p JOIN Taged_by t ON p.picture_id = t.picture_id WHERE p.picture_id = '{0}' AND t.tag_name = '{1}'".format(picid, tagname))
	cursor.execute("SELECT p.imgdata, p.picture_id, p.caption, p.likes, p.user_id FROM Pictures p LEFT JOIN Taged_by t ON p.picture_id = t.picture_id WHERE tag_name = '{0}'".format(tagname))
	return cursor.fetchall()

# - get search results via input tags
def getSearchedPhotoId(tagname, photos):
	taglist = stringToArray(tagname)
	dic = []
	for pic in photos:
		count = 0
		for i in taglist:
			cursor = conn.cursor()
			if cursor.execute("SELECT tag_name, picture_id FROM Taged_by WHERE tag_name = '{0}' AND picture_id = '{1}'".format(i, pic[1])):
				count = count + 1
			else:
				break
		if count == len(taglist):
			dic.append(pic[1])
	return dic 


# - get comments content according to the picture_id
def getComments(picid):
	cursor = conn.cursor()
	cursor.execute("SELECT comment_text, user_id FROM Comments WHERE picture_id = '{0}'".format(picid))
	return cursor.fetchall()

# - check if the email is unique
def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

# - 
def isAlbumUnique(albumname):
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Albums WHERE name = '{0}'".format(albumname)): 
		#this means there are greater than zero entries with that album
		return False
	else:
		return True

# - 
def isTagUnique(tag):
	cursor = conn.cursor()
	if cursor.execute("SELECT tag_name FROM Users WHERE tag = '{0}'".format(tag)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
# - 
def isAlbumExist(name):
	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Albums WHERE name = '{0}'".format(name)): 
		#this means there are greater than zero entries with that album
		return True
	else:
		return False

# - 		
def isTagInPic(tagname):
	pass

# - 
def update(uid):
	print "updated"
	cursor = conn.cursor()
	cursor.execute("UPDATE Users SET count = count + 1 WHERE user_id ='{0}'".format(uid))
	conn.commit()
	return

# - 
def stringToArray(str):
	list = str.split(" ")
	res = []
	for i in list:
		if i:
			res.append(i)
	return res




# - begin photo uploading code
# - photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# - 
@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'GET':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('upload.html', albums = getAlbumInfo(uid))
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		tag = request.form.get('tags')
		albumid = request.form.get('albums')
		print caption
		print tag
		print albumid
		if imgfile and caption and tag and albumid:
			update(uid)
			photo_data = base64.standard_b64encode(imgfile.read())
			taglist = stringToArray(tag)
			cursor = conn.cursor()
			cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}' )".format(photo_data,uid, caption, albumid))
			cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}' ORDER BY picture_id".format(uid))
			picid = cursor.fetchall()
			print picid
			for item in taglist:
				# cursor.execute("INSERT INTO Tags (tag_name) VALUES ('{0}')".format(item))
				cursor.execute("INSERT INTO Taged_by (picture_id, tag_name) VALUES ('{0}', '{1}')".format(int(picid[len(picid) - 1][0]), item))
			conn.commit()
			return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())
		else:
			return '''
				<a href='/upload'>All content are required!</a>
				'''
		
	# - The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code 






# - Personal page
@app.route('/personal', methods=['GET'])
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	info = getUserInfo(uid)
	albums = getAlbumInfo(uid)
	tags = getUserTags(uid)
	print tags
	return render_template('personal.html', email=info[0][0], firstname=info[0][1], lastname=info[0][2], birthday=info[0][3], hometown=info[0][4], gender=info[0][5], albums = albums, tags = tags)

# - album create
@app.route('/personal/create', methods=['POST'])
@flask_login.login_required
def create_album():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	name = request.form.get('name');
	print name
	date = datetime.datetime.now()
	cursor = conn.cursor()
	if isAlbumUnique(name):
		cursor.execute("INSERT INTO Albums (name, user_id, create_date) VALUES ('{0}', '{1}', '{2}')".format(name, uid, date))
		conn.commit()
	else:
		return'''
			<a href='/personal'>Duplicate album name, the album name has been used by other users or yourself</a>
			  '''
	
	return render_template('hello.html', name=flask_login.current_user.id, message='Album created!',  photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())

# - album delete
@app.route('/hello/personal/delete', methods=['POST'])
@flask_login.login_required
def delete_album():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	albumname = request.form.get('aname')
	if isAlbumExist(albumname):
		cursor = conn.cursor()
		cursor.execute("SELECT album_id FROM Albums WHERE name = '{0}'".format(albumname))
		albumid = cursor.fetchall()
		cursor.execute("DELETE FROM Albums WHERE album_id = '{0}'".format(albumid[0][0])) 
		cursor.execute("DELETE FROM Pictures WHERE album_id = '{0}'".format(albumid[0][0]))
		# cursor.execute("DELETE FROM Albums WHERE album_name = '{0}'".format(albumname)) 
		# cursor.execute("DELETE FROM Pictures WHERE album_name = '{0}'".format(albumname))
		conn.commit()
		return render_template("hello.html", name=flask_login.current_user.id, message='Album deleted!', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())
	else:
		return'''
			<a href='/personal'>The Album you want to delete doesn't exist!</a>
			  '''

# - default photo page			  
# @app.route('/photo', methods=['GET'])	#cannot use get here
# def photo():
# 	uid = getUserIdFromEmail(flask_login.current_user.id)
# 	aid = request.form.get('albumid')
# 	aname = getAlbumName(aid)
# 	photos = getAlbumPhotos(aid)
# 	return render_template('photo.html', photos = photos, attribute = 'Album', aname=aname[0][0])


# - show photos for album, require login
@app.route('/photo/album', methods=['POST'])	#cannot use get here
@flask_login.login_required
def show_album_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	aid = request.form.get('albumid')
	aname = getAlbumName(aid)
	photos = getAlbumPhotos(aid)
	return render_template('photo.html', photos = photos, attribute = 'Album', aname=aname[0][0])

# - show photos for user's tag, require login
@app.route('/photo/tag', methods=['POST'])	
@flask_login.login_required
def show_tag_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	tagname = request.form.get('tagname')
	print 'showtagphotos'
	print tagname
	return render_template('photo.html', photos = getUserTagPhotos(tagname, uid), tags = getAllTags(), attribute = 'Tag', aname = tagname)
# end of personal page



# - display the friend page
@app.route('/friend', methods=['GET'])
@flask_login.login_required
def view_users():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	users = getAllUsers(uid)
	friends = getFriends(uid)
	return render_template("friend.html", friends=friends, users=users)


# - begin show users function, require login
@app.route('/friend/added', methods=['POST'])
@flask_login.login_required
def add_friend():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	friendId = request.form.get('users')    #may not work since have to select the current value
	# print friendId
	Follow(uid, friendId)
	return render_template('hello.html', name=flask_login.current_user.id, message='Friend added',  photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())


# - basic page of view 
@app.route('/view', methods=['GET', 'POST'])
# @flask_login.login_required
def view_tags():
	# uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name FROM Albums")
	albums = cursor.fetchall()
	print albums
	return render_template('view.html', tags = getAllTags(), albums = albums, poptags = getPopTags())

# - view photos for each tag
@app.route('/view/tag/photo/', methods=['GET', 'POST'])
def show_all_tag_photos():
	if request.method == 'GET':
		return render_template("view.html", tags = getAllTags())
	if request.method == 'POST':
		tagname = request.form.get('tagname')
		print 'shoalltagphoho'
		print tagname
		return render_template("photo.html", photos=getAllTagPhotos(tagname), tags = getAllTags(), attribute = 'Tag', aname = tagname)

# - view photos for each tag on main page
@app.route('/view/tag_photo/<tagname>', methods=['GET', 'POST'])
def show_tags_photos(tagname):
	# if request.method == 'GET':
	# 	return render_template("view.html", tags = getAllTags())
	# if request.method == 'POST':
	print tagname
	return render_template("photo.html", photos=getAllTagPhotos(tagname), tags = getAllTags(), attribute = 'Tag', aname = tagname)	

# - view photos for albums
@app.route('/view/album/photo', methods=['GET', 'POST'])
def view_album():
	if request.method == 'POST':
		albumid = request.form.get('albums')
		albumname = getAlbumName(albumid)
		print albumid
		return render_template("photo.html", photos=getAlbumPhotos(albumid), tags = getAllTags(), attribute = 'Album', aname = albumname[0][0])

# - view photos for pop tags
@app.route('/view/poptag/photo/', methods=['GET', 'POST'])
def show_pop_tag_photos():
	if request.method == 'POST':
		tagname = request.form.get('tagname')
		return render_template("photo.html", photos=getAllTagPhotos(tagname), tags = getAllTags(), attribute = 'Tag', aname = tagname)

# - view photos via searching tags
@app.route('/view/search/photo/', methods=['GET', 'POST'])
def photo_search():
	if request.method == 'POST':
		tagnames = request.form.get('name')
		# print tagname
		pics = getAllPhotos()
		picids = getSearchedPhotoId(tagnames, pics)
		return render_template("photo.html", photos=getPicById(picids), tags = getAllTags(), attribute = 'Tag', recom = 'Search')

# - delete photo
@app.route('/hello/photo/delete/<picture_id>')
@flask_login.login_required
def delete_photo(picture_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)

	cursor = conn.cursor()
	if cursor.execute("SELECT * FROM Pictures WHERE picture_id = '{0}' AND user_id = '{1}'".format(picture_id, uid)):
		cursor.execute("DELETE FROM Taged_by WHERE picture_id ='{0}'".format(picture_id))
		cursor.execute("DELETE FROM Pictures WHERE picture_id ='{0}'".format(picture_id))
		conn.commit()
		uid = getUserIdFromEmail(flask_login.current_user.id)
		return render_template('hello.html', message='Your deleted your photo', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())#comments= getComments()
	else:
		return '''
			<a href='/'>You don't have authorization to delete the photo!</a>
			'''
	

def add_like(picid):
	cursor = conn.cursor()
	cursor.execute("UPDATE Pictures SET likes = likes + 1 WHERE picture_id ='{0}'".format(picid))
	conn.commit()
	return

# - 
@app.route('/hello/like/<picture_id>', methods=['POST','GET'])
def like(picture_id):
	add_like(picture_id)
	return render_template('hello.html', message='You liked a photo', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())
	



# - add new comment
@app.route('/comment/new/<picture_id>', methods=['POST','GET'])
# @flask_login.login_required
def add_comment(picture_id):
	if current_user.is_authenticated():
		uid = getUserIdFromEmail(flask_login.current_user.id)
	else:
		uid = None
	content = request.form.get('comment')
	date = datetime.datetime.now()
	userid = getUserId(picture_id)
	print userid
	cursor = conn.cursor()
	if userid and uid == userid[0][0]:
		return '''
			<a href='/'>You can't comment on your own photos!</a>
			'''
	elif uid != None:
		cursor.execute("INSERT INTO Comments (comment_text, user_id, picture_id, create_date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(content, uid, picture_id, date))
		update(uid)
	else:
		cursor.execute("INSERT INTO Comments (comment_text, picture_id, create_date) VALUES ('{0}', '{1}', '{2}')".format(content, picture_id, date))
	conn.commit()
	return render_template('hello.html', message='You comment on a photo', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())


def getUserId(picid):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Comments WHERE picture_id = '{0}'".format(picid))
	return cursor.fetchall()

# - show comment
@app.route('/comment/show/<picture_id>', methods=['POST','GET'])
def show_comment(picture_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('comment.html', message='You comment on a photo', photos=getAllPhotos(), comments = getComments(picture_id))

def getSimilarTag(tagnames):
	taglist = stringToArray(tagnames)
	dic = {}

	for i in taglist:
		cursor = conn.cursor()
		cursor.execute("SELECT COUNT(tag_name) from Taged_by WHERE tag_name = '{0}' GROUP BY tag_name ".format(i))

		j = cursor.fetchall()
		dic[i] = j[0][0]
	return sorted(dic.items(), key=lambda e:e[1], reverse=True) # return a list like [(key, value),...]

# - get recommendation photoids
def getPicRecom(photos):
	taglist = getPopTags()
	dic = {}
	for pic in photos:
		count = 0
		for i in taglist:
			cursor = conn.cursor()
			if cursor.execute("SELECT tag_name, picture_id FROM Taged_by WHERE tag_name = '{0}' AND picture_id = '{1}'".format(i, pic[1])):
				count = count + 1
		dic[pic[1]] = count
	temp = sorted(dic.items(), key=lambda e:e[1], reverse=True) # return a list like [(key, value),...]
	res = []
	c = 0
	for item in temp:
		if (c >= 5):
			break
		res.append(item[0])
		c = c + 1 
	return res

def getPicById(picids):
	photos = []
	for i in picids:
		cursor = conn.cursor()
		cursor.execute("SELECT imgdata, picture_id, caption, likes, user_id FROM Pictures WHERE picture_id = '{0}'".format(i))
		temp = cursor.fetchall()
		photos.append(temp[0])
	return photos

# - show recommendation, require login
@app.route('/recommendation', methods=['GET', 'POST'])
@flask_login.login_required
def show_recom():
	pics = getAllPhotos()
	picids = getPicRecom(pics)
	return render_template('recommendation.html', photos = getPicById(picids), tags = getAllTags(), recom = 'Recommendation')
	# return render_template('recommendation.html')

# - show recommendation tags, require login
@app.route('/recommendation/tag', methods=['GET', 'POST'])
@flask_login.login_required
def get_tag_recom():
	tags = request.form.get('inputtags')
	photos = getAllPhotos()
	retags = getReTags(tags, photos)
	print 'sum:'
	print len(retags)
	pics = getAllPhotos()
	picids = getPicRecom(pics)
	return render_template('recommendation.html', photos = getPicById(picids), retags = getReTags(tags, photos), recom = 'Recommendation')
	pass


def getReTags(tags, photos):
	picids = getSearchedPhotoId(tags, photos) # list
	dic = {}
	cursor = conn.cursor()
	for picid in picids:
		cursor.execute("SELECT tag_name, COUNT(tag_name) FROM Taged_by WHERE picture_id = '{0}' GROUP BY tag_name".format(picid))
		res = cursor.fetchall()
		dic[res[0][0]] = res[0][1] 
	lists = sorted(dic.items(), key=lambda e:e[1], reverse=True) # list like [(, ), (, ), ...]
	result = []
	count = 0
	for i in lists:
		if count == 3:
			break
		result.append(i[0])
		count = count + 1
	return result




def getAllUser():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, firstname, lastname FROM Users")
	return cursor.fetchall()

def getTopUsers():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, firstname, lastname FROM Users GROUP BY user_id ORDER BY count DESC LIMIT 10")
	a =  cursor.fetchall()
	print a
	return a
	# users = getAllUser()
	# dic = {}
	# for user in users:
	# 	count = 0
	# 	cursor = conn.cursor()
	# 	cursor.execute("SELECT COUNT(picture_id) FROM Pictures WHERE user_id = '{0}'".format(user[0]))
	# 	num1 = cursor.fetchall()
	# 	cursor.execute("SELECT COUNT(picture_id) FROM Comments WHERE user_id = '{0}'".format(user[0]))
	# 	num2 = cursor.fetchall()
		
	# 	for i in taglist:
	# 		cursor = conn.cursor()
	# 		if cursor.execute("SELECT tag_name, picture_id FROM Taged_by WHERE tag_name = '{0}' AND picture_id = '{1}'".format(i, pic[1])):
	# 			count = count + 1
	# 	dic[pic[1]] = count
	# temp = sorted(dic.items(), key=lambda e:e[1], reverse=True) # return a list like [(key, value),...]
	# return topusers




# - default page with all the photo 
@app.route("/", methods=['GET'])
def hello():
	# uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', message='Welecome to Photoshare', photos=getAllPhotos(), tags = getAllTags(), topusers = getTopUsers())


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)