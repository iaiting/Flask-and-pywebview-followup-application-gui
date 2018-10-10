from flask import Blueprint
from flask import render_template, request, redirect, url_for

#Custom
from dc.utils.folders import Folders
from dc.utils.commun import Commun

user_bp = Blueprint('user', __name__)

#Custom instantiantion
folder = Folders()
com_funcs = Commun()



@user_bp.route('/')
def login():
    folder.make_default_dirs()
    conf = com_funcs.config_info()

    return render_template('users/login.html')
    
    # createDirsifNotExists()
    # response_followup = create_table_followup()
    # response_users = create_table_users()
    # response_fileshistory = create_table_fileshistory()
    # if response_followup == True and response_users == True and response_fileshistory == True:
    #     return render_template('users/login.html')
    # else:
    #     errormessage = "Couldn't connect to the FOLLOWUP.DB - correct config.json file (path_to_database)!"
    #     return redirect(url_for('com.showFailedPage', errormessage=errormessage))