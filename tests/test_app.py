import unittest
from energy import app
from energy.views import *


class FlaskTestCase(unittest.TestCase):
    """ Test the flask app
    """
    def setUp(self):
        self.app = app.test_client()

    def test_index_status_code(self):
        """ Test some basic pages load correctly
        """
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/about/')
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
