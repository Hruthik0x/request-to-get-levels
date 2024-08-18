Note : 
- Add "credentials.json" file and fill in the "MONGO_URI"
- Please install libs from requirements.txt

## Configuring levels
All levels could be customized, under "Levels" folder
- New levels could be added, use the existing files (in Levels folder)0.py and 1.py as the templates
- You can configure the function gen_question to generate a question and its answer everytime its called 

| Variable         | Description                                                            |
|------------------|------------------------------------------------------------------------|
| `HINT_TEXT`      | Text sent when the user sends a request to the particular level        |
| `HINT_POINTS`    | Number of points deducted when the user requests for the hint          |
| `POINTS`         | Number of points awarded for a correct answer                          |
| `PENALTY_POINTS` | Number of points deducted for every wrong answer                       |


## config.py

| Function       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `get_instructions` | Text sent when user requests for instructions                               |
| `gen_body`     | This generates the body for the email to be sent, could be customized by the user |
| `valid_level`  | Checks if a given level_id is valid or not, could be customized by user     |
| `get_level_ids`| Returns the level ids, could be customized by the user                      |
| `gen_team_ids` | Generates team ids for each team                                            |
| `LEVEL_IDS` | Add the file names here that you want your server to use (Do not include ".py")|

## Launching and testing
Launch it with `server.py` 

API could be tested using this [file](https://github.com/Hruthik0x/request-to-get-levels/blob/main/Request_2_get_level.postman_collection.json)
