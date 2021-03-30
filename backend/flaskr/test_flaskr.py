from unittest import (
    mock,
    TestCase, 
    main
)
from flask_sqlalchemy import SQLAlchemy
from requests import (
    get,
    post,
    delete, 
    put
)
from flaskr import create_app
from models import setup_db
from werkzeug.exceptions import InternalServerError
from typing import List

BASE_URL = "http://flask_api:5000"
BODY = {
    "question": "Was Maradona better than Messi?",
    "category": "6",
    "answer": """Yes, since Maradona managed to win the World Cup once, 
                        whereas Messi hasn't reached that level yet.""",
    "difficulty": "7"
}


class TriviaTestCase(TestCase):
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
        
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        pass

    def test_get_categories_success(self):
        """
            Given a postgresql instance and flask app both up and running,
            When I hit the /api/v1/categories endpoint with the GET method,
            Then I get a 200 response in json format.
        """
        res = get(f"{BASE_URL}/api/v1/categories")
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)
        [self.assertIsInstance(el, dict) for el in res.json()]
        
        # Each occurrence of the returned response presents the following fields:
        # id, type. 
        for el in res.json():
            self.assertEqual(
                [k for k in filter(lambda k: k in el.keys(), 
                                   ["id", "type"])], 
                ["id", "type"]
            )

    def test_categories_method_not_allowed(self):
        """
            Given a postgresql instance and a flask app both up and running,
            When I hit the /api/v1/categories endpoint using the 
                PUT method (which is not allowed),
            Then I get a 405 response in json format.
        """
        res = put(f"{BASE_URL}/api/v1/categories")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 405)
        self.assertIsInstance(res.json(), dict)
        
        # The returned response must present the following fields:
        # status, success, message.
        self.assertEqual(
            [k for k in filter(lambda k: k in res.json(), 
                               ["status", "success", "message"])],
            ["status", "success", "message"]
        )
        self.assertEqual(res.json.get("status"), 405)
                    
    @mock.patch("flaskr.Category.query.all", side_effect=InternalServerError())
    def test_categories_internal_server_error(self, mock_output):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/categories endpoint with the GET method, 
            But a server-side occurs,
            Then I get a 500 response in json format.
        """
        responses = list()
        responses.append(get(f"{BASE_URL}/api/v1/categories")) 
        responses.append(get("f{BASE_URL}/api/v1/categories/1"))
        
        for res in responses:
            self.assertEqual(res.ok, False)
            self.assertEqual(res.status_code, 500)
            self.assertIsInstance(res.json(), dict)
            self.assertEqual(
                [k for k in filter(lambda k: k in res.json(), 
                                   ["status", "success", "message"])],
                ["status", "success", "message"]
            )
            self.assertEqual(res.json().get("status"), 500)
    
    def test_get_category_by_id_success(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/categories/<int:id> endpoint using 
                an existent id and the GET method, 
            Then I get a 200 response in json format.
        """
        EXISTENT_CAT: int = 1
        res = get(f"{BASE_URL}/api/v1/categories/{EXISTENT_CAT}")
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), dict)
    
    def test_get_category_by_id_not_found(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/categories/<int:id> endpoint using 
                a non-existent id and the GET method, 
            Then I get a 404 response in json format.
        """
        NON_EXISTENT_CAT: int = 27
        res = get(f"{BASE_URL}/api/v1/categories/{NON_EXISTENT_CAT}")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 404)
    
    def test_get_category_method_not_allowed(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/categories/<int:id> endpoint using 
                an existing id and the POST method, 
            Then I get a 405 response in json format.
        """
        res = post(f"{BASE_URL}/api/v1/categories/1")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 405)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 405)

    def test_get_question_success(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the GET method, 
            Then I get a 200 response in json format.
        """
        res = get(f"{BASE_URL}/api/v1/questions")
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        
        data: List[dict] = res.json()
        # Testing pagination works properly
        self.assertEqual(len(data), 10)
        # Verifying data complies to specs 
        for el in res.json():
            self.assertIsInstance(el, dict)
            self.assertEqual(
                [key for key in filter(lambda k: k in el.keys(), ["id",
                                                                  "question", 
                                                                  "answer",
                                                                  "category",
                                                                  "difficulty"])],
                ["id", "question", "answer", "category", "difficulty"]
            )
            self.assertIsInstance(el.get("id"), int)
            self.assertIsInstance(el.get("question"), str)
            self.assertIsInstance(el.get("answer"), str)
            self.assertIsInstance(el.get("category"), int)
            self.assertIsInstance(el.get("difficulty", int))

    def tests_get_questions_method_not_allowed(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint using 
                the PUT method (which is not allowed),
            Then I get a 200 response in json format.
        """
        res = put(f"{BASE_URL}/api/v1/questions")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 405)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 405)

    @mock.patch("flaskr.Question.query.all", side_effect=InternalServerError())
    def test_post_question_internal_server_error(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the POST method,
            But a server-side error occurs,
            Then I get a 200 response in json format.
        """
        res = get(f"{BASE_URL}/api/v1/questions")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 500)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 500)

    def test_post_question(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the POST method 
            And a properly constructed payload is used,
            Then I get a 200 response in json format.
        """
        res = post(f"{BASE_URL}/api/v1/questions", data=BODY)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 201)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(
            [el for el in filter(lambda k: k is res.json().keys(), ["id",
                                                                    "question",
                                                                    "category",
                                                                    "answer",
                                                                    "difficulty"])],
            ["id", "question", "category", "answer", "difficulty"]
        )
        self.assertEqual(res.json().get("question"), BODY.get("question"))
        self.assertEqual(res.json().get("answer"), BODY.get("answer"))
        self.assertEqual(int(res.json().get("category")), BODY.get("category"))
        self.assertEqual(int(res.json().get("difficulty")), BODY.get("difficulty"))

    def test_post_question_unprocessable(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the POST method,
            But a ill-constructed payload is used,
            Then I get a 422 response in json format.
        """
        truncated_body: dict = BODY
        truncated_body.pop("difficulty")
        res = post(f"{BASE_URL}/api/v1/questions", data=truncated_body)
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 422)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json.get("status"), 422)        

    def test_get_delete_question_by_id_failure(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the GET method,
            But a non-existent id is used,
            Then I get a 404 response in json format.
            
            Similarly,
            
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the DELETE method,
            But a non-existent id is used,
            Then I get a 404 response in json format.

        """
        NON_EXISTENT_ID: int = 6 ** 7
        responses = list()
        responses.append(get(f"{BASE_URL}/api/v1/questions/{NON_EXISTENT_ID}"))
        responses.append(delete(f"{BASE_URL}/api/v1/questions/{NON_EXISTENT_ID}"))
        for res in responses:
            self.assertEqual(res.ok, False)
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res.json(), dict)
            self.assertEqual(res.json.get("status"), 404)

    def test_delete_question_success(self):
        """ 
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the DELETE method,
            And an EXISTENT ID is used,
            Then I get a 204 response in json format.
        """
        res = post(f"{BASE_URL}/api/v1/questions", data=BODY)
        new_id = res.json().get("id")
        res = delete(f"{BASE_URL}/api/v1/questions/{new_id}") 
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 204)

    @mock.patch("flaskr.form.get", side_effect=InternalServerError())
    def test_get_q_using_search_term_failure(self, mock_output):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/search-term endpoint 
                with the POST method,
            But server-side error occurs,
            Then I get a 500 response in json format.
        """
        res = post(f"{BASE_URL}/api/v1/questions/search-term") 
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 500)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 500)

    def test_get_q_using_search_term_bad_request(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions endpoint with the POST method,
            But a ill-constructed payload is used (i.e., data=None),
            Then I get a 400 response in json format.
        """
        res = post(f"{BASE_URL}/api/v1/questions/search-term") 
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 400)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 400)

    def test_get_q_using_search_term_success(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/play endpoint with the POST method,
            And a properly constructed payload is used 
                (i.e., search_term field is not None),
            Then I get a 200 response in json format.
        """
        search_term = {"search_term": "Maradona"} 
        res = post(f"{BASE_URL}/api/v1/questions/search-term", data=search_term) 
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)
        
        # I want to make sur that the resource returned presents the following fields:
        # id, question, category, answer, difficulty.
        if len(res.json()):
            self.assertEqual(
                [el for el in filter(lambda k: k is res.json().keys(), ["id",
                                                                        "question",
                                                                        "category",
                                                                        "answer",
                                                                        "difficulty"])],
                ["id", "question", "category", "answer", "difficulty"]
            )
    
    @mock.patch("flaskr.request.get_json", side_effect=InternalServerError())
    def test_get_question_play_failure(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/play endpoint,
            But a server-side error takes place,
            Then a 500 response is returned in json format.
        """
        res = get(f"{BASE_URL}/api/v1/questions/play")
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 500)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 500)
   
    def test_get_question_play(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/play endpoint with the POST method,
            And a properly constructed payload
            Then I get a 200 response in json format.
        """
        payload = {"previous_question": 19, "category": 2}
        res = post(f"{BASE_URL}/api/v1/questions/play", data=payload)
        self.assertEqual(res.ok, True)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), dict)

        # I want to make sure that the returned resource presents the following
        # fields: id, question, category, answer, difficulty.
        if len(res.json().keys()):
            self.assertEqual(
                [el for el in filter(lambda k: k is res.json().keys(), ["id",
                                                                        "question",
                                                                        "category",
                                                                        "answer",
                                                                        "difficulty"])],
                ["id", "question", "category", "answer", "difficulty"]
            )

    def test_get_question_play_unprocessable_payload(self):
        """ 
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/play endpoint with the POST method,
            But ill-constructed payload is used 
                (i.e., a payload lacking one of the required fields),
            Then I get a 422 response in json format.
        """
        payload = {"previous_question": 19}
        res = post(f"{BASE_URL}/api/v1/questions/play", data=payload)
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 422)
        self.assertIsInstance(res.json(), dict)
        self.assertIsInstance(res.json().get("status"), 422) 

    def test_get_question_play_w_non_existent_cat(self):
        """
            Given a psql instance and a flask app both up and running,
            When I hit the /api/v1/questions/play endpoint with the POST method,
            But a payload with a non existing category ID is used,
            Then I get a 404 response in json format. 
        """
        NON_EXISTENT_CAT: int = 6 ** 7
        payload = {"previous_question": 19, "category": NON_EXISTENT_CAT}
        res = post(f"{BASE_URL}/api/v1/questions/play", data=payload)
        self.assertEqual(res.ok, False)
        self.assertEqual(res.status_code, 404)
        self.assertIsInstance(res.json(), dict)
        self.assertEqual(res.json().get("status"), 404)


if __name__ == "__main__":
    main()
