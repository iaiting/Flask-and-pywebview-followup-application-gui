
def defaultconfig():
    #create default config.json file
    import json
    with open('config.json', 'w') as config:
        config_data = {
            "path_to_database": "FUDB/FOLLOWUP.DB",
            "path_to_frontend": "FUDB/",
            "path_to_dcs_info": "FUDB/",
            "path_to_bin": "bin/",
            "path_to_excels_exported_from_database": "excels exported/",
            "path_to_excels_to_be_imported_in_database": "excels to be imported/",
            "path_to_new_opfiles": "DC BATCHES IN WORK/0 NEW/",
            "path_to_batches_unassigned": "DC BATCHES IN WORK/1 UNASSIGNED/",
            "path_to_batches_prepfiles": "DC BATCHES IN WORK/2 PREPARED FILES/",
            "path_to_batches_assigned": "DC BATCHES IN WORK/3 ASSIGNED/",
            "path_to_batches_tobechecked": "DC BATCHES IN WORK/4 TO BE CHECKED/",
            "path_to_batches_tbimported": "DC BATCHES IN WORK/5 TO BE IMPORTED/",
            "path_to_batches_finished": "DC BATCHES IN WORK/6 FINISHED/",
            "path_to_batches_instandby": "DC BATCHES IN WORK/7 IN STANDBY/",
            "path_to_batches_unrecordable": "DC BATCHES IN WORK/8 UNRECORDABLE/",
            "batch_status_options_responsible": "PREP. OP FILE, IMPORTATION & SPLIT FILE, RELIABILITY & DATA UPGRADE, CHECK OP FILE, CHECK SPLIT FILE, CHECK FRONT END, **TO BE CHECKED",
            "batch_status_options_proofreader": "OP FILE OK, SPLIT FILE OK, FRONT END OK, **TO BE IMPORTED, **FINISHED, **REWORK, **STANDBY, **UNRECORDABLE",
            "batch_status_options_overall": "ONGOING, STANDBY, FINISHED, UNRECORDABLE",
            "aircraft": "A300, A300-600, A310, A320, A330, A340, A350, A380",
            "split_batch_factor": "2, 3, 4, 5, 6, 7, 8, 9",
            "generateBigID": "NO",
            "generateCustomID": "YES",
            "customIDlentgh": "6"
                        }
        #Write to file
        json.dump(config_data, config)


def get_jsonfilespath():
    #create a session json file on each call and a config.json file if not found
    import json, time, os
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        configfilepath = open(os.path.join(__location__, 'config.json'))
        with open('session.json', 'w') as sessionfile:
            sessionfilepath = open(os.path.join(__location__, sessionfile.name))
        return configfilepath.name, sessionfilepath.name
    except:
        try:
            defaultconfig() #create default config.json file if not found
            time.sleep(2) #wait for the file to be created
            configfilepath = open(os.path.join(__location__, 'config.json'))
            with open('session.json', 'w') as sessionfile:
                sessionfilepath = open(os.path.join(__location__, sessionfile.name))
            return configfilepath.name, sessionfilepath.name
        except:
            return False, False


def readjson(filepath):
    #Return a dict form a json file
    import json
    with open(filepath) as j:
        adict = json.load(j)
    return adict


def configInfo():
    #Get db path from dbpath.json file
    import json, time
    from fup.utils.jsoninfo import get_jsonfilespath

    configfilepath, sessionfilepath = 'config.json', 'session.json'
    try:
        return readjson(configfilepath)
    except:
        try:
            configfilepath, sessionfilepath = get_jsonfilespath()
            return readjson(configfilepath)
        except Exception as e:
            print("config.json file not found! creating config default Got: ", e)
            time.sleep(3)
            return configInfo()
        return False




def user_session(user_working, user_password, user_rights):
    #Write current user data session
    import json
    configfilepath, sessionfilepath = 'config.json', 'session.json'
    try:
        with open(sessionfilepath, "w") as session:
            current_user_working = user_working
            current_user_password = user_password
            current_user_rights = user_rights
            user_session_data = {"current_user_working": current_user_working,
                                 "current_user_password": current_user_password,
                                 "current_user_rights": current_user_rights}
            #Write to file
            json.dump(user_session_data, session)
    except:
        False


def sessionInfo():
    #Get curent user info from session.json file
    import json
    configfilepath, sessionfilepath = 'config.json', 'session.json'
    try:
        return readjson(sessionfilepath)
    except:
        configfilepath, sessionfilepath = get_jsonfilespath()
        return readjson(sessionfilepath)


def appSettings():
    import json
    configfilepath, sessionfilepath = 'config.json', 'session.json'
    try:
        return readjson(configfilepath)
    except:
        configfilepath, sessionfilepath = get_jsonfilespath()
        return readjson(configfilepath)
















#
