# flaskboost

Experimental project to build in robust features for flask

## Why Flaskboost

### The new kid on the block

> "Achieve the shortest schedules, least effort, and highest levels of user satisfaction." 
> 
> -- Capers Jones, Applied Software Measurement: Assuring Productivity and Quality, 1991.

We are currently in a [post-industrial society](https://en.wikipedia.org/wiki/Post-industrial_society), where the service sector generates more wealth than the manufacturing sector. This causes the rising of service tech sector, which changes the requirements of application development dramatically in two major ways: 

* Smaller development team size
	* More and more robust and easy to use software frameworks/tools has been created target on building services, for example Android Studio, NodeJs, Flask, and much more. The frameworks reduces the difficulty to develop a service, hence allows team in major tech companies (like Google and Microsoft) and startups to have a **smaller team size**.
* Development speed is critical
	* The speed of developing and testing an idea is critical for project survival, and sometimes the companies which own the project. In general better development speed means release a service faster than competitors, be more satisfied by customers, less failure rate, and potentially more investment from investors (for startups).

So the application development frameworks has to accommodate smaller teams with high speed. 

### Think fast, develop faster

The primary object of this project is to speed up idea prototyping phase, which in terms decreasing the time spend start from solid ideas, building, shipment and user testing. 

It achieves the speed up primarily by the following:

* Strict isolation on MVC
* Building robust controllers to fit most of website needs
* Speeding up front end development by advanced template system
* Aiding Developers in everyday operations by utility tools 
* Exposing bugs by tracking tools
* Interpreting and analysing the user feedback by additional tools

This repo is part of experiments conducting for rapid development framework (RDF), to boost speed and quality of the development process for startups. This project is only focus on application in flask and python development environment. If it works well, more frameworks, languages, and different platforms support will come soon.

### The Sacrifices & Drawbacks

No one is perfect. The framework speed up development process, but with some costs. Here is a list of guesses of drawbacks that **may** cost you: 

* Low application speed
	* High development speed in general comes with the cost of low application speed. For example python has high development speed and low application speed. (or is it? look at Youtube)
* Flexibility of infrastructure
	* The framework increase development speed with a great cost of sacrifices what infrastructure you can choose to use. For example you can not choose Microsoft Azure database, or your own server to serve static files. **BUT** because you have all the source code, you can easily switch to another one in post release. 
* Slower speed and high cost in post release
	* Our idea is to speed up before service release as much as possible, the post release speed is treated as secondary priority. The reason is that we expect development teams have more resources (developers, funding...) after release.

### What is extra from flask?

* Developing
	* Strict logic decoupling by modules 
	* Realtime DBs support with OO design
	* Rapid template system based on popular JS library
* Debugging
	* Utilities functions
	* Predefined errors and handling
* Deploying
	* Environment settings isolation

### A late Santa for you

If you just started a new flask project, flask boost allows you to build on a well organised structure with necessary and powerful features you need to start your website. If you already have a flask website, this repo can help you to learn how to build additional features you need.  Both rookies and veterans friendly. 

### Principles & Priorities

Follows the guidelines of RDF, the project is trying to accommodates all the following criteria at the same time. But if there is a conflict, which comes first has priority:

* Security
	* Data Loss
	* Data Breach
	* Availability
* Development Speed
	* Low Bug Tolerance
	* Maintainability
	* Code Readability
	* Flexibility (for propose of your application)
* Production Server Running Speed
	* Request Handling Speed (single thread)
	* Scalability

If there is a conflict in any part of design, it should be specified in the trade-off section.

The followings does **not** have priority:

* Flexibility (to switch development components like library, db...)

### Current Status

Messy, experimental and not tested. Use at your own risk.

Currently can deploy on Heroku server. More servers support in future.

## Contents

* Experienced User Guide
	* To Do List
	* Cheatsheet
		* SQLAlchemy
* User Guide
	* Local Development Environment
	* Remote Production Environment
	* Testing Environment (Coming soon)		
* Server Coding
	* Coding Styles
	* Structure
	* Runtime Management
	* Testing
* Controllers: feature Sets
	* User Management
	* Admin Panel
	* Payment System (Optional)
* Models: Database & Storage
	* Relational Database
	* Realtime Database (Optional)
	* Upload Storage (Optional)
* Views: Templates & Looks
	* Static Files Management
	* Rapid Template System
* Developers utilities
	* Setup Runtime
	* Sync Data
		* Database
		* Static Files
* Trade-Offs
* Definitions

## Experienced User Guide

### To Do List

If you are not familiar with flask and this framework, escape to the next section.

All required modifications except secrets have a **CRUMB** marker in comments, and optional modifications has **CANDY** markers.

* Download credential file from Firebase to "settings/firebase_cred.json"
* Set general settings in "settings/settings.py"
	* app_name
	* reset_db
* Set Secrets in "**settings/secrets.py**":
	* Secret class 
		* local_secret
		* remote_secret
	* DBs class
		* local_db_user
		* remote_db_user
		* local_db_password
		* remote_db_password
		* local_db_location
		* remote_db_location
		* local_db_name
		* remote_db_name
	* realtime class
		* local_realtime_url
		* local_realtime_cred_path
		* local_realtime_api_key
		* remote_realtime_url
		* remote_realtime_cred_path
		* remote_realtime_api_key
* Set relational database models in "**dbs.py**"
	* (Optional) Add user fields , for each one:
		* Add new fields in "\__init__" within User model
	* (Optional) Add additional roles in _init_roles function, for each one:
		* add additional test users in _init_roles function
	* Add additional tables, for each one:
		* add additional table reference into fetch function
		* Add additional table tests in _init_data function
* Set Realtime Database Models in "**firedbs.py**"
	* add additional realtime models, for each one:
		* add building sequence helpers
		* add fetch path and getter helpers
		* call _rebuild functions to additional tables in _remove_db function
		* get dependency from relational db and fetch them in _init_data function
		* add additional model tests in _init_data

### Cheatsheet

#### SQLAlchemy

##### Index:

First integer or manual primary key

```python

# ---- Index ----
db.Column(db.Integer(), primary_key=True) 

# ---- Row ----
# time
db.Column(db.DateTime())

# Unique
db.Column(db.String(50), nullable=False, unique=True)

# Nullable
db.Column(db.String(50), nullable=False, default='')

# Unique nullable (allow null, and unique if it is not null)
db.Column(db.String(50), unique=True, nullable=True)

# ---- Foreign Key ----
# Link By Secondary Table
db.relationship('table', secondary='secondary_table',
            backref=db.backref('my_table_reference', lazy='dynamic'))

# Secondary Table Entry
db.Column(db.Integer(), db.ForeignKey('table.index', ondelete='CASCADE'))

# Link to table itself
# Create a secondary table, with two entries link to current table
db.relationship('secondary_table', backref='entry_reference', primaryjoin=INDEX==secondary_table.entry_name)
```

## User Guide

### Setting Up - Local Development

#### Databases

In order to start play around, you need a running relational DBs, we recommend set up PostgreSQL locally. You need to finish the following tasks, and depend on the OS environment you are using, the instructions might be vary, we are not going to include here. Keep in mind that there are tools out there like pgAdmin that can help you. The tasks are following: 

* Create new local database
* Create access account within new database, owner access account would be optimal
* Record account username and password
* Fill in your secret file in "setting/secrets.py":
	* local_db_user
	* local_db_password
	* local_db_name
	* local_db_location

After this, you need to setup the realtime db. We currently only support firebase. The following tasks are required to setup minimum authentication, but it may be outdated by the time you are using it, depend on if there is change in firebase web interface:

* Create a firebase account
* Create a new project
* Go into the project, enable email authentication
	* Go to "Authentication/SIGN-IN METHOD" section, enable email/password
* Add a new user for authentication
	* Go to "Authentication/USERS", add a email and password
* Record project id and API key
	* Click the setting sign at the right side of overview, go to project settings, record project id and API key
* Fill in your secret file in "setting/secrets.py":
	* realtime_db_url, follow this format:
		* https://YOUR_PROJECT_ID.firebaseio.com/
	* realtime_api_key
	* realtime_secret
		* a path to the credential file relative to "setting" folder
	* realtime_auth_email
	* realtime_auth_password

#### Environment Variables

If you already know how environment variables works, skip this section.

The first step is to tell what the server is running on, by export the environment variables. 

Depend on if it is development/production/testing, ways of exporting environment are different. We will discuss different ways to set up in different runtime. 

Local:

* Local environment is set up by "export" Linux command.

Production: 

* Normally server environment like Heroku have [dev friendly environments](https://devcenter.heroku.com/articles/heroku-local#set-up-your-local-environment-variables). Recommend to follow your own server setups. 

### Setting Reference List

#### Secret & flexible Information:

Modify the following variables in settings/settings.py:

* app_name: name of the website
* reset_db: if the db is going to reset every time server reboot
	* testing default: True
	* production default: False

Create a file under folder "settings" called "secret.py", and record the following variables:

* encryption
	* local_secret
	* remote_secret
* DB related
	* local information
		* local_db_user
		* local_db_password
		* local_db_name
	* Remote
		* remote_db_user
		* remote_db_password
		* remote_db_name
* General setting

##### Must-have environment variables:

* RUNTIME
	* One of development / production / testing

## Server Coding

### Coding Styles

Coding styles follows [PEP 8](https://www.python.org/dev/peps/pep-0008/). 

### Structure

Flask server structure in this project follows [offical flask guideline for larger application](http://flask.pocoo.org/docs/0.12/patterns/packages/), and [hitchhiker's guide to python - structuring project](http://docs.python-guide.org/en/latest/writing/structure/). 

### Runtime Management

There are several kinds of runtime environment:

* Development: local running environment
* Production: actual server running environment
* Testing: testing environment

Different environments has different settings:

* Debug information visibility
* Deploy pipeline
* Database connection
* Static files serving


## Trade-Offs

### Database Type

For the choice of database type, we considered other types, and eventually selected relational database: PostgreSQL, primarily for its reliability and speed. Here is a list of types and reason of denying:

* Other relational DBs
	* Compare with PostgreSQL, other relational DBs have lower reliability, hence decrease data security.
* NoSQL in general
	* NoSQL has lower speed in terms of single data entry fetching speed, which is the primary the operation main database should perform.
	* Without abstract layer relational management like SQLAlchemy, it increases the chance of developer making bugs, reduce development speed.

## Definitions

* Basic Needs
	* Basic needs are a set of general needs in order for most of websites to function. Here is the list:
		* User Management
		* Admin Data Management
		* Static File Serving
		* Secure Communication
* Feature Needs
	* Feature needs are any functionality that is not basic needs. For examples, chatting with customer service, uploading photo.
* Main Database
	* Main Database is the database that holds the most basic information needed for the website, and most likely have relative heavy load since it links everything together. If there is secondary databases, main database can be used to check data integrity. 
	* For example: a real time database to store chat data, that use the user information in main database for integrity checking.