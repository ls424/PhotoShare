DROP DATABASE photoshare;
CREATE DATABASE photoshare;
USE photoshare;
-- DROP TABLE Pictures CASCADE;
-- DROP TABLE Users CASCADE;

CREATE TABLE Users (
    user_id int4 NOT NULL AUTO_INCREMENT,
    email varchar(255) UNIQUE NOT NULL,
    password varchar(255) NOT NULL,
    firstname varchar(255) NOT NULL,
    lastname varchar(255) NOT NULL,
    birthday varchar(255) NOT NULL,
    hometown varchar(255) NOT NULL,
    gender varchar(5) NOT NULL,
    count int4 DEFAULT 0,
    PRIMARY KEY (user_id)
  #CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums
(
  album_id int4 NOT NULL AUTO_INCREMENT,
  name varchar(255) UNIQUE NOT NULL,
  user_id int4 NOT NULL,
  create_date date,
  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures
(
  picture_id int4 NOT NULL AUTO_INCREMENT,
  user_id int4,
  album_id int4,
  imgdata longblob,
  caption VARCHAR(255),
  likes int4 DEFAULT 0,
  PRIMARY KEY (picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE
);

-- CREATE TABLE Have_photo
-- (
--   picture_id int4 NOT NULL,
--   album_id int4 NOT NULL,
--   PRIMARY KEY picture_id,
--   FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
--   FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE NO ACTION
-- );

-- CREATE TABLE Own_albums
-- (
--   user_id int4 NOT NULL,
--   album_name int4 NOT NULL,
--   PRIMARY KEY (album_id),
--   FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE NO ACTION,
--   FOREIGN KEY (album_id) REFERENCES Albums(album_id)
-- );

-- CREATE TABLE Tags
-- (
--   tag_name varchar(255),
--   PRIMARY KEY (tag_name)
-- );

CREATE TABLE Comments
(
  comment_id int4 NOT NULL AUTO_INCREMENT,
  comment_text varchar(255),
  user_id int4,
  picture_id int4,
  create_date varchar(255),
  PRIMARY KEY (comment_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

-- CREATE TABLE Comment_by
-- (
--   picture_id int4 NOT NULL,
--   comment_id int4,
--   PRIMARY KEY (comment_id),
--   FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE NO ACTION,
--   FOREIGN KEY (comment_id) REFERENCES Comments(comment_id)
-- );

CREATE TABLE Taged_by
(
  picture_id int4 NOT NULL,
  tag_name varchar(255),
  PRIMARY KEY (picture_id, tag_name),
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
  -- FOREIGN KEY (tag_name) REFERENCES Tags(tag_name)
);

CREATE TABLE Follow_to
(
  user1_id int4 NOT NULL,
  user2_id int4 NOT NULL,
  PRIMARY KEY (user1_id, user2_id),
  FOREIGN KEY (user1_id) REFERENCES Users(user_id),
  FOREIGN KEY (user2_id) REFERENCES Users(user_id)
);





INSERT INTO Users (email, password, firstname, lastname, birthday, hometown, gender) VALUES ('test1@bu.edu', 'test1', 'f1', 'l1', '1990.1.1','wa', 'male');
INSERT INTO Users (email, password, firstname, lastname, birthday, hometown, gender) VALUES ('test2@bu.edu', 'test2', 'f2', 'l2', '1991.2.2','ma', 'fmale');
