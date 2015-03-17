===========
Flask-Bower
===========

Flask-Bower provides a method to manage and serve `bower <http://bower.io/>`_ installed packages. This simplifies javascript dependency management a lot.

To provide this, there is a flask blueprint to serve content from your ``bower_components`` directory 
and use `url_for` for serving the files same as serving files form static folder. No template changes is required. 

Usage
-----

Flask-Bower is available on PyPi: https://pypi.python.org/pypi/Flask-Bower/ So just add it to your requirements.txt or install using ``pip install flask-bower``

First you have to add it to your app::

  from flask.ext.bower import Bower

  [...]

  Bower(app)

This provides the ``/bower`` url route and a new jinja2 function ``url_for()``

The ``bower_components`` directory has do be inside the app directory (``app/bower_components`` - like your ``static`` and ``templates`` directories)

Install your packages like ``jquery`` with bower: ``bower install -S jquery``

Now it should look like::

  $ ls -1 app/bower_components/jquery
  MIT-LICENSE.txt
  bower.json
  dist
  src


To include and use this, you can use ``url_for()``::

  <script src="{{ url_for('static', filename='dist/jquery.js') }}"></script>


Configuration
-------------

There are several configuration options to customize the behavior:

``BOWER_COMPONENTS_ROOT``
  default: ``bower_components``

  Directory name containing your installed bower packages

``BOWER_QUERYSTRING_REVVING``
  default: ``True``

  Append ?version= parameter to url (useful for cache busting by updates). It tries to detect the version in the following order:

  1. bower.json
  2. package.json (if available)
  3. file modification timestamp

``BOWER_TRY_MINIFIED``
  default: ``True``

  Check if a minified version is available and serve this instead (check if a file with ``<filename>.min.<ext>`` like ``dist/jquery.min.js`` exists)

``BOWER_URL_PREFIX``
  default: ``/bower``

  Customize the url prefix

``BOWER_SUBDOMAIN``
  default: ``None``

  Subdomain to serve the content like ``static`` (see flask blueprint documentation for subdomains)