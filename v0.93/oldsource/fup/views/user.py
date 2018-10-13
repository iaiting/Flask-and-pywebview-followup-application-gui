from flask import Blueprint
from flask import render_template, request, redirect, url_for

#App imports
from fup.models.batch import create_table_followup, create_table_fileshistory
from fup.models.user import create_table_users, add_user, remove_user, modify_user
from fup.helpers.user import check_user, users_data
from fup.utils.jsoninfo import sessionInfo
from fup.helpers.batch import extractFollowup
from fup.utils.commun import createDirsifNotExists

user = Blueprint('user', __name__)


@user.route('/')
def login():
    createDirsifNotExists()
    response_followup = create_table_followup()
    response_users = create_table_users()
    response_fileshistory = create_table_fileshistory()
    if response_followup == True and response_users == True and response_fileshistory == True:
        return render_template('users/login.html')
    else:
        errormessage = "Couldn't connect to the FOLLOWUP.DB - correct config.json file (path_to_database)!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))


@user.route('/delegate-page', methods=['GET', 'POST'])
def delegateUserPage():
    #Check user in database and send corespondend template
    username = request.form['username']
    password = request.form['password']
    check_user(username, password)
    userinfo = sessionInfo()
    #print('guguuuu', userinfo)
    if userinfo["current_user_rights"] == 'user':
        return render_template('users/user_page.html')
    elif userinfo["current_user_rights"] == 'proofreader':
        return render_template('users/proofreader_page.html')
    elif userinfo["current_user_rights"] == 'admin':
        return render_template('users/admin_page.html')
    else:
        errormessage = "Incorrect inputs or user not in database!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))


@user.route('/home-page')
def homePage():
    #Check user in database and send corespondend template
    userinfo = sessionInfo()
    username = userinfo['current_user_working']
    password = userinfo['current_user_password']
    check_user(username, password)
    userinfo = sessionInfo()
    if userinfo["current_user_rights"] == 'user':
        return render_template('users/user_page.html')
    elif userinfo["current_user_rights"] == 'proofreader':
        return render_template('users/proofreader_page.html')
    elif userinfo["current_user_rights"] == 'admin':
        return render_template('users/admin_page.html')
    else:
        errormessage = "Incorrect inputs or user not in database!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))




@user.route('/manage-users')
def showManageUsersPage():
    context = users_data()
    return render_template('users/manage_users.html', context=context)


@user.route('/users-management', methods=['GET', 'POST'])
def apply_manage_users():
    useremail = request.form['user_email']
    try:
        userpassword = request.form['user_password']
    except:
        userpassword = ''
    try:
        user_right = request.form['user_rights']
    except:
        user_right = ''
    try:
        admin_choice = request.form['admin_choice']
    except:
        admin_choice = ''
    try:
        defaultProofreader = request.form["defaultProofreader"]
    except:
        defaultProofreader = ''

    #print(useremail, userpassword, user_right, defaultProofreader)

    if admin_choice == "add_user":
        if add_user(useremail, userpassword, user_right, defaultProofreader):
            return redirect(url_for('comm.showSuccessPage'))
        else:
            errormessage = "Changes not saved into the database!"
            return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
    elif admin_choice == "remove_user":
        if remove_user(useremail):
            return redirect(url_for('comm.showSuccessPage'))
        else:
            errormessage = "Changes not saved into the database!"
            return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
    elif admin_choice == "modify_user":
        if modify_user(useremail, userpassword, user_right, defaultProofreader):
            return redirect(url_for('comm.showSuccessPage'))
        else:
            errormessage = "Changes not saved into the database!"
            return redirect(url_for('comm.showFailedPage', errormessage=errormessage))


@user.route("/extract-your-batches")
def applyextractFollowup():
    try:
        extractFollowup(user_batches=True)
        return redirect(url_for('comm.showSuccessPage'))
    except:
        errormessage = "Something went wrong when extracting the excel from database"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
























#
