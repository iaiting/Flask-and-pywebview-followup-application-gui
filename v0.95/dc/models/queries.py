from dc.utils.dbwrap import Dbwrap
from dc.utils.commun import Commun

class Queries:

    func = Commun()
    conf = func.config_info()
    db = Dbwrap(conf["path_to_database"])

    """Contains static variables with sql queries for this app tables"""

    #Query for creating the followup table in db
    sql_create_table_followup = """CREATE TABLE IF NOT EXISTS `followup` (`BatchID` TEXT,
                                                                    `Aircraft` TEXT,
                                                                    `Operator` TEXT,
                                                                    `OriginalFilesName` TEXT,
                                                                    `OriginalFilesPath` TEXT,
                                                                    `FilesID` TEXT,
                                                                    `AddedDate` DATE,
                                                                    `StartDate` DATE,
                                                                    `Responsible` TEXT,
                                                                    `Proofreader` TEXT,
                                                                    `ResponsibleStatus` TEXT,
                                                                    `ProofreaderStatus` TEXT,
                                                                    `ResponsibleComment` TEXT,
                                                                    `ProofreaderComment` TEXT,
                                                                    `OverallStatus` TEXT,
                                                                    `EstimatedTaskNbr` INTEGER,
                                                                    `EstimatedFdgNbr` INTEGER,
                                                                    `TotalRowsNbr` INTEGER,
                                                                    `MPDTaskRowsNbr` INTEGER,
                                                                    `OperatorRowsNbr` INTEGER,
                                                                    `FindingsRowsNbr` INTEGER,
                                                                    `ChangesLog` TEXT,
                                                                    `ImportedDateISAIM` DATE);
                                                                """

    #Query for creating the fileshistory table in db
    sql_create_table_fileshistory = """CREATE TABLE IF NOT EXISTS `fileshistory` (`FileName` TEXT,
                                                                            `AddedInBatch` TEXT,
                                                                            `FileSize` INTEGER,
                                                                            `ModificationDate` DATE);
                                                                        """


    #Used for creation of user table
    sql_create_table_users = """CREATE TABLE IF NOT EXISTS `users` (`User` TEXT, 
                                                                    `Password` TEXT, 
                                                                    `Rights` TEXT, 
                                                                    `Proofreader` TEXT, 
                                                                    PRIMARY KEY(`User`));"""


    def create_followup_db(self):
        """Create the db  with the default tables"""
        self.db.execute_query(self.sql_create_table_users)
        self.db.execute_query(self.sql_create_table_followup)
        self.db.execute_query(self.sql_create_table_fileshistory)
        self.func.wait_file_on_disk(self.conf["path_to_database"], timeout=60)
        
