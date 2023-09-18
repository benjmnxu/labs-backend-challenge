used openai, textdistance.
installed flask-caching but unimplemented

Initially created three main models: Club, User, and Tag
Club and User self-explanatory. Tag was created as opposed to a field of 
Club in order to model a many-to-many relationship, allowing query of all clubs
described by a certain tag. 

For users, it was important that they had a unique id and username to differentiate
their account from others. Id is a vestigial structure left over from when usernames
were allowed to be duplicated. Other fields: year, major, and clubs are important indicators
for the website as they provide a sense of who a reviewer is and how much they can be trusted.

For clubs, there are similar explanations for the identifiers. Other fields are self-explanatory
as they describe the club itself.

Created extensions.py to fix SQLAlchemy instance issues. Puting db into a separate class, then
import it prevented circular imports and multiple conficting instances. 

For authentification, I created a seperate table called ActiveUser. This allows users to be tracked
as to when they are using the website. Their active user is associated with their profile in User,
and authentification required apis will only work if the linking table active_user contains the 
ActiveUser instance.

This also means that every api feature that requires authentification is accessed not by User but ActiveUser, requiring each api call to include the current_user field. This creates an outward facing user and an inwards facing user.

Database populated by clubs scraped from pennclubs.com.
Implemented limit unit tests to test api connection and connectivity


/api/get_user:
Auth required
required: (str) current_user, (str) username.
Here, the current_user is the aforementioned active user and the username is the username of the user to get. Returns a users year, major, and clubs that they are a part of.

/api/search_clus:
Auth not required.
Required: (str) name
"name" is a substring and the api will return any club whos name includes "name"

/api/add_club:
Auth required.
Required: (str) code, (str) name, (str) description
optional: (str or List[str])  tags


/api/favorite_club:
Auth required.
Required: (str) code, (str) current_user

/api/modify_club:
Auth required.
Required: (str) current_user, (str) code
Optional: (str) description, (str) name, (List[str]) add_members, (List[str]) remove_members, (List[str]) add_tags, (List[str]) remove_tags

/api/tags:
Auth not required
returns multiple lists of clubs by distinct tag

Additional route features:


/api/comment:
Allows user to comment on clubs and reply to other comments. All comments associated with a club can be seen with /api/clubs.

/api/upload_files:
Allows users to upload club-related files to the database. Will be associated and returned with /api/clubs

/api/recommend_tags:
Uses openai's GPT to generate recommended tags based off of a club's description. Thisi allows for the user to easily grab tags and modify the club. Prefers to use pre-existing tags as to avoid creating too many different tags.

/api/similar_clubs:
Uses sentence-transformer to convert descriptions into vectors, then measures cosine similarity This allows the api to recommend new clubs to the user that are similar to their specified. Can specify the number of clubs to recommend. 

