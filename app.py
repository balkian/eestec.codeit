from flask import Flask, Response, url_for, redirect
import os
from urlparse import urlsplit
from pymongo import Connection
import library
import json
from datetime import datetime
import ast

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
app.debug = True

@app.route('/')
def hello():
    return redirect(url_for('static', filename='prueba.html'))

@app.route('/stats')
def stats():
    stats = dict(db.stats.find_one(fields={'_id':False}))
    return Response(json.dumps(stats,skipkeys=True),mimetype='application/json')

@app.route('/orgs')
def orgs():
    orglist = db.orgs.find(fields={'_id':False})
    orgs={}
    for org in orglist:
        orgs[org[u'login']]=org
    print orgs
    return Response(json.dumps(orgs,skipkeys=True),mimetype='application/json')

@app.route('/users')
def users():
    userlist = db.users.find(fields={'_id':False})
    users={}
    for user in userlist:
        users[user[u'login']]=user
    return Response(json.dumps(users,skipkeys=True),mimetype='application/json')

@app.route('/repos')
def repos():
    repolist = db.repos.find(fields={'_id':False})
    repos={}
    for repo in repolist:
        repos[repo[u'url']]=repo
    return Response(json.dumps(repos,skipkeys=True),mimetype='application/json')

def update_db():
    store.load_all(file='lcs.json')
    stats=store.get_stats()
    db.logs.insert({'time':str(datetime.now())})
    db.stats.insert(stats)
    orgs = db.orgs
    db.orgs.ensure_index('name',30)
    for org in store.orgs:
        orgdb=orgs.update({'login':org},
                store.orgs[org],
                upsert=True,
                w=0)
    users = db.users
    for user in store.users:
        print "User:%s"%user
        print ">%s"%store.users[user]
        userdb=users.update({'login':user},
                store.users[user],
                upsert=True,
                w=0)
    repos = db.repos
    for repo in store.repos:
        reposdb=repos.update({'url':repo},
                store.repos[repo],
                upsert=True,
                w=0)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# Connect to memcache with config from environment variables.
