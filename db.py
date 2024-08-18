import random
import string
import json
from config import SECRET_LENGTH, MIN_LEVEL, MAX_LEVEL, teams_data, get_level_ids, gen_team_ids, valid_level
from pymongo import MongoClient# all the team names alogn with their maild ids
from importlib.util import spec_from_file_location, module_from_spec

class DB : 
    client = None
    levels_db = None
    creds_col = None

# used in server.py
def init_db():
# EDIT THE COFIDENTIAL.JSON FILE, DO NOT CHANGE THE BELOW LINES
    with open('confidential.json') as f:
        data = json.load(f)

    MONGO_URI = data['MONGO_URI']
    DB.client = MongoClient(MONGO_URI)
    DB.creds_col = DB.client['creds']['creds']
    DB.levels_db = DB.client['levels']
    DB.team_ids = DB.levels_db.list_collection_names()

    if (check_creds_db == False ) : 
        print(" >> WARNING !! - CREDS DB IS NOT IN PROPER FORMAT")
        while True :
            user_input = input(" >> Type 'RESET_CREDS_DB' to reset the LEVELS db, or type 'QUIT' to stop the server and quit")
            if (user_input == 'RESET_CREDS_DB') :
                reset_creds_db()
                break
            elif (user_input == 'QUIT') :
                quit() 
            else : 
                print(" >> INVALID INPUT GIVEN, TRY AGAIN")

    if (check_levels_db == False ) :
        print(" >> WARNING !! - LEVELS DB IS NOT IN PROPER FORMAT")
        while True :
            user_input = input(" >> Type 'RESET_LEVELS_DB' to reset the LEVELS db, or type 'QUIT' to stop the server and quit")
            if (user_input == 'RESET_LEVELS_DB') :
                reset_levels_db()
                break
            elif (user_input == 'QUIT') :
                quit() 
            else : 
                print(" >> INVALID INPUT GIVEN, TRY AGAIN")

# Used in server.py
# Exposed 
def get_hint(team_id, secret, level):
    if (validate_creds(team_id, secret) == 0) :
        return "Invalid Creds"
    if (valid_level(level) == False) :
        return "Invalid level"
    data = DB.levels_db[team_id].find_one({'_id': level})
    if (data['hint_penalty_charged'] == 0) :
        total_points = get_score(team_id)
        hint_penalty = data['hint_penalty']
        # Update the hint penalty charged
        DB.levels_db[team_id].update_one( {'_id': level}, 
                                          {'$set': 
                                          {
                                              'hint_penalty_charged': data['hint_penalty_charged'] - hint_penalty, 
                                              'points_charged': data['points_charged'] - hint_penalty,
                                          }})
        # Update the total score of the team
        set_total_score(team_id, total_points - 
                        hint_penalty)
        return data['hint_text'] + '\n' + f"Hint penalty applied : {hint_penalty} points for taking hint, updated score : {total_points - hint_penalty}" 
    else :
        return data['hint_text']

# Used in server, db.get_score
# returns team_id : score dictionary
def get_scores():
    # Gotta rewrite this function
    team_scores = []
    team_ids = DB.levels_db.list_collection_names()
    for team_id in team_ids : 
        data = DB.levels_db[team_id].find_one({'_id' : team_id})
        team_scores.append([data['name'], team_id, data['total_score']])
    team_scores.sort(key=lambda x: x[2])
    team_scores_json = {}
    for score in team_scores :
        team_scores_json[score[1]] = {score[0] : score[2]}
    return team_scores_json

def get_questions(team_id):
    if (team_id in DB.team_ids) :
        collection = DB.levels_db[team_id]
        questions = {}
        for level in get_level_ids() :
            questions[level] = collection.find_one({'_id' : str(level)})['question']
        return questions    
    else :
        return "Invalid team_id"

# Checks answer from db - get_answer
# Updates score in db - Increase / decreases 
# Sets level status in db - set_level_status
def validate_answer(team_id, secret, level, answer):
    if (validate_creds(team_id, secret) == 0) :
        return "Invalid Creds"
    if (valid_level(level) == False) :
        return "Invalid level"
    else :
        data = DB.levels_db[team_id].find_one({'_id' : level})
        total_score = get_score(team_id)
        if (data['status'] == True) :
            return "You have already solved this question"
        else : 
            if (answer == data['answer']) :
                # Update the level status and level score 
                DB.levels_db[team_id].update_one({'_id' : level}, {'$set' : {'status' : True, 'points_charged' : data['points_charged'] + data['points']}})
                # Update the total score of the team
                DB.levels_db[team_id].update_one({'_id' : team_id}, {'$set' : {'total_score' : total_score + data['points']}})
                return f"CORRECT ANSWER, SCORE INCRRASED BY : {data['points']} POINTS.\nUPDATED SCORE : {total_score + data['points']}"
            
            else :
                # Update the score and penalty charged 
                DB.levels_db[team_id].update_one({'_id' : level}, {'$set' : {'points_charged' : data['points_charged'] - data['wrong_penalty'], 'wrong_penalty_charged' : data['wrong_penalty_charged'] - data['wrong_penalty']}})
                # Update the total score of the team
                DB.levels_db[team_id].update_one({'_id' : team_id}, {'$set' : {'total_score' : total_score - data['wrong_penalty']}})
                return f"WRONG ANSWER TRY AGAIN, PENALTY APPLIED : {data['wrong_penalty']} POINTS.\nUDPATED SCORE : {total_score - data['wrong_penalty']}"

