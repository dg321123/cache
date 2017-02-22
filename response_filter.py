import json


def vectorize_response(response, n):
    collection = []
    for page in response:
        print page
        list_response = json.loads(page)
        if isinstance(list_response, list):
            collection += list_response
        else:
            collection = list_response

    return collection


def top_response_filter(response, n):
    collection = vectorize_response(response, n)
    return collection[:n]


def bottom_response_filter(response, n):
    collection = vectorize_response(response, n)
    return collection[-1 * n:]


def response_filter(response, filter_type, count):
    if filter_type == 'top':
        filter_method = top_response_filter
    elif filter_type == 'bottom':
        filter_method = bottom_response_filter
    else:
        filter_method = vectorize_response

    return filter_method(response, count)


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