FROM    python:3.7-slim
WORKDIR /app
RUN     mkdir flaskr
ADD     ./__init__.py ./requirements.txt ./
ADD     ./models.py ./flaskr/__init__.py ./flaskr/test_flaskr.py ./flaskr/
RUN     echo "Installing dependencies..." \
          && python -m pip install -r ./requirements.txt 
CMD     ["flask", "run", "--host", "0.0.0.0"]