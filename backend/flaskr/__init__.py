from flask import (
    Flask, 
    request, 
    abort, 
    jsonify
)
from werkzeug.exceptions import (
    BadRequest,
    MethodNotAllowed,
    NotFound,
    UnprocessableEntity
)
from flask_cors import CORS
from typing import (
    Iterable,
    List,
    Optional
)
from dataclasses import dataclass
import logging
from .models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
METHOD_NOT_ALLOWED: str = "You cannot use this endpoint to perform a {method} request."
MSG_UNPROCESSABLE: str = "Make sur that {params} are not null."


@dataclass(frozen=True)
class QuestionPayload:
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None

    def get_null_fields(self) -> List[str]:
        problematic_keys = filter(lambda k: k[1] is None, self.__dict__.items())
        return [el[0] for el in problematic_keys]        


def paginate(results: Iterable, start_at: int) -> List[object]:
    start = (start_at - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return results[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE")
        return response

    @app.route("/api/v1/categories")
    def get_categories() -> List[dict]:
        try:
            categories: List[Category] = paginate(
                results=Category.query.all(),
                start_at=request.args.get("page", 1, type=int)
            )
            return jsonify([cat.format() for cat in categories])
        except MethodNotAllowed:
            abort(405, METHOD_NOT_ALLOWED.format(request.method))
        else:
            abort(500)
    
    @app.route("/api/v1/categories/<int:id>")
    def get_category_by_id(id: int) -> dict:
        try:
            cat: Category = Category.query.get(id)
            if cat is None:
                raise NotFound()
            return cat.format()
        except NotFound:
            abort(404)
        except MethodNotAllowed:
            abort(405)
        else: 
            abort(500)

    """
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    """
    @app.route("/api/v1/questions", methods=["GET", "POST"])
    def get_post_questions() -> List[dict]:
        try:
            if request.method == "GET":
                questions: List[Question] = paginate(
                    results=Question.query.all(),
                    start_at=request.args.get("page", 1, type=int)
                )
                return jsonify([q.format() for q in questions])
            
            if request.method == "POST":
                req_body = request.get_json()
                payload = QuestionPayload(req_body.get("question"),
                                          req_body.get("answer"),
                                          req_body.get("category"),
                                          req_body.get("difficulty"))
                           
                undefined_properties = payload.get_null_fields()
                
                if undefined_properties:
                    raise UnprocessableEntity(
                        MSG_UNPROCESSABLE.format(params=" - ".join(undefined_properties))
                    )
                question = Question(question=payload.question,
                                    answer=payload.answer,
                                    category=payload.category,
                                    difficulty=payload.difficulty)
                question.insert()
                return jsonify(question.format()), 201

        except MethodNotAllowed as e:
            logging.error(e.args)
            abort(405, METHOD_NOT_ALLOWED.format(request.method))
        except UnprocessableEntity as e:
            logging.error(e.args)
            abort(422, e.args[0] if len(e.args) else None)
        else:
            abort(500)

    @app.route("/api/v1/questions/<int:id>", methods=["GET", "DELETE"])
    def get_delete_question(id: int) -> dict:

        try:
            question = Question.query.get(id)    
            
            if question is None:
                raise NotFound()

            if request.method == "GET":
                return jsonify(question.format())

            if request.method == "DELETE":
                question.delete()
                return jsonify({}), 204

        except NotFound:
            abort(404)
        else:
            abort(500)

    @app.route("/api/v1/questions/search-term", methods=["POST"])
    def get_questions_using_search_term() -> List[dict]:
        """
            #TODO
            TEST: Search by any phrase. The questions list will update to include 
            only question that include that string within their question. 
            Try using the word "title" to start. 
        """
        try:
            payload = request.get_json()
            search_term = payload.get("search_term") if payload is not None else None
            logging.debug(f"search_term={search_term}")
            if search_term is None:
                raise BadRequest()
            
            res: List[Question] = paginate(
                results=Question.query.filter(Question.question.ilike(f"%{search_term}%")).all(), 
                start_at=request.args.get("page", 1, type=int)
            )
            return jsonify([q.format() for q in res])
        
        except BadRequest:
            abort(400, MSG_UNPROCESSABLE.format(params="search_term"))
        except MethodNotAllowed:
            abort(405, METHOD_NOT_ALLOWED.format(request.method))
        else:
            abort(500)

    @app.route("/api/v1/categories/<int:cat_id>/questions", methods=["GET"])
    def get_questions_by_category(cat_id: int) -> List[dict]:
        try:
            questions: List[Question] = paginate(
                results=Question.query.filter(Question.category == cat_id).all(),
                start_at=request.args.get("page", 1, type=int)
            )
            return jsonify([q.format() for q in questions])
        except NotFound:
            abort(404, f"Could not find a category with id={cat_id}")
        except MethodNotAllowed:
            abort(405, METHOD_NOT_ALLOWED.format(request.method))
        else:
            abort(500)

    @app.route("/api/v1/questions/quizzes", methods=["POST"])
    def post_quizzes_questions():
        """
            #TODO: Integration tests
            TEST: In the "List" tab / main screen, clicking on one of the 
            categories in the left column will cause only questions of that 
            category to be shown. 

            #TODO: Integration tests
            TEST: In the "Play" tab, after a user selects "All" or a category,
            one question at a time is displayed, the user is allowed to answer
            and shown whether they were correct or not. 
        """
        from random import randint
        try:
            body = request.get_json()
            category = body.get("quiz_category")
            previous_question = body.get("previous_questions")
            
            if category is None or previous_question is None:
                raise UnprocessableEntity(MSG_UNPROCESSABLE.format(
                    params=" - ".join(["category", "previous_question"])
                ))
            possible_questions = Question.query.filter(
                Question.category == int(category)
            ).all()
            
            if not possible_questions:
                raise NotFound(f"Could find any category with id={category}.")
            
            random_q_excluding_previous = [el for el in filter(lambda x: x.id != int(previous_question),
                                                               possible_questions)]
            if not len(random_q_excluding_previous):
                return {}
            
            idx: int = randint(0, len(random_q_excluding_previous) - 1) 
            return random_q_excluding_previous[idx].format() 

        except UnprocessableEntity as e:
            logging.warning(e.args)
            abort(422, e.args[0] if len(e.args) else None)
        except NotFound as e:
            abort(404, e.args[0] if len(e.args) else None)
        else:
            abort(500)

    @app.errorhandler(405)
    def method_not_allowed(error):
        BASIC_MSG = "Method not allowed."
        return jsonify({
            "status": 405,
            "success": False,
            "message": error.description if error.description else BASIC_MSG 
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        BASIC_MSG = "Internal Server Error"
        return jsonify({
            "status": 500,
            "success": False,
            "message": error.description if error.description else BASIC_MSG 
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        BASIC_MSG = "The requested resource was not found."
        return jsonify({
            "status": 404,
            "success": False,
            "message": error.description if error.description else BASIC_MSG 
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "status": 422,
            "success": False,
            "message": "payload is unprocessable."
        }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": 400,
            "success": False,
            "message": error.description if error.description else "Bad request" 
        }), 400
    
    return app

    
