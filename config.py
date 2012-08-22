import os

def get_upload_path():
    UPLOAD_PATH = os.getcwd() + '/uploads/'
    if not os.path.exists(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    return UPLOAD_PATH

def get_sessions_path():
    SESSIONS_PATH = os.getcwd() + '/sessions/'
    if not os.path.exists(SESSIONS_PATH):
        os.mkdir(SESSIONS_PATH)
    return SESSIONS_PATH