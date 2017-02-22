import argparse

from flask import Flask, jsonify, make_response, abort

from request_data import request_data

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify("Healthy")


# Accept all URLs. For URLs that are not cached, reach out to github and return
# the response recieved from there.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def get_task(path):
    [status_code, response] = request_data("api.github.com/", path)
    if status_code == 200:
        return jsonify(''.join(response))
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

    app.run(debug=True, port=args.port)
