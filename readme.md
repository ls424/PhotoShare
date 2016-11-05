#Introduction

This is a full-stack website that using Mysql, Flask and Python to implement photo share and recommendation function.

##Features:

#####Tag management
Viewing your photos by tag name. 
Viewing all photos by tag name. 
Viewing the most popular tags. 
Photo search. 
#####Comments
Leaving comments
Like functionality
#####Recommendations
'You-may-also-like' functionality
	Tag recommendation functionality



#Installation


##Database setup: (for ubuntu)
First make sure you have Mysqlinstalled on your machine:

####For Linux:
Then start mysql:
```
mysql -u root -p
```
password is None so just press enter.
```
source ./schema.sql 
```
Now quit MySQL (enter CTRL-D or \q)

####For windows:
Open Mysql CommandLine then:
```
SOURCE FULL Path/shcema.sql
```

##Application Setup:
```
virtualenv photoenv
source photoenv/bin/activate #use Full Path/Scripts/activate on windows
pip install -r requirements.txt
python app.py
```
Remember that, before running the app, change the mysql password to your own, it is defaulted in the code as 'password'.
You can now point your favorite web brower to [localhost:5000](localhost:5000) to see your web app. 
