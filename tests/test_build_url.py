import os
import shutil
import unittest
from flask import Flask, url_for
from werkzeug.routing import BuildError
from flask_bower import Bower, bower_url_for


def additional_build_error_handler(error, endpoint, values):
    return True


class BowerTestCase(unittest.TestCase):

    def clean_alt_dir(self):
        alt_dir = os.path.abspath(os.path.join(os.path.curdir, 'tests', 'bower_components_alt'))
        if os.path.isdir(alt_dir):
            shutil.rmtree(alt_dir)

    def setUp(self):
        self.clean_alt_dir()
        self.app = Flask(__name__)
        self.app.config['SERVER_NAME'] = 'unit.test'

    def tearDown(self):
        self.clean_alt_dir()

    def test_bower_url_for(self):
        """
        Test of the bower_url_for function
        """
        Bower(self.app)
        with self.app.app_context():
            self.assertEqual(bower_url_for('jquery', 'dist/jquery.js'),
                             "http://unit.test/bower/jquery/dist/jquery.min.js?version=2.1.3")

    def test_bower_url_for_no_revving(self):
        """
        Test the BOWER_QUERYSTRING_REVVING parameter
        """
        self.app.config['BOWER_QUERYSTRING_REVVING'] = False
        Bower(self.app)
        with self.app.app_context():
            self.assertEqual(bower_url_for('jquery', 'dist/jquery.js'),
                             "http://unit.test/bower/jquery/dist/jquery.min.js")

    def test_bower_subdomain(self):
        """
        Test the flask blueprint subdomain configuration
        """
        self.app.config['BOWER_SUBDOMAIN'] = 'static'
        Bower(self.app)
        with self.app.app_context():
            self.assertEqual(bower_url_for('jquery', 'dist/jquery.js'),
                             "http://static.unit.test/bower/jquery/dist/jquery.min.js?version=2.1.3")

    def test_url_error_handler(self):
        """
        Test the flask build_error_handler functionality
        """
        Bower(self.app)
        with self.app.app_context():
            self.assertEqual(url_for('bower.static', filename='jquery/dist/jquery.js'),
                             "http://unit.test/bower/jquery/dist/jquery.min.js?version=2.1.3")

    def test_component_not_found(self):
        """
        Test when a component is not found
        """
        Bower(self.app)
        with self.app.app_context():
            with self.assertRaises(BuildError):
                url_for('bower.static', filename='not_found/not_found.js')

    def test_file_not_found(self):
        """
        Test when a component exists but the file is not found in the component
        """
        Bower(self.app)
        with self.app.app_context():
            with self.assertRaises(BuildError):
                url_for('bower.static', filename='jquery/not_found.js')

    def test_build_error_handler_chain(self):
        """
        Append an additional build_error_handler to validate that adjacent handlers will be called as well

        """
        Bower(self.app)
        self.app.url_build_error_handlers.append(additional_build_error_handler)
        with self.app.app_context():
            self.assertTrue(url_for('bower.static', filename='not_found/not_found.js'))

    def test_absolute_root_path(self):
        """
        Test using an absolute path to BOWER_COMPONENTS_ROOT
        Copies the existing bower_components folder to 'bower_components_alt'
        Sets the absolute path to the new directory as BOWER_COMPONENTS_ROOT

        Validates that url_for continues to work & tests calling get on the
        provided URL.
        """
        alt_dir = os.path.abspath(os.path.join(os.path.curdir, 'tests', 'bower_components_alt'))

        shutil.move(os.path.abspath(os.path.join(os.path.curdir, 'tests', 'bower_components')), alt_dir)

        self.app.config['BOWER_COMPONENTS_ROOT'] = alt_dir
        Bower(self.app)

        with self.app.app_context():
            self.assertEqual(bower_url_for('jquery', 'dist/jquery.js'),
                             "http://unit.test/bower/jquery/dist/jquery.min.js?version=2.1.3")
            url = bower_url_for('jquery', 'dist/jquery.js')
        client = self.app.test_client()

        self.assertEqual(client.get(url).status_code, 200)

        # move files back to leave it clean
        shutil.move(alt_dir, os.path.abspath(os.path.join(os.path.curdir, 'tests', 'bower_components')))
