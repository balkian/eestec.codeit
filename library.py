import requests
import json
from secrets import *
from collections import Counter

API_URL = 'https://api.github.com/'

def get_url(url,relative=True):
    if relative:
        url=API_URL+url
    r = requests.get(url, params={"client_id":CLIENT_ID, "client_secret":CLIENT_SECRET})
    if(r.ok):
        print r.headers 
        print 'Rate remaining: %s' % r.headers['x-ratelimit-remaining']
        data= r.text or r.content
        if len(data) == 0:
            return None
        else:
            return json.loads(data)
def get_org(org):
    return get_url('orgs/%s'%org)

def get_user(user):
    return get_url('users/%s'%user)

def get_members(org):
    return get_url('orgs/%s/members'%org)

class Store(dict):
    def __init__(self):
        self[u'repos']={}
        self[u'users']={}
        self[u'orgs']={}

    @property
    def orgs(self):
        return self[u'orgs']

    @property
    def users(self):
        return self[u'users']

    @property
    def repos(self):
        return self[u'repos']

    def add_org(self,org):
        self[u'orgs'][org.name]=org

    def add_repo(self,repo):
        self[u'repos'][repo[u'url']]=repo

    def add_user(self,user):
        self[u'users'][user[u'login']]=user

    def load_all(self,file='lcs.json'):
        lcs=json.load(open(file))
        self[u'lcs']=lcs
        for lcrepo in lcs.keys():
            repo=Org(lcrepo,store=self)
            self.add_org(repo)
        for org in self.orgs.values():
            print "ORG: %s:" % org
            org.reload_repos()
            org.reload_members()
        for user in self.users.values():
            print "USER: %s" %user
            user.reload_repos()

    def get_stats(self):
        statistics={}
        usedlanguages={}
        linesperlanguage={}
        for repo in self.repos.values():
            language=repo[u'language']
            url=repo[u'url']
            if language in usedlanguages:
                usedlanguages[language].append([url])
            else:
                usedlanguages[language]=list([url])
            languages=repo[u'languages']
            for language,lines in languages.iteritems():
                if language in linesperlanguage:
                    linesperlanguage[language]+=lines
                else:
                    linesperlanguage[language]=lines
        lcrepos=0
        statistics[u'usedlanguages']=usedlanguages
        statistics[u'linesperlanguage']=linesperlanguage
        for lc in self[u'lcs']:
            lcrepos+=len(self.orgs[lc][u'repos'])
        statistics["lc-repos"]=lcrepos
        statistics["total-repos"]=len(self.repos)
        statistics["total-users"]=len(self.users)
        totalfollowers=0
        totalfollowing=0
        totalstarred=0
        for user in self.users.values():
            totalfollowing+=len(user.following)
            totalfollowers+=len(user.followers)
            totalstarred+=len(user.starred)
            user.repos
        totalwatching=0
        totalforks=0
        for repo in self.repos.values():
            totalwatching+=repo[u'watchers_count']
            totalforks+=repo[u'forks_count']
        statistics['total-followers']=totalfollowers
        statistics['total-following']=totalfollowing
        statistics['total-starred']=totalstarred
        statistics['total-watching']=totalwatching
        statistics['total-forks']=totalforks
        self[u'statistics']=statistics
        print self[u'orgs']
        print self[u'statistics'][u'linesperlanguage']

class BasicItem(dict):
    def __init__(self,name,dic=None,method=get_url,name_key=u'url',store=None):
        self.store=store
        asdict=dic
        if name and not dic:
            asdict=method(name)
        if dic:
            asdict=dic
        for key in asdict.keys():
            self[key]=asdict[key]
        if name: 
            self.name=name
        elif dic:
            self.name=self[name_key]

class Repo(BasicItem):
    def __init__(self,dic,store=None):
        super(Repo,self).__init__(name,dic,method=get_repo,name_key=u'url',store=store)

class BasicLogin(BasicItem):
    def __init__(self,name,dic=None,method=get_url,store=None):
        super(BasicLogin,self).__init__(name,dic,method=method,name_key=u'login',store=store)

    def reload_repos(self):
        repos=get_url(self[u'repos_url'],relative=False)
        for repo in repos:
            repo['languages']=get_url(repo[u'languages_url'],relative=False)
        self.repos=repos
    
    @property
    def repos(self):
        if not u'repos' in self:
            self.reload_repos()
        if self.store is not None:
            return [store['repos'][name] for name in self[u'repos']]
        return self[u'repos']

    @repos.setter
    def repos(self,dic):
        repos=dic
        if self.store is not None:
            self[u'repos']=[]
            for repo in repos:
                url=repo[u'url']
                store.add_repo(repo)
                self[u'repos'].append(url)

        else:
            self[u'repos']=repos
            return self[u'repos']

    def from_dict(dic,store=None):
        name=dic[u'login']
        newUser = User(None,dic,store)
        return newUser

class User(BasicLogin):
    def __init__(self,name,dic=None,store=None,getAll=True):
        super(User,self).__init__(name,dic,method=get_user,store=store)
        if(getAll):
            self.reload_all()
            
    def reload_all(self):
        self.reload_starred()
        self.reload_followers()
        self.reload_following()

    def reload_starred(self):
        starred=get_url('users/%s/starred'%self.name)
        self[u'starred']=[repo[u'url'] for repo in starred]

    def reload_followers(self):
        followers=get_url(self['followers_url'],relative=False)
        self[u'followers']=[user[u'login'] for user in followers]

    def reload_following(self):
            following=get_url(self['following_url'],relative=False)
            self[u'following']=[user[u'login'] for user in following]

    @property
    def starred(self):
        if not u'starred' in self:
            self.reload_starred()
        else:
            return self[u'starred']

    @property
    def following(self):
        if not u'following' in self:
            self.reload_following()
        else:
            return self[u'following']

    @property
    def followers(self):
        if not u'followers' in self:
            self.reload_followers()
        else:
            return self[u'followers']


class Org(BasicLogin):
    def __init__(self,name,dic=None,store=None):
        super(Org,self).__init__(name,dic,method=get_org,store=store)

    def deep_load_members(self):
        for member in self.members:
            member.reload_repos() 

    @property
    def members(self):
        if not u'members' in self:
            self.reload_members()
        if self.store is not None:
            return [store[u'users'][name] for name in self[u'members']]
        else:
            return self[u'members']
        
    def reload_members(self):
        dic=get_members(self.name)
        arr=[]
        for member in dic:
            arr.append(User(None,member,store=self.store))
        if self.store is not None:
            self[u'members']=[member.name for member in arr]
            for member in arr:
                self.store.add_user(member)
        else:
            self[u'members']=arr

