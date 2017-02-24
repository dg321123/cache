import argparse
import primed_cache
import app_config
import signal

from flask import Flask, jsonify, make_response, abort

from cache import Cache

from response_filter import response_filter, path_to_parts

from process_lock_value_type import ProcessLockValueType

from leader_elector import LeaderElector

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

    app_config.service_port = args.port
    app_config.process_lock_value = ProcessLockValueType(
        app_config.service_fqdn, app_config.service_pid, app_config.service_port)

    print app_config.process_lock_value.__dict__

    app_config.leader_elector = LeaderElector(redis_config=app_config.redis_config,
                                              app_name=app_config.app_name,
                                              process_lock_value=app_config.process_lock_value,
                                              process_lock_ttl=app_config.process_lock_ttl_sec,
                                              retry_interval_ms=app_config.retry_interval_ms)

    app_config.t.start()

    _cache = primed_cache.get_primed_cache()

    signal.signal(signal.SIGINT, app_config.signal_handler)

    app.run(debug=False, port=args.port, ssl_context='adhoc')