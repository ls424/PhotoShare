#Introduction

This is a full-stack website that using Mysql, Flask and Python to implement photo share and recommendation function.

##Features:
#####1 Tag management:
       1.1 Viewing your photos by tag name
       1.2 Viewing all photos by tag name
       1.3 Viewing the most popular tags
       1.4 Photo search

#####2 Comments:
       2.1 Leaving comments
       2.2 Like functionality

#####3 Recommendations:
       3.1 'You-may-also-like' functionality
       3.2 Tag recommendation functionality


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

#More To Do:
#####So far, the app is running locally for single-user test, it could be improved with multi-user usage with adding session.
#####In addition, the api could be redesigned to rest api and adding more stuff to front-end with better user experience.
#####More to go, the app could be hosted by Nignx deployed on AWS for public access. Then the database has to be on cloud accrodingly. 
#####When the user gets more and more, we might need a distributed system to improve the performance.
