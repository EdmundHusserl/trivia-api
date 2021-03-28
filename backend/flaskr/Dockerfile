FROM    python:3.7-slim
WORKDIR /app
RUN     mkdir flaskr
ADD     ./__init__.py ./test_flaskr.py ./flaskr/requirements.txt ./
ADD     ./models.py ./flaskr/__init__.py ./flaskr/
RUN     python -m pip install -r ./requirements.txt
CMD     ["flask", "run", "--host", "0.0.0.0"]