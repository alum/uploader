import session


class StreamWrapper(object):
    '''
    Wraps the underlying stream that HTTP POST data is sent to and updates the
    session with the progress. This makes it possible to update a progress meter
    with how many percent of the data have been recieved from the client.
    '''
    def __init__(self, stream, content_length, sessionid):
        self._stream = stream
        self._progress = 0
        self._read_bytes = 0
        self._content_length = int(content_length)
        self._sessionid = sessionid

    def read(self, bytes):
        rv = self._stream.read(bytes)
        self._update_progress(bytes)
        return rv

    def _update_progress(self, bytes):
        self._read_bytes += bytes
        progress = int(float(self._read_bytes) / float(self._content_length) * 100)
        if progress > self._progress + 0.01:  # Only update progress if there is more than 1 % progress
            self._progress = progress
            params = {'progress': progress,
                    'upload_status': 'uploading',
                    'url': ''}
            session.set(self._sessionid, params)

    def readline(self, size):
        return self._stream.readline(size)
