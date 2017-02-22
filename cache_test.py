from cache import Cache, Observer, Attributes
from time import sleep
import json


def get_index(pages, key):
    collection = []
    for page in pages:
        repo_list = json.loads(page)
        for repo in repo_list:
            collection.append([repo['full_name'], repo[key]])

    collection.sort(key=lambda x: x[1], reverse=True)
    return collection


def get_index_forks(pages):
    return get_index(pages, 'forks_count')


def get_index_last_updated(pages):
    return get_index(pages, 'updated_at')


def get_index_open_issues(pages):
    return get_index(pages, 'open_issues_count')

def get_index_stars(pages):
    return get_index(pages, 'stargazers_count')

def get_index_watchers(pages):
    return get_index(pages, 'watchers_count')


fork_observer = Observer('/view/top/N/forks', get_index_forks)
last_updated_observer = Observer('/view/top/N/last_updated', get_index_last_updated)
open_issues_observer = Observer('/view/top/N/open_issues', get_index_open_issues)
stars_observer = Observer('/view/top/N/stars', get_index_stars)
watchers_observer = Observer('/view/top/N/watchers', get_index_watchers)

default_val = ''
default_attributes = Attributes()
cache = Cache()

# Priming
print 'priming cache'
cache.put('/', default_val, -10)
cache.put('/orgs/Netflix', default_val, -10)
cache.put('/orgs/Netflix/repos', default_val, -10)
cache.put('/orgs/Netflix/members', default_val, -10)

cache.put('/view/top/N/forks', default_val, -10)
cache.add_observer('/orgs/Netflix/repos', fork_observer)

cache.put('/view/top/N/last_updated', default_val, -10)
cache.add_observer('/orgs/Netflix/repos', last_updated_observer)

cache.put('/view/top/N/open_issues', default_val, -10)
cache.add_observer('/orgs/Netflix/repos', open_issues_observer)

cache.put('/view/top/N/stars', default_val, -10)
cache.add_observer('/orgs/Netflix/repos', stars_observer)

cache.put('/view/top/N/watchers', default_val, -10)
cache.add_observer('/orgs/Netflix/repos', watchers_observer)

[status_code, value] = cache.get('/')
[status_code, value] = cache.get('/orgs/Netflix/repos')
[status_code, forks] = cache.get('/view/top/N/forks')
[status_code, last_updated] = cache.get('/view/top/N/last_updated')
[status_code, open_issues] = cache.get('/view/top/N/open_issues')
[status_code, stars] = cache.get('/view/top/N/stars')
[status_code, watchers] = cache.get('/view/top/N/watchers')

print forks
print last_updated
print open_issues
print stars
print watchers


[status_code, value] = cache.get('/')
[status_code, value] = cache.get('/orgs/Netflix/repos')
[status_code, forks] = cache.get('/view/top/N/forks')
[status_code, last_updated] = cache.get('/view/top/N/last_updated')
[status_code, open_issues] = cache.get('/view/top/N/open_issues')
[status_code, stars] = cache.get('/view/top/N/stars')
[status_code, watchers] = cache.get('/view/top/N/watchers')

sleep (2)

[status_code, value] = cache.get('/')
[status_code, value] = cache.get('/orgs/Netflix/repos')
[status_code, forks] = cache.get('/view/top/N/forks')
[status_code, last_updated] = cache.get('/view/top/N/last_updated')
[status_code, open_issues] = cache.get('/view/top/N/open_issues')
[status_code, stars] = cache.get('/view/top/N/stars')
[status_code, watchers] = cache.get('/view/top/N/watchers')

sleep(1)

[status_code, value] = cache.get('/')
[status_code, value] = cache.get('/orgs/Netflix/repos')
[status_code, forks] = cache.get('/view/top/N/forks')
[status_code, last_updated] = cache.get('/view/top/N/last_updated')
[status_code, open_issues] = cache.get('/view/top/N/open_issues')
[status_code, stars] = cache.get('/view/top/N/stars')
[status_code, watchers] = cache.get('/view/top/N/watchers')
