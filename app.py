import os
from flask import Flask
import os
from urlparse import urlsplit
from pymongo import Connection
import library
import json
from datetime import datetime

url = os.getenv('MONGOLAB_URI', 'mongodb://heroku_app12633543:e4kprjp4r1kj0bbv9f4gih4km@dbh44.mongolab.com:27447/heroku_app12633543')
parsed = urlsplit(url)
db_name = parsed.path[1:]


store=library.Store()

# Get your DB
db = Connection(url)[db_name]

# Authenticate
if '@' in url:
    user_pass = parsed.netloc.split('@')[0].split(':')
    db.authenticate(user_pass[0], user_pass[1])

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

def update_db():
    store.load_all('prueba.json')
    stats=store.get_stats()
    db.logs.insert({'time':str(datetime.now())})
    db.stats.insert(stats)
    orgs = db.orgs
    db.orgs.ensure_index('name',30)
    for org in store.orgs:
        orgdb=orgs.update({'name':org},
                {'name': org, 'data':store.orgs[org]},
                upsert=True,
                w=0)
    users = db.users
    for user in store.users:
        print "User:%s"%user
        print ">%s"%store.users[user]
        userdb=users.update({'name':user},
                {'name': user, 'data':store.users[user]},
                upsert=True,
                w=0)
    repos = db.repos
    for repo in store.repos:
        reposdb=repos.update({'url':repo},
                {'url': url, 'data': store.repos[repo]},
                upsert=True,
                w=0)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    update_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# Connect to memcache with config from environment variables.