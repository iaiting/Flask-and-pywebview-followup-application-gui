
class Queries:

    """Contains static variables with sql queries for this app tables"""

    #Query for creating the followup table in db
    sql_create_table_followup = """CREATE TABLE IF NOT EXISTS `followup` (`BatchID` TEXT,
                                                                    `Aircraft` TEXT,
                                                                    `Operator` TEXT,
                                                                    `OriginalFilesName` TEXT,
                                                                    `OriginalFilesPath` TEXT,
                                                                    `FilesID` TEXT,
                                                                    `AddedDate` TEXT,
                                                                    `StartDate` TEXT,
                                                                    `Responsible` TEXT,
                                                                    `Proofreader` TEXT,
                                                                    `ResponsibleStatus` TEXT,
                                                                    `ProofreaderStatus` TEXT,
                                                                    `ResponsibleComment` TEXT,
                                                                    `ProofreaderComment` TEXT,
                                                                    `OverallStatus` TEXT,
                                                                    `EstimatedTaskNbr` TEXT,
                                                                    `EstimatedFdgNbr` TEXT,
                                                                    `TotalRowsNbr` TEXT,
                                                                    `MPDTaskRowsNbr` TEXT,
                                                                    `OperatorRowsNbr` TEXT,
                                                                    `FindingsRowsNbr` TEXT,
                                                                    `ChangesLog` TEXT,
                                                                    `ImportedDateISAIM` TEXT);
                                                                """

    #Query for creating the fileshistory table in db
    sql_create_table_fileshistory = """CREATE TABLE IF NOT EXISTS `fileshistory` (`FileID` TEXT,
                                                                            `AddedInBatch` TEXT,
                                                                            `FileName` TEXT,
                                                                            `FileSizeBytes` TEXT,
                                                                            `ModificationDate` TEXT);
                                                                        """


    #Used for creation of user table
    sql_create_table_users = """CREATE TABLE IF NOT EXISTS `users` (`UserEmail` TEXT, 
                                                                    `UserPassword` TEXT, 
                                                                    `UserRights` TEXT, 
                                                                    `DefaultProofreader` TEXT, 
                                                                    PRIMARY KEY(`UserEmail`));"""
