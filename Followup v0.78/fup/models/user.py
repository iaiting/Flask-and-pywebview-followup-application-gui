def create_table_users():
    from fup.models.sqlquery import sql_create_table_users, sql_user_first_use, sql_delete_default_admin
    from fup.utils.dbwrap import execute_query, get_dftable
    try:
        execute_query(sql_create_table_users)
        user_df = get_dftable('users')
        rows, _ = user_df.shape
        if rows == 0:
            return execute_query(sql_user_first_use)
        elif rows > 1:
            return execute_query(sql_delete_default_admin)
        return True
    except Exception as e:
        print("Users table error: ", e)
        return False


def add_user(useremail, userpassword, user_right, defaultProofreader):
    from fup.utils.dbwrap import execute_query
    from fup.models.sqlquery import insert_user

    if len(defaultProofreader) == 0:
        defaultProofreader = "UNASSIGNED"
    insert_user = insert_user.format(useremail, userpassword, user_right, defaultProofreader)
    return execute_query(insert_user)


def modify_user(UserEmail, UserPassword, UserRights, DefaultProofreader):
    from fup.utils.dbwrap import execute_query
    from fup.utils.commun import validate
    from fup.helpers.user import update_user
    import inspect
    frame = inspect.currentframe()
    args, _, _, paramdict = inspect.getargvalues(frame)

    validated = validate(args, paramdict)

    for col, val in validated.items():
        if col == 'UserEmail': continue
        if update_user(validated['UserEmail'], col, val):
            pass
        else:
            return False

    return True


def remove_user(UserEmail):
    from fup.utils.dbwrap import execute_query
    delete_user = """DELETE FROM users WHERE UserEmail='{}' """.format(UserEmail)
    return execute_query(delete_user)
