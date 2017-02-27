import app_config
import os
import requests
import sys

from datetime import datetime
from linkparser import LinkParser
from log import logger


def get_auth_token():

    if 'GITHUB_API_TOKEN' not in os.environ:
        raise EnvironmentError('Environment variable GITHUB_API_TOKEN not defined')

    return 'token ' + os.environ['GITHUB_API_TOKEN']


# This method os to request data from an endpoint for it's request.
# GitHub paginates it's responses. This method expects all endpoints
# to paginate the responses in the same way i.e. using the following in
# '<https://api.github.com/organizations/913567/repos?page=3>; rel="next", <https://api.github.com/organizations/913567/repos?page=5>; rel="last", <https://api.github.com/organizations/913567/repos?page=1>; rel="first", <https://api.github.com/organizations/913567/repos?page=1>; rel="prev"'
# the response header.
#
# This method tries to request all pages iteratively and flatten the response.
# TODO Potential improvements:
#   1. Add retry in case one of the many requests fails.
#   2. Since some responses can be very large, sending requests for many pages
#      at once (after finding the number of pages from the first response) will
#      speed things up significantly.
def request_data(endpoint, request, timeout):

    next_link = 'https://' + endpoint + request

    token = get_auth_token()

    headers = {'Authorization': token}

    response = []

    while next_link != '':

        try:
            r = requests.get(next_link, headers=headers, verify=False, timeout=(3, timeout))
        except requests.exceptions.Timeout as e:
            logger.warn('Request %s timed out after %d', next_link, timeout)
            return [598, response]
        except requests.exceptions.ConnectionError as e:
            logger.error('Caught %s', e.message)
            app_config.request_connection_failure = True
            raise

        app_config.request_connection_failure = False

        if r.status_code == 200:

            response.append(r.text)

            if 'link' in r.headers:
                link_string = r.headers['link']
                lp = LinkParser(link_string)
                next_link = lp.get_link('next')
            else:
                next_link = ''

        else:
            logger.warn('Failed request with status code %d', r.status_code)
            return [r.status_code, response]

    return [200, response]


def get_fresh_copy(key):
    leader_value = app_config.leader_elector.get_leader()

    if leader_value.__dict__ == app_config.process_lock_value.__dict__:
        source = app_config.golden_source
        timeout = app_config.leader_timeout
    else:
        source = leader_value.fqdn + ':' + str(leader_value.port)
        timeout = app_config.slave_timeout

    logger.debug('Source endpoint is %s, timeout is %d', source, timeout)

    return request_data(source, key, timeout)
