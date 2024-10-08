SECRET_LENGTH = 128

LEVEL_IDS = ['0','1']
# all the team names alogn with their maild ids
teams_data = [
                {
                    'team_name' : "TEAM_NAME_0",
                    'mail' : "MAIL_ID_0",
                },
                {
                    'team_name' : "TEAM_NAME_1",
                    'mail' : "MAIL_ID_1",
                },
            ]

INSTRUCTIONS = """
Mention instructiions here...
"""

def get_instructions():
    return INSTRUCTIONS

def gen_body():
    body = f"""
    ................ Other details .............
    Instructions : 
    {INSTRUCTIONS}
    """
    return body

def gen_team_ids(teams_data) :
    for i in range (len(teams_data)) :
        teams_data[i]['team_id'] = f'team_{i}'
    return teams_data

# Could be customly defined, do not change the function prototype ..
def valid_level(level):
    try : 
        level = int(level)
        return level in get_level_ids()
    except :
        return False

# Could be customly defined, do not change the fucntion prototype ..
def get_level_ids():
    return LEVEL_IDS