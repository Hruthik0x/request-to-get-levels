from flask import Flask, request
#from flask_cors import CORS
from config import get_instructions
from db import get_scores, init_db, reset_creds_db, reset_levels_db, validate_answer, get_questions, get_hint

app = Flask(__name__)

# Calls get_instructions from config.py
@app.route('/instructions', methods=['GET'])
def return_instructions():
    return get_instructions()

# requires id, secret, level
@app.route('/hint', methods=['POST'])
def return_hint():
    data = request.form
    team_id = data['team_id']
    level = data['level']
    secret = data['secret']
    return get_hint(team_id, secret, level)

# requires level
@app.route('/questions', methods=['POST'])
def return_question():
    team_id = request.form['team_id']
    return get_questions(team_id)

# requires id, secret, level, answer
@app.route('/submit', methods=['POST'])
def submit_answer():
    data = request.form
    team_id = data['team_id']
    secret = data['secret']
    level = data['level']
    answer = data['answer']
    return validate_answer(team_id, secret, level, answer)

# Calls get_scores from db.py
@app.route('/scores', methods=['GET'])
def return_scores():
    return get_scores()


def init() :

    # Connects to db 
    # Checks if data in DB is in proper format
    # If data is not in proper format, prompts the user to reset the db
    # User choose to reset the db or quit.
    init_db()

    # Generates creds, new secrets 
    # reset_creds_db()

    # Generates questions, sets all levels, points to 0
    # reset_levels_db()

if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)