# This is both exposed and internal
# Exposed : If user wants to reset the db they can use this 
# Internal : Used by init_db 
def reset_creds_db() :
    global teams_data
    # Dropping the db and then creating it again
    DB.client.drop_database('creds')
    DB.creds_db = DB.client['creds']
    DB.creds_col = DB.creds_db['creds']
    teams_data = gen_team_ids(teams_data)

    for team in teams_data : 
        insert_data = {
                        '_id': team['team_id'], 
                       'secret': gen_secret(SECRET_LENGTH),
                       'mail': team['mail'],
                       }
        DB.creds_col.insert_one(insert_data)

# This is both exposed and internal
# Exposed : If user wants to reset the db they can use this 
# Internal : Used by init_db 
def reset_levels_db() :
    global teams_data
    teams_data = gen_team_ids(teams_data)
    DB.client.drop_database('levels')
    DB.levels_db = DB.client['levels']

    for team in teams_data :
        collection = DB.levels_db[team['team_id']]
        # To maintain total score of the team
        insert_data = {
            '_id' : team['team_id'],
            'total_score' : 0,
            'name' : team['team_name'],
        }
        collection.insert_one(insert_data)
        for level in get_level_ids() :
            # use approriate gen_question function
            question, answer = gen_question(level)
            hint_penalty_points = get_var_dynamic(str(level), ['HINT_PENALTY'])[0]
            wrong_penalty_points = get_var_dynamic(str(level), ['PENALTY_POINTS'])[0]
            hint_text = get_var_dynamic(str(level), ['HINT_TEXT'])[0]
            points = get_var_dynamic(str(level), ['POINTS'])[0]
            insert_data = {
                '_id' : str(level), 
                'status' : False ,
                'points_charged' : 0,
                'hint_penalty_charged' : 0,
                'wrong_penalty_charged' : 0,
                'hint_penalty' : hint_penalty_points ,
                'wrong_penalty' : wrong_penalty_points,
                'points' : points,
                'question' : question,
                'answer' : str(answer),
                'hint_text' : hint_text
            }
            collection.insert_one(insert_data)


# ================== INTERNAL FUNCTIONS ==================
# Note : Internal functions do not check if a particular collection exists 
#        before performing any operation on it.

# returns current total socre of the team
# used in db.validate_answer, db.get_scores
def get_score(team_id):
    return DB.levels_db[team_id].find_one({'_id' : team_id})['total_score']

# Used in db.reset_db.py
def gen_question(level):
    spec = spec_from_file_location(str(level), 'Levels/'+str(level)+".py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    gen_question_var = getattr(module, 'gen_question')
    return gen_question_var()

# Used in db.get_hint
def get_hint_text(level):
    return get_var_dynamic(str(level), ['HINT_TEXT'])[0]

# Used in reset_db to generate every user's secret
def gen_secret(n):
    secret = ''.join(random.choices(string.ascii_letters + string.digits, k=n))
    return secret

# Used to get a variable 'var_name' from a file 'file_name'
def get_var_dynamic(file_name, var_names):
    out = []
    spec = spec_from_file_location(file_name, 'Levels/'+file_name+".py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    for var_name in var_names :
        out.append(getattr(module, var_name))
    return out 

# Used to verify secret and team id
def validate_creds(team_id, secret):
    out = DB.creds_col.find_one({'_id' : team_id})
    if ( out is not None ):
        if out['secret'] == secret :
            return 1     
    return 0

# Used in db.validate_answer
# Before calling this function ensure team id exists, level exists
def get_answer(team_id, level):
    return DB.levels_db[team_id].find_one({'_id' : level})['answer']

# Used in db.validate_answer
# Before calling this function ensure team_id exists, level exists
def set_level_status(team_id, level_id, status):
    DB.levels_db[team_id].update_one({'_id' : level_id},{'$set': {'status': status}})

# Used in db.validate_answer
# Ensure team_id exists before calling this function
def set_total_score(team_id, score):
    DB.levels_db[team_id].update_one({'_id' : team_id}, {'$set' : {'total_score' : score}})


def check_creds_db() :
    return True

def check_levels_db() :
    return True 
