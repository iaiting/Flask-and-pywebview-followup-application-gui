
def get_usersdict(listallusers=False):
    from fup.utils.dbwrap import get_dftable
    import pandas as pd
    user_dict = get_dftable('users').to_dict('list')
    if listallusers == True:
        return user_dict['UserEmail']
    else:
        return user_dict


def check_user(username, password):
    from fup.utils.jsoninfo import user_session
    from fup.helpers.user import get_usersdict
    import pandas as pd

    usersdict = get_usersdict()

    usessiondict = {'userfound': False}
    for i, email in enumerate(usersdict['UserEmail']):
        try:
            user = email.split('@')[0]
        except:
            pass
        #print(username, password, email)
        if username.strip() == user.strip() or username.strip() == email.strip():
            password_db = usersdict['UserPassword'][i]
            if password_db == password:
                rights = usersdict['UserRights'][i]
                user_session(email, password_db, rights)
                usessiondict['userfound'] = True
            else:
                pass

    if usessiondict['userfound']:
        return True
    else:
        user_session('NoEmail', 'NoPass', 'NoRights')
        return False





def users_data(getdf=False):
    #Get from the users table all the proofreaders
    from fup.utils.dbwrap import get_dftable
    import pandas as pd
    usersdf = get_dftable('users')

    if getdf == True:
        return usersdf

    usersProofs = usersdf[usersdf['UserRights'] == 'proofreader']
    proofslist = usersProofs['UserEmail'].tolist()
    context = {'proofreaderList': proofslist,
               'UserEmail': usersdf['UserEmail'].tolist(),
               'UserPassword': usersdf['UserPassword'].tolist(),
               'UserRights': usersdf['UserRights'].tolist(),
               'DefaultProofreader': usersdf['DefaultProofreader'].tolist()
                }
    return context


def getuserProofreader(user):
    from fup.helpers.user import users_data
    import pandas as pd

    df_users = users_data(True)
    user_data = df_users[df_users['UserEmail'] == user]
    user_proofreader = user_data['DefaultProofreader'].tolist()[0]
    return user_proofreader















#
