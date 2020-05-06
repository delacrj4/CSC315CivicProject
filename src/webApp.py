# Fix jinja encoding error
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import psycopg2
from config import config
from flask import Flask, render_template, request

# Global Variables
emailG = ''
fnameG = ''
userIdG = -1

def connect(query):
    """ Connect to the database server """
    conn = None
    try:
        # Connect to the Postgres server
        conn = psycopg2.connect(host='localhost', port = 5432, database = 'proj', user = 'osc', password = 'osc')
        conn.autocommit = True

        print('Connected')
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a query
        if query is not '':
            cur.execute(query)
        
        # Get query result
        if cur.description is not None:
            rows = cur.fetchall()
        else:
            rows = [['No results fetched']]
        
        # Terminate the connection
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection terminated')
    # Return query result
    return rows

# Create flask instance
app = Flask(__name__)

# Display home page
@app.route('/')
def renderIndexPage():
    return render_template('index.html', fnameH=fnameG)

# Display login page
@app.route('/account/login')
def accountLoginForm():
    return render_template('accountLogin.html')

# Login form - redirected to newsfeed page
@app.route('/newsfeed', methods=['POST'])
def newsfeedPage():
    global userIdG, emailG, fnameG

    # Submited from login form
    email = request.form['email']
    password = request.form['psw']

    # Attempt login
    query = 'SELECT user_id FROM account WHERE eMail=\'' + email + '\' AND password=\'' + password + '\';'
    queryResult = connect(query)

    # Invalid email or password - reload page 
    if not queryResult:
	return render_template('accountLogin.html')

    # Assign global vars
    userIdG = queryResult[0][0]
    emailG = email

    # Get first name from database
    query = 'SELECT fname FROM account WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    fnameG = queryResult[0]

    # Get all articles from database
    query = 'SELECT * FROM newsfeed;'
    queryResult = connect(query)
    
    # Remove media_id from article results for display purposes
    articles = []
    count = 1
    for x in range(0, len(queryResult)):
        tempList = []
        tempList.append(count)
        for y in range(1, 5):
            tempList.append(queryResult[x][y])
        articles.append(tempList)
        count += 1

    return render_template('newsfeed.html', fnameH=fnameG, articlesH=articles)

# Signed out - redirected to home page
@app.route('/account/signed-out', methods=['POST'])
def signedOut():
    global userIdG, emailG, fnameG

    # Reset global vars
    userIdG = -1
    emailG = ''
    fnameG = ''

    return render_template('index.html')

# Display register page
@app.route('/account/register')
def renderAccountPage():
    return render_template('accountRegister.html')

# Register form - redirected to preferences page
@app.route('/account/new-user/preferences', methods=['POST'])
def accountRegisterForm():
    global emailG, fnameG

    # Submitted from register form
    fnameG = request.form['fname']
    lname = request.form['lname']
    resCounty = request.form['resCounty']
    city = request.form['city']
    zipCode = request.form['zipCode']
    emailG = request.form['email']
    password = request.form['psw']
    repeatPassword = request.form['repeat-psw']
    
    # Check password spelling
    # Reload page if passwords don't match
    if password != repeatPassword:
        return render_template('accountRegister.html')
    
    # Add account to database
    query = 'INSERT INTO account (user_id, eMail, password, fname, lname) VALUES (DEFAULT, \'' + emailG + '\', \'' + password + '\', \'' + fnameG + '\', \'' + lname + '\');'
    connect(query)
    
    # Set default data
    setDefaultData(password)

    # Add residence to database
    query = 'INSERT INTO residence (user_id, county, city, zip_code) VALUES (' + str(userIdG) + ', \'' + resCounty + '\', \'' + city + '\', \'' + zipCode + '\');'
    connect(query)

    return render_template('preferences.html', fnameH=fnameG, lnameH=lname, resCountyH=resCounty, cityH=city, zipCodeH=zipCode, emailH=emailG, notification='on', prefCounty='Atlantic')

def setDefaultData(password):
    global userIdG, emailG

    # Get userID
    query = 'SELECT user_id FROM account WHERE eMail=\'' + emailG + '\' AND password=\'' + password + '\';'
    queryResult = connect(query)[0]
    userIdG = queryResult[0]
    
    # Add default preferences
    query = 'INSERT INTO preferences (user_id, notification, pref_region) VALUES (' + str(userIdG) + ', \'on\', \'Atlantic\');'
    connect(query)

# Display preferences page
@app.route('/account/preferences')
def renderPreferencesPage():
    global userIdG, emailG, fnameG

    # Get last name from database
    query = 'SELECT lname FROM account WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    lname = queryResult[0]

    # Get res county from database
    query = 'SELECT county FROM residence WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    resCounty = queryResult[0]

    # Get city from database
    query = 'SELECT city FROM residence WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    city = queryResult[0]

    # Get zip code from database
    query = 'SELECT zip_code FROM residence WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    zipCode = queryResult[0]

    # Get notification preference from database
    query = 'SELECT notification FROM preferences WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    notification = queryResult[0]

    # Get preferred county from database
    query = 'SELECT pref_region FROM preferences WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    prefCounty = queryResult[0]

    return render_template('preferences.html', fnameH=fnameG, lnameH=lname, resCountyH=resCounty, cityH=city, zipCodeH=zipCode, emailH=emailG, notificationH=notification, prefCountyH=prefCounty)

