import argparse
import app_config
import primed_cache
import redis
import requests
import signal

from cache import Cache
from datetime import datetime, timedelta
from flask import Flask, jsonify, make_response, abort
from leader_elector import LeaderElector
from log import logger
from process_lock_value_type import ProcessLockValueType
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
    now = datetime.now()

    if now - app_config.time_of_last_leader_sync > timedelta(seconds=app_config.process_lock_ttl_sec) \
            or app_config.request_connection_failure:
        return abort(404)

    return jsonify("Healthy")


# Accept all URLs. For URLs that are not cached, reach out to github and return
# the response received from there.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def get_task(path):
    [key, filter_type, count] = path_to_parts(path)
    [status_code, value] = _cache.get(key)
    if status_code == 200:
        list_response = response_filter(value, filter_type, count)
        return jsonify(list_response)
    else:
        logger.debug('Failed request. status code %d', status_code)
        abort(status_code)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-p", "--port", help="The port at which the server listens",
                        type=int)

    args = parser.parse_args()

    app_config.service_port = args.port
    app_config.process_lock_value = ProcessLockValueType(
        app_config.service_fqdn, app_config.service_pid, app_config.service_port)

    logger.debug("process_log_value = %s", app_config.process_lock_value.__dict__)

    # Lets register SIGINT before we start the leader election thread.
    signal.signal(signal.SIGINT, app_config.signal_handler)

    app_config.leader_elector = LeaderElector(redis_config=app_config.redis_config,
                                              app_name=app_config.app_name,
                                              process_lock_value=app_config.process_lock_value,
                                              process_lock_ttl=app_config.process_lock_ttl_sec,
                                              retry_interval_ms=app_config.retry_interval_ms)

    app_config.t.start()

    # Don't startup if unable to prime the cache entries. Ideally we should have a 
    # process nanny to detect this failure and retry starting up the process. We 
    # could introduce that logic in this package, but the nanny can be useful for 
    # other processes too and also keeping it separate helps with separation of 
    # concerns. 
    try:
        logger.debug('Priming cache')
        _cache = primed_cache.get_primed_cache()
        retry = False
    except (requests.exceptions.ConnectionError, redis.exceptions.ConnectionError) as e:
        logger.error(e)
        app_config.terminate_leader_elector_hb = True
        app_config.t.join(None)
        exit(1)

    app.run(debug=False, port=args.port, ssl_context='adhoc')
