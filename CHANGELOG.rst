Changes
-------

:2.0.0:

- drop python 2.6 support / six dependency
- switch build infrastructure to pytest and GitHub Actions
- switch to `.bower.json` as per recommendation - thanks `@ivelin`_
- Fix ModuleNotFoundError - thanks `@jeffhung`_

.. _@ivelin: https://github.com/lobeck/flask-bower/pull/9
.. _@jeffhung: https://github.com/lobeck/flask-bower/pull/10

:1.3.0:

- Support absolute paths in BOWER_COMPONENT_ROOT - thanks `@jesseops`_

.. _@jesseops: https://github.com/lobeck/flask-bower/pull/6

:1.2.1:

- remove BuildError handling since flask is already taking care (glitch in the flask documentation)

:1.2.0:

- add conditional switch on ``send_file`` to ensure 304 responses

:1.1.0:

- flasks default ``url_for`` is now supported for bower assets - requires Flask >= 0.9
- added ``BOWER_KEEP_DEPRECATED`` option
- added ``BOWER_REPLACE_URL_FOR`` option
- ``bower_url_for`` is now deprecated

:1.0.3: (not released)

- ``bower.json`` is now optional since it may be not available  if files are pulled from a random source which is not supporting bower

:1.0.2:

- updated documentation

:1.0.1:

- initial release