# Update preferences form
@app.route('/account/update-preferences', methods=['POST'])
def updatePreferences():
    global userIdG, emailG, fnameG

    # Submitted from preferences form
    fname = request.form['fname']
    lname = request.form['lname']
    resCounty = request.form['resCounty']
    city = request.form['city']
    zipCode = request.form['zipCode']
    email = request.form['email']
    oldPassword = request.form['oldPsw']
    newPassword = request.form['newPsw']
    notification = request.form['notification']
    prefCounty = request.form['prefRegion']
    deleteMe = request.form['deleteMe']

    # --Update first name-- #
    #
    if fname != '':
        fnameG = fname

        query = 'UPDATE account SET fname=\'' + fnameG + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)

    # --Update last name-- #
    #
    if lname != '':
        query = 'UPDATE account SET lname=\'' + lname + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)
    else: # Get last name from database
        query = 'SELECT lname FROM account WHERE user_id=' + str(userIdG) + ';'
        queryResult = connect(query)[0]
        lname = queryResult[0]

    # --Update Address-- #
    #
    if resCounty != '': # Update res county
        query = 'UPDATE residence SET county=\'' + resCounty + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)
    else: # Get res county from database
        query = 'SELECT county FROM residence WHERE user_id=' + str(userIdG) + ';'
        queryResult = connect(query)[0]
        resCounty = queryResult[0]
    if city != '': # Update city
        query = 'UPDATE residence SET city=\'' + city + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)
    else: # Get city from database
        query = 'SELECT city FROM residence WHERE user_id=' + str(userIdG) + ';'
        queryResult = connect(query)[0]
        city = queryResult[0]
    if zipCode != '': # Update zip code
        query = 'UPDATE residence SET zip_code=\'' + zipCode + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)
    else: # Get zip code from database
        query = 'SELECT zip_code FROM residence WHERE user_id=' + str(userIdG) + ';'
        queryResult = connect(query)[0]
        zipCode = queryResult[0]

    # --Update email-- #
    #
    if email != '':
        emailG = email
        query = 'UPDATE account SET eMail=\'' + emailG + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)

    # --Update password-- #
    #
    query = 'SELECT password FROM account WHERE user_id=' + str(userIdG) + ';'
    queryResult = connect(query)[0]
    currPassword = queryResult[0]

    if oldPassword == currPassword:
        if oldPassword != '' and newPassword != '':
            query = 'UPDATE account SET password=\'' + newPassword + '\' WHERE user_id=' + str(userIdG) + ';'
            connect(query)
    
    # --Update notification-- #
    #
    query = 'UPDATE preferences SET notification=\'' + notification + '\' WHERE user_id=' + str(userIdG) + ';'
    connect(query)

    # --Update preferred county-- #
    #
    if prefCounty != 'Choose':
        query = 'UPDATE preferences SET pref_region=\'' + prefCounty + '\' WHERE user_id=' + str(userIdG) + ';'
        connect(query)
    else: # Get preferred county from database
        query = 'SELECT pref_region FROM preferences WHERE user_id=' + str(userIdG) + ';'
        queryResult = connect(query)[0]
        prefCounty = queryResult[0]

    # Delete Account
    if deleteMe == 'DELETE ME':
        query = 'DELETE FROM residence WHERE user_id=' + str(userIdG) + ';'
        connect(query)
        query = 'DELETE FROM preferences WHERE user_id=' + str(userIdG) + ';'
        connect(query)
        query = 'DELETE FROM account WHERE user_id=' + str(userIdG) + ';'
        connect(query)
        
        # Reset global vars
        userIdG = -1
        emailG = ''
        fnameG = ''

        return render_template('index.html') # Redirct to home page

    return render_template('preferences.html', fnameH=fnameG, lnameH=lname, resCountyH=resCounty, cityH=city, zipCodeH=zipCode, emailH=emailG, notificationH=notification, prefCountyH=prefCounty)

# Display newsfeed webpage
@app.route('/newsfeed')
def renderNewsfeedPage():
    # Get all articles from database
    query = 'SELECT * FROM newsfeed'
    queryResult = connect(query)
    
    # Remove media_id from article results for display purposes
    articles = []
    count = 1
    for x in range(0, len(queryResult)):
        tempList = []
        tempList.append(count)
        for y in range(1, 5):
            tempList.append(queryResult[x][y])
        articles.append(tempList)
        count += 1


    return render_template('newsfeed.html', fnameH=fnameG, articlesH=articles)

# Newsfeed filter form
@app.route('/newsfeed/filtered', methods=['POST'])
def filterArticles():
    # Submitted from filtered articles form
    tags = request.form.getlist('tags')
    
    query = 'SELECT * FROM newsfeed'
    if len(tags) == 1:
        query += ' WHERE topic=\'' + tags[0] + '\''
    elif len(tags) > 1:
        query += ' WHERE topic=\'' + tags[0] + '\''
        for x in range(1, len(tags)):
            print('testing')
            query += ' or topic=\'' + tags[x] + '\''
    
    query += ';'
    
    queryResult = connect(query)

    # Remove media_id from article results for display purposes
    articles = []
    count = 1
    for x in range(0, len(queryResult)):
        tempList = []
        tempList.append(count)
        for y in range(1, 5):
            tempList.append(queryResult[x][y])
        articles.append(tempList)
        count += 1
    
    return render_template('newsfeed.html', fnameH=fnameG, articlesH=articles)

if __name__ == '__main__':
    app.run(debug = True)
