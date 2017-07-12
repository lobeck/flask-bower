#!/usr/bin/env python
# coding=utf8
import os
from flask import abort, json, send_file, Blueprint, current_app, url_for
import sys

from flask._compat import reraise


def validate_parameter(param):
    if '..' in param or param.startswith('/'):
        abort(404)


def serve(component, filename):
    validate_parameter(component)
    validate_parameter(filename)

    root = current_app.config['BOWER_COMPONENTS_ROOT']

    return send_file(os.path.join(root, component, filename), conditional=True)


def bower_url_for(component, filename, **values):
    """
    DEPRECATED
    This function provides backward compatibility - please migrate to the approach using "bower.static"

    :param component: bower component (package)
    :type component: str
    :param filename: filename in bower component - can contain directories (like dist/jquery.js)
    :type filename: str
    :param values: additional url parameters
    :type values: dict[str, str]
    :return: url
    :rtype: str
    """
    return build_url(component, filename, **values)


def replaced_url_for(endpoint, filename=None, **values):
    """
    This function acts as "replacement" for the default url_for() and intercepts if it is a request for bower assets

    If the file is not available in bower, the result is passed to flasks url_for().
    This is useful - but not recommended - for "overlaying" the static directory (see README.rst).
    """
    lookup_result = overlay_url_for(endpoint, filename, **values)

    if lookup_result is not None:
        return lookup_result

    return url_for(endpoint, filename=filename, **values)


def handle_url_error(error, endpoint, values):
    """
    Intercept BuildErrors of url_for() using flasks build_error_handler API
    """
    url = overlay_url_for(endpoint, **values)
    if url is None:
        exc_type, exc_value, tb = sys.exc_info()
        if exc_value is error:
            reraise(exc_type, exc_value, tb)
        else:
            raise error
    # url_for will use this result, instead of raising BuildError.
    return url


def overlay_url_for(endpoint, filename=None, **values):
    """
    Replace flasks url_for() function to allow usage without template changes

    If the requested endpoint is static or ending in .static, it tries to serve a bower asset, otherwise it will pass
    the arguments to flask.url_for()

    See http://flask.pocoo.org/docs/0.10/api/#flask.url_for
    """
    default_url_for_args = values.copy()
    if filename:
        default_url_for_args['filename'] = filename

    if endpoint == 'static' or endpoint.endswith('.static'):

        if os.path.sep in filename:
            filename_parts = filename.split(os.path.sep)
            component = filename_parts[0]
            # Using * magic here to expand list
            filename = os.path.join(*filename_parts[1:])

            returned_url = build_url(component, filename, **values)

            if returned_url is not None:
                return returned_url

    return None


def build_url(component, filename, **values):
    """
    search bower asset and build url

    :param component: bower component (package)
    :type component: str
    :param filename: filename in bower component - can contain directories (like dist/jquery.js)
    :type filename: str
    :param values: additional url parameters
    :type values: dict[str, str]
    :return: url
    :rtype: str | None
    """
    root = current_app.config['BOWER_COMPONENTS_ROOT']
    bower_data = None
    package_data = None

    # check if component exists in bower_components directory
    if not os.path.isdir(os.path.join(current_app.root_path, root, component)):
        # FallBack to default url_for flask
        return None

    # load bower.json of specified component
    bower_file_path = os.path.join(current_app.root_path, root, component, 'bower.json')
    if os.path.exists(bower_file_path):
        with open(bower_file_path, 'r') as bower_file:
            bower_data = json.load(bower_file)

    # check if package.json exists and load package.json data
    package_file_path = os.path.join(current_app.root_path, root, component, 'package.json')
    if os.path.exists(package_file_path):
        with open(package_file_path, 'r') as package_file:
            package_data = json.load(package_file)

    # check if specified file actually exists
    if not os.path.exists(os.path.join(current_app.root_path, root, component, filename)):
        return None

    # check if minified file exists (by pattern <filename>.min.<ext>
    # returns filename if successful
    if current_app.config['BOWER_TRY_MINIFIED']:
        if '.min.' not in filename:
            minified_filename = '%s.min.%s' % tuple(filename.rsplit('.', 1))
            minified_path = os.path.join(root, component, minified_filename)

            if os.path.exists(os.path.join(current_app.root_path, minified_path)):
                filename = minified_filename

    # determine version of component and append as ?version= parameter to allow cache busting
    if current_app.config['BOWER_QUERYSTRING_REVVING']:
        if bower_data is not None and 'version' in bower_data:
            values['version'] = bower_data['version']
        elif package_data is not None and 'version' in package_data:
            values['version'] = package_data['version']
        else:
            values['version'] = os.path.getmtime(os.path.join(current_app.root_path, root, component, filename))

    return url_for('bower.serve', component=component, filename=filename, **values)


class Bower(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('BOWER_COMPONENTS_ROOT', 'bower_components')
        app.config.setdefault('BOWER_KEEP_DEPRECATED', True)
        app.config.setdefault('BOWER_QUERYSTRING_REVVING', True)
        app.config.setdefault('BOWER_REPLACE_URL_FOR', False)
        app.config.setdefault('BOWER_SUBDOMAIN', None)
        app.config.setdefault('BOWER_TRY_MINIFIED', True)
        app.config.setdefault('BOWER_URL_PREFIX', '/bower')

        blueprint = Blueprint(
            'bower',
            __name__,
            url_prefix=app.config['BOWER_URL_PREFIX'],
            subdomain=app.config['BOWER_SUBDOMAIN'])

        blueprint.add_url_rule('/<component>/<path:filename>', 'serve', serve)

        app.register_blueprint(blueprint)

        if app.config['BOWER_KEEP_DEPRECATED'] is True:
            app.jinja_env.globals['bower_url_for'] = bower_url_for

        if app.config['BOWER_REPLACE_URL_FOR'] is True:
            app.jinja_env.globals['url_for'] = replaced_url_for

        app.url_build_error_handlers.append(handle_url_error)
