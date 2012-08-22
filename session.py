'''
A singleton type session manager that sets and gets session variables to/from
disk. We could also use a database or other type of shared data store (like
memcached/riak/etc.) for saving and sharing sessions between app workers.
'''
import os
import pickle

# Local imports
import filehelper
import config
from datetime import datetime


# Create a unique session filename. We could hash it for brevity/security
# but there is no need that in this for this application.
def create():
    sessionid = datetime.now().strftime('%Y%m%d%H%m%s%f')
    return filehelper.create_filename(config.get_sessions_path(), sessionid)


def get(id):
    try:
        f = open(get_path(id), 'r')
        data = f.read()
        f.close()
        return pickle.loads(data)  # Unserialize session data from disk
    except:
        return None


def set(id, params):
    path = get_path(id)
    if not os.path.exists(path):
        f = open(path, 'w+')
        f.write(pickle.dumps(params))
        f.close()
        return params
    else:
        f = open(path, 'r')
        data = f.read()
        obj = pickle.loads(data)
        f.close()
        for k, v in params.iteritems():
            obj[k] = v
        f = open(path, 'w')
        f.write(pickle.dumps(obj))
        f.close()
        return obj


def destroy(id):
    os.remove(get_path(id))


def get_path(id):
    return config.get_sessions_path() + str(id)
