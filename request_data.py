import os
import requests

from linkparser import LinkParser


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
def request_data(endpoint, request):

    next_link = 'https://' + endpoint + request

    token = get_auth_token()

    headers = {'Authorization': token}

    response = []

    while next_link != '':
        r = requests.get(next_link, headers=headers)

        if r.status_code == 200:

            response.append(r.text)

            if 'link' in r.headers:
                link_string = r.headers['link']
                lp = LinkParser(link_string)
                next_link = lp.get_link('next')
            else:
                next_link = ''

        else:
            return [r.status_code, response]

    return [200, response]
