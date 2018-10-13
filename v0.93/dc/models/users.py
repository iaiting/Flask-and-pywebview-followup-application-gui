import os
import pandas as pd
from dc.utils.dbwrap import Dbwrap
from dc.utils.commun import Commun

class User:

    func = Commun()
    conf = func.config_info()
    db = Dbwrap(conf["path_to_database"])

    def add_user(self, username, userpassword, userrights, defaultproofreader):
        """Adds a user to the database"""
        user_row = {
            "User": username,
            "Password": userpassword,
            "Rights": userrights,
            "Proofreader": defaultproofreader}
        return self.db.create_row("users", user_row)


    def remove_user(self, username):
        """Delete user from users table"""
        return self.db.delete_row("users", "User", username)

    
    def get_all_users(self, asdict=True):
        """Get user table from database in dictionary format or dataframe format"""
        table = self.db.get_table("users", asdict=asdict)
        return table

    def verify_user(self, username, userpassword):
        """Check if user is in the database"""
        user_data = self.db.select_row("users", "User", username)
        
        if len(user_data["User"]) == 1 and len(user_data["Password"]) == 1:
            user_session = {"User": user_data["User"][0], "Password": user_data["Password"][0], "Rights": user_data["Rights"][0]}
            self.func.write_json(user_session, "session.json")
            return user_session 

    def session_info(self):
        """Get info from session.json file"""
        session_data = self.func.read_json("session.json")
        return session_data

    def get_users_by_rights(self, rights):
        """Get users list by specified rights from users table"""
        users_df = self.get_all_users(asdict=False)
        users_df = users_df[users_df["Rights"] == rights]
        users_df = users_df.to_dict("list")
        usersli = users_df["User"]
        return usersli

    def get_proofreaders(self):
        """Get proofreaders list"""
        return self.get_users_by_rights(rights="proofreader")

    def get_users(self):
        """Get users list"""
        return self.get_users_by_rights(rights="user")

    def get_admins(self):
        """Get admins list"""
        return self.get_users_by_rights(rights="user")

    def get_settings(self):
        """Get app settings"""
        data = self.func.read_json("config.json")
        return data

    
    def export_table(self, table_name):
        """Export followup from db"""
        export_path = self.conf["path_to_excels_exported_from_database"]
        df = self.db.read_table(table_name)
        save_path = os.path.join(export_path, "{}.xlsx".format(table_name))
        df.to_excel(save_path, index=False)
    
    def import_table(self, table_name):
        """Import table into db, replace table if exists"""
        import_path = self.conf["path_to_excels_to_be_imported_in_database"]
        followup_file_path = os.path.join(import_path, "{}.xlsx".format(table_name))
        fupdf = pd.read_excel(followup_file_path)
        self.db.insert_table(fupdf, table_name)

    
        

        

        