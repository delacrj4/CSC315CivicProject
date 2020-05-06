<h1>CSC315-01 Collaborative Project</h1>
<h2>Webpage Alternative to CivicStory</h2></br>
Members: Amulya Badineni, Julian De La Cruz, Alhasssane Traore, Adam Mellan

<h3>Project Goal:</h3>
The goal of the project is to allow users to create an account and select specific preferences. By having accounts, the target audience of the website is defined. The content of CivicStory will be then filtered according to a user’s preferences so that they can then get a custom feed that displays media content based on a certain tag. This feature can be enhanced by adding different types of filters.


<h4>How to run:</h4>
<p>
This webpage utilizes PostgreSQL, Flask, HTML, and CSS</br>
1. Download src folder</br>
2. cd into src folder using the terminal</br>
3. Run the following commands</br>
      - sudo apt-get update</br>
      - sudo apt-get install postgresql-12</br>
      - sudo apt-get install postgres-psycopg2</br>
      - sudo apt-get install python2.7</br>
      - sudo apt-get install python-pip</br>
      - pip install flask</br>
4. run: </br>
      - Sudo postgres -u psql</br>
      - ALTER USER osc WITH SUPERUSER;</br>
      - ALTER USER osc WITH CREATEROLE;</br>
      - ALTER USER osc WITH CREATEDB;</br>
      - ALTER USER osc PASSWORD ‘osc’;</br>
      - createdb civicstoryDB</br>
      - psql civicstory</br>
      - copy the contents of create-tables.txt into the terminal and press enter</br>
5. run: python webApp.py</br>
6. Go to the browser and type use the url: 127.0.0.1:5000</br>
</p>

Home page:
![alt text](images/home.png)

Register page:
![alt text](images/register.png)

Login page:
![alt text](images/login.png)

Preferences page:
![alt text](images/preferences.png)

Newsfeed page:
![alt text](images/newsfeed.png)

