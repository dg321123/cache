import json

from process_lock_value_type import ProcessLockValueType
from redis_config_type import RedisConfigType


# This method unmarshals the json into an object based on the 'type' specified in the json.
def decode_json_dump(val):
    obj = json.loads(val)
    if 'type' in obj:
        if obj['type'] == 'ProcessLockValueType':
            return ProcessLockValueType(obj['fqdn'], obj['pid'], obj['port'])
        elif obj['type'] == 'RedisConfig':
            return RedisConfigType(obj['hostname'], obj['port'], obj['db'])
    return obj
