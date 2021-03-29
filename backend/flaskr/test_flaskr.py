import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from requests import (
    get,
    post,
    delete, 
    put
)
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format("jorgepl",
                                                               "admin",
                                                               "psql_db:5432", 
                                                               self.database_name)
        self.base_url = "http://flaskr:5000"
        
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
    
        res = get(f"{self.base_url}/api/v1/categories")
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)
        [self.assertIsInstance(el, dict) for el in res.json()]
        
        for el in res.json():
            self.assertEqual(
                [k for k in filter(lambda k: k in el.keys(), 
                                   ["id", "type"])], 
                ["id", "type"]
            )

    def test_categories_method_not_allowed(self):
        res = put(f"{self.base_url}/api/v1/categories")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 405)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(
            [k for k in filter(lambda k: k in res.json(), 
                               ["status", "success", "message"])],
            ["status", "success", "message"]
        )
                         
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
