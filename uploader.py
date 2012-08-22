'''
SuperUpload

This file includes all controller logic
as well as WSGI application entry point.
'''


# Standard library imports
import os
import json

# Library imports
from werkzeug.wrappers import Request, Response, Headers
from werkzeug.wsgi import wrap_file

# Local imports
import router
import session
import filehelper
from wrappers import StreamWrapper
import config


# Main entry point for the WSGI application
@Request.application
def application(request):
    return router.route(request)


def index(request):
    f = open('index.html', 'r')
    output = f.read()
    f.close()
    return Response(output, content_type="text/html")


# Creates a session and sends the ID to the client as JSON
def session_create(request):
    sessionid = session.create()
    return Response(json.dumps({'status': 'success',
                                'sessionid': sessionid}))


# File upload handler
def upload(request):
    if request.method != 'POST':
        return not_found()
    if 'sessionid' not in request.args:
        return Response('You must submit a sessionid for your upload.')
    sessionid = request.args['sessionid']

    filename = filehelper.get_filename(config.get_upload_path())
    session.set(sessionid, {'progress': 0,
                            'upload_status': 'uploading',
                            'url': '',
                            'filename': filename})
    request.environ['wsgi.input'] = StreamWrapper(request.environ['wsgi.input'],
                                                  request.environ['CONTENT_LENGTH'],
                                                  sessionid)
    # Save the file locally
    f = request.files['file']
    path = config.get_upload_path() + filename
    f.save(path)
    f.close()

    filehelper.save_metadata(filename, {'title': f.filename, 'description': ''})
    session.set(sessionid, {'progress': 100,
                             'upload_status': 'complete',
                             'url': request.host_url + 'file/' + filename,
                             'filename': filename})
    return Response('<!DOCTYPE html><html><head></head><body>\
                     <p>Upload OK</p></body>')


# Sends file upload progress to the client as JSON
def progress(request):
    if 'sessionid' not in request.args:
        return Response(json.dumps({'status': 'error',
                                    'message': 'Sessionid missing.'}))
    obj = session.get(request.args['sessionid'])
    if obj is None:
        return Response(json.dumps({'status': 'error',
                                    'message': 'No such session.'}))
    obj['status'] = 'success'
    return Response(json.dumps(obj))


def save_description(request):
    if request.method != 'POST':
        return not_found()
    if 'sessionid' not in request.form or 'description' not in request.form:
        return Response(json.dumps({'status': 'error',
                                    'message': 'Could not save description. Required parameters missing.'}))

    description = request.form['description']
    obj = session.get(request.form['sessionid'])
    if obj is None or 'filename' not in obj:
        return Response(json.dumps({'status': 'error',
                                    'message': 'Could not save metadata file.'}))

    filename = obj['filename']
    metadata = filehelper.save_metadata(filename,
                                       {'description': description})
    try:
        title = metadata['title']
        url = obj['url']
    except KeyError:
        title = '(upload in progress...)'
        url = ''
    return Response(json.dumps({'status': 'success',
                               'title': title,
                               'description': description,
                               'url': url}))
    return Response(json.dumps({'status': 'success',
                               'title': title,
                               'description': description,
                               'url': obj['url']}))


# Sends an uploaded file to the client
def get_file(request, filename):
    filename = filehelper.safe_filename(filename)
    try:
        f = open(config.get_upload_path() + filename, 'r')
    except IOError:
        return not_found(request)

    file_iterator = wrap_file(request.environ, f)
    try:
        metadata = filehelper.get_metadata(filename)
        title = metadata['title']
    except:
        title = filename
    headers = Headers()
    headers.add('Content-Type', 'application/octet-stream')
    headers.add('Content-Disposition', 'attachment', filename=title)
    headers.add('Content-Length', os.fstat(f.fileno()).st_size)
    return Response(response=file_iterator, headers=headers)


# 404!
def not_found(request):
    return Response('Could not find the path ' + request.path, status=404)


# Routes are defined here
def config_routes():
    router.add_route('/', index)
    router.add_route('/session/create', session_create)
    router.add_route('/upload', upload)
    router.add_route('/progress', progress)
    router.add_route('/savedescription', save_description)
    router.add_route('/file/*', get_file)
    router.add_route('404', not_found)

config_routes()


# Only for starting the development server (will block on file upload!)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', port, application, use_reloader=True)
