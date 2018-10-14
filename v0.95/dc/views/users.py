
from flask import Blueprint
from flask import render_template, request, redirect, url_for

user_bp = Blueprint('user_bp', __name__)

#Custom
from dc.utils.folders import Folders
from dc.utils.commun import Commun
from dc.models.queries import Queries
from dc.models.users import User


folder = Folders()
func = Commun()
q = Queries()
user = User()



@user_bp.route('/')
def login():
    try:
        folder.make_default_dirs()
        if not folder.db_exists():
            q.create_followup_db()
            return render_template('users/manage_users.html')
        else:
            return render_template('users/login.html')
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage=str(err)))

        

@user_bp.route('/users-management', methods=['GET', 'POST'])
def apply_manage_users():
   
    useremail = request.form['user_name']
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

  
    if admin_choice == "add_user":
        if user.add_user(useremail, userpassword, user_right, defaultProofreader):
            return redirect(url_for('com_bp.showSuccessPage'))
        else:
            errormessage = "Changes not saved into the database!"
            return redirect(url_for('com_bp.showFailedPage', errormessage=errormessage))
    
    elif admin_choice == "remove_user":
        if user.remove_user(useremail):
            return redirect(url_for('com_bp.showSuccessPage'))
        else:
            errormessage = "Changes not saved into the database!"
            return redirect(url_for('com_bp.showFailedPage', errormessage=errormessage))



@user_bp.route('/delegate-page', methods=['GET', 'POST'])
def delegateUserPage():
    #Check user in database and send corespondend template
    username = request.form['username']
    password = request.form['password']
    userinfo = user.verify_user(username, password)
    
    if not isinstance(userinfo, dict):
        errormessage = "Incorrect inputs or user not in database!"
        return redirect(url_for('com_bp.showFailedPage', errormessage=errormessage))
    
    context = user.context_disable()
    
    return render_template('users/home_page.html', context=context)
    
    # if userinfo["Rights"] == 'user':
    #     return render_template('users/user_page.html')
    # elif userinfo["Rights"] == 'proofreader':
    #     return render_template('users/proofreader_page.html')
    # elif userinfo["Rights"] == 'admin':
    #     return render_template('users/home_page.html')
    # else:
    #     errormessage = "Incorrect inputs or user not in database!"
    #     return redirect(url_for('com_bp.showFailedPage', errormessage=errormessage))


@user_bp.route('/manage-users')
def showManageUsersPage():
    context = {"proofreaders": user.get_proofreaders(),
                "all_users": user.get_all_users()}
    return render_template('users/manage_users.html', context=context)


@user_bp.route('/home-page')
def homePage():
    context = user.context_disable()
    return render_template('users/home_page.html', context=context)
    

@user_bp.route('/app-settings/')
def showAppSettings():
    context = user.get_settings()
    return render_template('app_settings.html', context=context)


@user_bp.route("/import-export")
def showimportexport():
    context = user.context_disable()
    return render_template('tasks/import_export.html', context=context)


@user_bp.route("/extract-followup")
def extractFollowup():
    try:
        user.export_table("followup")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't extract followup table!"))
        


@user_bp.route("/extract-fileshistory")
def extractFileshistory():
    try:
        user.export_table("fileshistory")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't extract fileshistory table!"))


@user_bp.route("/extract-users")
def extractUsers():
    try:
        user.export_table("users")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't extract users table!"))



@user_bp.route("/import-followup")
def importFollowup():
    try:
        user.import_table("followup")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't import followup table!"))


@user_bp.route("/import-fileshistory")
def importFileshistory():
    try:
        user.import_table("fileshistory")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't import fileshistory table!"))


@user_bp.route("/import-users")
def importUsers():
    try:
        user.import_table("users")
        return redirect(url_for('com_bp.showSuccessPage'))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage="Can't import users table!"))

    

