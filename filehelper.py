import os
import time

# Local imports
import pickle
import config


# Remove underscore and dot from a filename to avoid filename injection attacks
def safe_filename(filename):
    ext = get_extension(filename)
    temp_name = filename[:(-len(ext))]
    return temp_name.replace('/', '_').replace('.', '_') + ext


def get_filename(upload_dir):
    filename = str(int(time.time()))
    return create_filename(upload_dir, filename, '')


def get_extension(filename):
    return filename[filename.rfind('.'):]


# Recursively add underscore until valid path found,
# just in case we have a lot of concurrent uploads
def create_filename(directory, filename, ext=''):
    if not os.path.exists(directory + filename + ext):
        return filename + ext
    else:
        return create_filename(directory, filename + '_', ext)


def save_metadata(filename, params):
    path = config.get_upload_path() + filename + '.metadata'
    if not os.path.exists(path):
        f = open(path, 'w+')
        f.write(pickle.dumps(params))
        f.close()
        return params
    else:
        f = open(path, 'r+')
        data = f.read()
        obj = pickle.loads(data)
        f.close()
        for k, v in params.iteritems():
            obj[k] = v
        f = open(path, 'w')
        f.write(pickle.dumps(obj))
        f.close()
        return obj


def get_metadata(filename):
    path = config.get_upload_path() + filename + '.metadata'
    f = open(path, 'r')
    return pickle.loads(f.read())
    f.close()
