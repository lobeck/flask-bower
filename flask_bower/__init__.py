#!/usr/bin/env python
# coding=utf8
import os
from flask import abort, json, send_file, Blueprint, current_app, url_for
from werkzeug.routing import BuildError


def validate_parameter(param):
    if '..' in param or param.startswith('/'):
        abort(404)


def serve(component, filename):
    validate_parameter(component)
    validate_parameter(filename)

    root = current_app.config['BOWER_COMPONENTS_ROOT']

    return send_file('/'.join([root, component, filename]))


def bower_url_for(component, filename, **values):
    root = current_app.config['BOWER_COMPONENTS_ROOT']
    bower_data = None
    package_data = None

    # check if component exists in bower_components directory
    if not os.path.isdir('/'.join([current_app.root_path, root, component])):
        raise BuildError('/'.join([component, filename]), values, 'GET')

    # load bower.json of specified component
    bower_file_path = '/'.join([current_app.root_path, root, component, 'bower.json'])
    if os.path.exists(bower_file_path):
        with open(bower_file_path, 'r') as bower_file:
            bower_data = json.load(bower_file)

    # check if package.json exists and load package.json data
    package_file_path = '/'.join([current_app.root_path, root, component, 'package.json'])
    if os.path.exists(package_file_path):
        with open(package_file_path, 'r') as package_file:
            package_data = json.load(package_file)

    # check if filename is listed in 'main' of bower.json
    # disabled because it caused some errors with blueimp-gallery
#    if filename not in bower_data['main']:
#        raise BuildError('/'.join([component, filename]), values, 'GET')

    # check if specified file actually exists
    if not os.path.exists('/'.join([current_app.root_path, root, component, filename])):
        raise BuildError('/'.join([component, filename]), values, 'GET')

    # check if minified file exists (by pattern <filename>.min.<ext>
    # returns filename if successful
    if current_app.config['BOWER_TRY_MINIFIED']:
        if '.min.' not in filename:
            minified_filename = '%s.min.%s' % tuple(filename.rsplit('.', 1))
            minified_path = '/'.join([root, component, minified_filename])

            if os.path.exists('/'.join([current_app.root_path, minified_path])):
                filename = minified_filename

    # determine version of component and append as ?version= parameter to allow cache busting
    if current_app.config['BOWER_QUERYSTRING_REVVING']:
        if bower_data is not None and 'version' in bower_data:
            values['version'] = bower_data['version']
        elif package_data is not None and 'version' in package_data:
                values['version'] = package_data['version']
        else:
            values['version'] = os.path.getmtime('/'.join([current_app.root_path, root, component, filename]))

    return url_for('bower.serve', component=component, filename=filename, **values)


class Bower(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('BOWER_COMPONENTS_ROOT', 'bower_components')
        app.config.setdefault('BOWER_QUERYSTRING_REVVING', True)
        app.config.setdefault('BOWER_TRY_MINIFIED', True)
        app.config.setdefault('BOWER_URL_PREFIX', '/bower')
        app.config.setdefault('BOWER_SUBDOMAIN', None)

        blueprint = Blueprint(
            'bower',
            __name__,
            url_prefix=app.config['BOWER_URL_PREFIX'],
            subdomain=app.config['BOWER_SUBDOMAIN'])

        blueprint.add_url_rule('/<component>/<path:filename>', 'serve', serve)

        app.register_blueprint(blueprint)

        app.jinja_env.globals['bower_url_for'] = bower_url_for
