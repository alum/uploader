Uploader
--------

A small uploader system which does upload progress. Written in python. Works with IE7+.


Dependencies
------------
* Werkzeug 0.8.3
* gunicorn 0.14.6 (HTTP / WSGI server)
* eventlet 0.9.17 (worker class for gunicorn)


How to run
----------
To serve with gunicorn on port 80:
sudo gunicorn uploader:application -b 0.0.0.0:80 -w 4 --timeout 30 -k eventlet --access-logfile access.log --daemon
(Just remove --daemon to get output to stdout.)

It will not work using the 'sync' worker since an upload request may take long time and gunicorn will then kill the synchronous worker.
Don't try to run this behind nginx, it won't work since nginx does request buffering.

It is also possible to run this with the pythin built in WSGI server by running 'python uploader.py'. However, progress will not be reported since the server is single threaded and blocking.