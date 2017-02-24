import json


# This assumes that only list responses are split across pages. I don't like it, but
# it gets me started quickly, punting the question about handling response formats to
# the future.
def coalesce_response(response, n):
    collection = []
    for page in response:
        list_response = json.loads(page)
        if isinstance(list_response, list):
            collection += list_response
        else:
            collection = list_response

    return collection


# Method to return the top 'n' responses
def top_response_filter(response, n):
    collection = coalesce_response(response, n)
    return collection[:n]


# Method to return the bottom 'n' responses
def bottom_response_filter(response, n):
    collection = coalesce_response(response, n)
    return collection[-1 * n:]


# This method can be extended to incorporate other filter types, say average or sum of top n elements.
def response_filter(response, filter_type, count):
    if filter_type == 'top':
        filter_method = top_response_filter
    elif filter_type == 'bottom':
        filter_method = bottom_response_filter
    else:
        filter_method = coalesce_response

    return filter_method(response, count)


# Split the path into 3 parts -
#   1. key = key into the cache
#   2. filter_type = kind of filter to apply on the response from the cache
#   3. count = limit the number of response elements
# In the future, you can add other filters such as mean, median, etc.
def path_to_parts(path):
    parts = path.split('/')
    key = ''
    filter_type = ''
    count = 0
    for part in parts:
        if part == 'top' or part == 'bottom':
            filter_type = part
        elif part.isdigit():
            count = int(part)
        else:
            key += '/' + part

    return [key, filter_type, count]