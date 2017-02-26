from cache import Cache, Observer
import json


# get_index method is the registered callback method to refresh the views.
# You may create other such callback refresher methods if you want to cache
# other information.
def get_index(pages, key):
    collection = []
    for page in pages:
        repo_list = json.loads(page)
        for repo in repo_list:
            collection.append([repo['full_name'], repo[key]])

    collection.sort(key=lambda x: x[1], reverse=True)

    return [json.dumps(collection)]


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


fork_observer = Observer('/view/forks', get_index_forks)
last_updated_observer = Observer('/view/last_updated', get_index_last_updated)
open_issues_observer = Observer('/view/open_issues', get_index_open_issues)
stars_observer = Observer('/view/stars', get_index_stars)
watchers_observer = Observer('/view/watchers', get_index_watchers)


def get_primed_cache():
    default_val = ''
    cache = Cache()

    # Registering cache keys
    cache.put('/', default_val, -10)
    cache.put('/orgs/Netflix', default_val, -10)
    cache.put('/orgs/Netflix/repos', default_val, -10)
    cache.put('/orgs/Netflix/members', default_val, -10)

    cache.put('/view/forks', default_val, -10)
    cache.add_observer('/orgs/Netflix/repos', fork_observer)

    cache.put('/view/last_updated', default_val, -10)
    cache.add_observer('/orgs/Netflix/repos', last_updated_observer)

    cache.put('/view/open_issues', default_val, -10)
    cache.add_observer('/orgs/Netflix/repos', open_issues_observer)

    cache.put('/view/stars', default_val, -10)
    cache.add_observer('/orgs/Netflix/repos', stars_observer)

    cache.put('/view/watchers', default_val, -10)
    cache.add_observer('/orgs/Netflix/repos', watchers_observer)

    # Priming the cache by requesting data
    [status_code, value] = cache.get('/')
    [status_code, value] = cache.get('/orgs/Netflix')
    [status_code, value] = cache.get('/orgs/Netflix/repos')
    [status_code, value] = cache.get('/orgs/Netflix/members')
    [status_code, forks] = cache.get('/view/forks')
    [status_code, last_updated] = cache.get('/view/last_updated')
    [status_code, open_issues] = cache.get('/view/open_issues')
    [status_code, stars] = cache.get('/view/stars')
    [status_code, watchers] = cache.get('/view/watchers')

    return cache
