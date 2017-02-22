import argparse
import primed_cache
import json

from flask import Flask, jsonify, make_response, abort

from cache import Cache

from response_filter import response_filter, path_to_parts

app = Flask(__name__)

_cache = Cache()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify("Healthy")


# Accept all URLs. For URLs that are not cached, reach out to github and return
# the response recieved from there.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def get_task(path):
    [key, filter, count] = path_to_parts(path)
    [status_code, value] = _cache.get(key)
    if status_code == 200:
        list_response = response_filter(value, filter, count)
        return jsonify(list_response)
    else:
        abort(status_code)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", help="The port at which the server listens",
                        type=int)

    parser.add_argument("-d", "--redis-host", help="The name of the redis host",
                        type=str)

    parser.add_argument("-e", "--redis-port", help="The port at which redis is listening",
                        type=int)

    args = parser.parse_args()

    _cache = primed_cache.get_primed_cache()

    app.run(debug=False, port=args.port)
