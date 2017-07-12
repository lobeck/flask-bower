===========
Flask-Bower
===========

Flask-Bower provides a method to manage and serve `bower <http://bower.io/>`_ installed packages. This simplifies javascript dependency management a lot.

To provide this, there is a flask blueprint to serve content from your ``bower_components`` directory and use ``url_for()`` for serving the files same as serving files form flask static folder.

Usage
-----

| Flask-Bower is available on PyPi: https://pypi.python.org/pypi/Flask-Bower/
|
| So just add it to your requirements.txt or install using ``pip install flask-bower``
|
| First you have to add it to your app

::

  from flask_bower import Bower

  [...]

  Bower(app)

| This provides the ``/bower`` url route.
|
| Per default, the ``bower_components`` directory has to be inside the app directory (``app/bower_components`` - like your ``static`` and ``templates`` directories). Another directory can be specified using ``BOWER_COMPONENTS_ROOT``
|
| Install your packages like ``jquery`` with bower: ``bower install -S jquery``

Now it should look like::

  $ ls -1 app/bower_components/jquery
  MIT-LICENSE.txt
  bower.json
  dist
  src


To include and use this, you can use ``url_for()``::

  <script src="{{ url_for('bower.static', filename='jquery/dist/jquery.js') }}"></script>


Configuration
-------------

There are several configuration options to customize the behavior:

``BOWER_COMPONENTS_ROOT``
  default: ``bower_components``

  Directory name containing your installed bower packages

``BOWER_KEEP_DEPRECATED``
  default: ``True``

  Keep deprecated functions available

  Note: deprecated functions will be removed in future versions

  affected functions:

  - ``bower_url_for`` - please migrate to ``url_for('bower.static', filename='component/path')``

``BOWER_QUERYSTRING_REVVING``
  default: ``True``

  Append ?version= parameter to url (useful for cache busting by updates). It tries to detect the version in the following order:

  1. bower.json
  2. package.json (if available)
  3. file modification timestamp

``BOWER_REPLACE_URL_FOR``
  default: ``False``

  Replace flasks ``url_for()`` function in templates.

  This is useful - but not recommended - to build an "overlay" for the static folder.

  **Warning:** Replacing ``url_for()`` causes conflicts with other flask extensions like ``flask-cdn``, since only one extension can replace ``url_for()`` at a time and the last registered extension wins.

``BOWER_SUBDOMAIN``
  default: ``None``

  Subdomain to serve the content like ``static`` (see flask blueprint documentation for subdomains)

``BOWER_TRY_MINIFIED``
  default: ``True``

  Check if a minified version is available and serve this instead (check if a file with ``<filename>.min.<ext>`` like ``jquery/dist/jquery.min.js`` exists)

``BOWER_URL_PREFIX``
  default: ``/bower``

  Customize the url prefix


Deprecations
------------

``bower_url_for(component, file)``
==================================

    |  This is now deprecated since it is a break of the development workflow due to the use of a different function than ``url_for()``, which is the default for url handling in flask.
    |
    |  Since v1.1.0 it is possible to use the default ``url_for()`` function also for flask assets::

    ::

        url_for('bower.static', filename='component/path')

    Use of this new approach is recommended to all developers and to simplify the migration the ``bower_url_for()`` function will stay available for a while; though it can be disabled to help migrating (see ``BOWER_KEEP_DEPRECATED``)
