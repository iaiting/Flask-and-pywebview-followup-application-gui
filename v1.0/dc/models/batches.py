import os
import re
import pandas as pd
from lxml import etree
from dc.utils.commun import Commun
from dc.utils.dbwrap import Dbwrap
from dc.utils.folders import Folders
from dc.models.users import User
from dc.utils.mail import Mail


class Batches:

    func = Commun()
    conf = func.config_info()
    db = Dbwrap(conf["path_to_database"])
    folder = Folders()
    user = User()
    mail = Mail(conf["MAIL_SERVER"], conf["MAIL_PORT"])

    def process_files_paths(self, filesInfodict):
        """Extract files names, set and id for each file path"""
        
        id_lentgh = int(self.conf["IDlentgh"])
        new_opfiles_path = self.conf["path_to_new_opfiles"]
        
        paths_to_files = list(filesInfodict.keys())
        
        original_files_names = []
        new_files_names = []
        for file_path in paths_to_files:
            fid = self.func.generate_id(id_lentgh)
            file_name = self.func.get_file_name(file_path)
            
            original_files_names.append(file_name)
            
            new_file_name = os.path.join("{} {}".format(fid, file_name))
            new_files_names.append(new_file_name)
    
        files = ", ".join(original_files_names)
        new_files = ", ".join(new_files_names)
        return files, new_files
    
    
    def get_paths_for_unassigned_prepared(self, bid_info):
        """Create the paths to move the folders from new to unassigned and prepared"""
        org_path = bid_info["OriginalFilesPath"]
        opfolder = "{} {}".format(bid_info["Operator"], bid_info["Aircraft"])
        
        new_path = os.path.join(org_path, opfolder)
        bid_opfolder = "{} _{}".format(opfolder, bid_info["BatchID"])
        unassigned_path = os.path.join(self.conf["path_to_batches_unassigned"], bid_opfolder)
        prepared_path = os.path.join(self.conf["path_to_batches_prepfiles"], bid_opfolder)
        
        return new_path, unassigned_path, prepared_path, bid_opfolder
    
    
    def add_id_to_prepfiles(self, bid_info, bid_opfolder):
        """Add the new files names to files in prepared/unassigned files"""
        
        org_files = self.func.listify_string(bid_info["OriginalFilesName"])
        new_files = self.func.listify_string(bid_info["FilesID"])
        prep_path = self.conf["path_to_batches_prepfiles"]
        unassg_path = self.conf["path_to_batches_unassigned"]
        
        prep_bid_path = os.path.join(prep_path, bid_opfolder)
        unassg_bid_path = os.path.join(unassg_path, bid_opfolder)
        
        for org, new in zip(org_files, new_files):
            #Paths for prepared files
            preporg_path = os.path.join(prep_bid_path, org)
            prepnew_path = os.path.join(prep_bid_path, new)
            
            #Paths for unassigned files
            unassgorg_path = os.path.join(unassg_bid_path, org)
            unassgnew_path = os.path.join(unassg_bid_path, new)
              
            self.func.move_folder(preporg_path, prepnew_path)
            self.func.move_folder(unassgorg_path, unassgnew_path)
    
    
    def copy_files_to_unassigned_prepared_dirs(self, bid_info):
        """Copy files from new folder to unassigned and prepared path folder"""
        new_path, unassigned_path, prepared_path, bid_opfolder = self.get_paths_for_unassigned_prepared(bid_info)
        #Raise error if a dir is found in new operator files 
        self.func.accept_only_files(new_path) 
        #Copy from new to unassigned
        self.func.copy_dirs(new_path, unassigned_path)
        #Copy from unassigned to prepared
        self.func.copy_dirs(unassigned_path, prepared_path)
        #Rename files from prepared folder
        self.add_id_to_prepfiles(bid_info, bid_opfolder)

    def check_file_history(self, file_info):
        """Check if an operator file was added before based on name, size and modification date"""
        
        dfgen, conn = self.db.read_table("fileshistory", chunk_size=50000)

        for df in dfgen:
            df_name = df[df["FileName"] == file_info["FileName"]]
            if df_name.shape[0] > 0:
                df_size = df[df["FileSize"] == int(file_info["FileSize"])]
                df_date = df[df["ModificationDate"] == file_info["ModificationDate"]]
                if df_size.shape[0] > 0 and df_date.shape[0] > 0:
                    conn.close()
                    raise Exception("File '{}' was added before in batch '{}'".format(df_name["FileName"].tolist()[0], df_name["AddedInBatch"].tolist()[0]))
        conn.close()
    

    def prepare_fileshistory_info(self, bid_info, files_info):
        """Get rows to insert in fileshistory and check if was previously added""" 
        
        rows = []
        for file_path, info in files_info["FilesInfo"].items():
            file_name = self.func.get_file_name(file_path)

            file_info = {"FileName": file_name,
                        "AddedInBatch": bid_info["BatchID"],
                        "FileSize": info["FileSize"],
                        "ModificationDate": info["ModificationDate"]}

            self.check_file_history(file_info)
            rows.append(file_info)

        return rows
    

    def add_batch(self):
        """Add batch to database """
        bid = self.func.generate_id(int(self.conf["IDlentgh"]))
        files_info = self.folder.new_opfiles_info()
        files_names, new_files_names = self.process_files_paths(files_info["FilesInfo"])
        userdata = self.user.session_info()
        
        batch_info_followup = {"BatchID": bid,
                      "Aircraft": files_info["Aircraft"],
                      "Operator": files_info["Operator"],
                      "OriginalFilesName": files_names,
                      "OriginalFilesPath": self.conf["path_to_new_opfiles"],
                      "FilesID": new_files_names,
                      "AddedDate": self.func.current_date(),
                      "Responsible": "UNASSIGNED",
                      "Proofreader": "UNASSIGNED",
                      "ResponsibleStatus": "",
                      "ProofreaderStatus": "",
                      "OverallStatus": "UNASSIGNED",
                      "ChangesLog": "Batch added by {},".format(userdata["User"])} 
        
        batch_info_fileshistory = self.prepare_fileshistory_info(batch_info_followup, files_info)
        #Data for db is prepared now copy the files.
        self.copy_files_to_unassigned_prepared_dirs(batch_info_followup)    
        #Now the files a copied now insert data to database
        #Insert the batch
        self.db.create_row("followup", batch_info_followup)
        #Insert the file history
        for file_history in batch_info_fileshistory:
            self.db.create_row("fileshistory", file_history)

        return bid

    
    def followup_reversed(self):
        """Get followup table from db reverse it and return it as dict"""
        df = self.db.read_table("followup")
        df_dict = df.reindex(index=df.index[::-1]).to_dict('list')
        return df_dict


    def followup_for_responsible(self):
        """Get followup table from db reverse it filter it for current user and return it as dict"""
        userdata = self.user.session_info()
        df = self.db.select_row("followup", "Responsible", userdata["User"], asdict=False)
        df_dict = df.reindex(index=df.index[::-1]).to_dict('list')
        return df_dict

    def fileshistory_table(self):
        """Get file history table as dict by default"""
        return self.db.get_table("fileshistory")
    
    def get_batch(self, bid=""):
        """Get batch id if specified"""
        bid_data = self.db.select_row("followup", "BatchID", bid)
        data = {}
        for col, val in bid_data.items():
            data[col] = val[0]

        return data


    def bid_options(self, get_followup=False, get_filehistory=False):
        """Batch status options from config.json file"""
        
        batch_opt = {
            "status_user" : self.func.listify_string(self.conf["batch_status_options_responsible"]),
            "status_proofreader" : self.func.listify_string(self.conf["batch_status_options_proofreader"]),
            "status_overall" : self.func.listify_string(self.conf["batch_status_options_overall"]),
        }

        bid_data = self.func.read_json("batch.json")
        batch_opt.update(bid_data)
        batch_opt.update(self.user.context_disable())
        batch_opt.update({"users": self.user.get_users(), "proofreaders": self.user.get_proofreaders()})
        if get_followup:
            fup_data = self.followup_reversed()
            batch_opt.update(fup_data)
        if get_filehistory:
            hist_data = self.fileshistory_table()
            batch_opt.update(hist_data)

        return batch_opt       

    def data_mail_for_send_mail(self, newdata):
        """Send email between proofreader and responsible"""
        session = self.user.session_info()
        olddata = self.func.read_json("batch.json")
        
        if olddata["Responsible"] != "UNASSIGNED" and olddata["Proofreader"] != "UNASSIGNED":
            user_responsible = self.db.select_row("users", "User", olddata["Responsible"])
            user_proofreader = self.db.select_row("users", "User", olddata["Proofreader"])
            responsible_mail = user_responsible["Email"][0]
            proofreader_mail = user_proofreader["Email"][0]
        else:
            user_responsible = self.db.select_row("users", "User", newdata["Responsible"])
            user_proofreader = self.db.select_row("users", "User", newdata["Proofreader"])
            responsible_mail = user_responsible["Email"][0]
            proofreader_mail = user_proofreader["Email"][0]

            
        sender_email = session["Email"] 

        if self.conf["MAIL_PASSWORD"] == "":
            sender_password = session["Password"]
        else:
            sender_password = self.conf["MAIL_PASSWORD"]
    
        cols_of_interest = ["Responsible", "Proofreader", "ResponsibleStatus", "ProofreaderStatus", "ResponsibleComment", "ProofreaderComment"]

        mail_receiver, update_subject, update_message = "", "", ""

        for col in cols_of_interest:
            if col in list(newdata.keys()):
                if olddata[col] != newdata[col]:
                    update_subject = "{} {} {} UPDATE".format(olddata["Operator"], olddata["Aircraft"], olddata["BatchID"])
                    
                    if col == "Responsible":
                        if olddata["Responsible"] != newdata["Responsible"]:
                            mail_receiver = responsible_mail
                            update_message = "Hi there,\n\n\nYou({}) are now the responsible for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break
                    if col == "Proofreader":
                        if olddata["Proofreader"] != newdata["Proofreader"]:
                            mail_receiver = responsible_mail
                            update_message = "Hi there,\n\n\n{} is now the proofreader for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break
                    if col == "ResponsibleStatus":
                        if olddata["ResponsibleStatus"] != newdata["ResponsibleStatus"]:
                            mail_receiver = proofreader_mail
                            update_message = "Hi there,\n\n\nResponsible changed status to '{}' for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break
                    if col == "ProofreaderStatus":
                        if olddata["ProofreaderStatus"] != newdata["ProofreaderStatus"]:
                            mail_receiver = responsible_mail
                            update_message = "Hi there,\n\n\nProofreader changed status to '{}' for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break
                    if col == "ResponsibleComment":
                        if olddata["ResponsibleComment"] != newdata["ResponsibleComment"]:
                            mail_receiver = proofreader_mail
                            update_message = "Hi there,\n\n\nResponsible said '{}' for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break
                    if col == "ProofreaderComment":
                        if olddata["ProofreaderComment"] != newdata["ProofreaderComment"]:
                            mail_receiver = responsible_mail
                            update_message = "Hi there,\n\n\nProofreader said '{}' for batch {}\n\n\n\n\n\n\n\nThis is an automatic message sent by the Followup.".format(newdata[col], olddata["BatchID"])
                            break

        data = {"sender_email":sender_email,
                "sender_password":sender_password,
                "mail_receiver":mail_receiver,
                "update_subject": update_subject,
                "update_message":update_message}
        
        print(newdata, "\n\n", data)

        if update_subject != "":
            try:
                self.mail.send_mail(sender_email, sender_password, mail_receiver, update_subject, update_message)
            except Exception as err:
                errmsg = self.func.write_traceback(err)
                print(errmsg)
                print(data)
                raise Exception("Email cannot be sent! Please sent email to {} and inform him/her of what you did!".format(mail_receiver))




    def set_default_proofreader(self, data):
        """Update with the default proofreader for the given responsible if needed"""
        if "Responsible" in list(data.keys()):
            user_data = self.db.select_row("users", "User", data["Responsible"])
            data["Proofreader"] = user_data["Proofreader"][0]
            data["ResponsibleStatus"] = ""
            data["ProofreaderStatus"] = ""
            data["OverallStatus"] = "ONGOING"
            data["StartDate"] = self.func.current_date()
            bid_info = self.func.read_json("batch.json")
            data["ChangesLog"] = bid_info["ChangesLog"] + "\nAssigned to {} on {},".format(data["Responsible"], data["StartDate"])
            
            return data
        else:
            return data


    def clear_start_date(self, data):
        """If Status is STANDBY or UNRECORDABLE then clear start date"""
        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "UNRECORDABLE" or data["ProofreaderStatus"] == "STANDBY":
                data["StartDate"] = ""
                data["ImportedDateISAIM"] = ""
                data["TotalRowsNbr"] = ""
                data["MPDTaskRowsNbr"] = ""
                data["OperatorRowsNbr"] = ""
                data["FindingsRowsNbr"] = ""
                data["EstimatedTaskNbr"] = ""
                data["EstimatedFdgNbr"] = ""
            
            if data["ProofreaderStatus"] == "UNRECORDABLE":
                data["OverallStatus"] = "UNRECORDABLE"
            
            if data["ProofreaderStatus"] == "STANDBY":
                data["OverallStatus"] = "STANDBY"

        return data

    
    def dcs_info(self, dcspath):
        """Get xml info from the extracted xml from FE"""

        file = open(dcspath)
        tree = etree.parse(file)

        sumAll = tree.xpath('//sum')
        totalRows = sum([int(s.text) for s in sumAll])

        sumMpd = tree.xpath('//mpdTask//sum')
        mpdtask = sum([int(s.text) for s in sumMpd])

        sumOp = tree.xpath('//opeTask//sum')
        optask = sum([int(s.text) for s in sumOp])

        sumFindings = tree.xpath("//finding[@activated='true']//sum")
        findings = sum([int(s.text) for s in sumFindings])

        info_dcs = {"TotalRowsNbr": totalRows,
                "MPDTaskRowsNbr": mpdtask,
                "OperatorRowsNbr": optask,
                "FindingsRowsNbr": findings
                }

        return info_dcs
    
    
    def update_ifstatus_finished(self, data):
        """If Status is FINISHED update ImportedDateISAIM column"""
        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "FINISHED":
                data["ImportedDateISAIM"] = self.func.current_date()
                data["OverallStatus"] = "FINISHED"
        return data

    
    def update_ifstatus_toimport(self, data):
        """If ProofreaderStatus is To import then look for dcs info and update data"""
        
        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "TO BE IMPORTED":
                dcs_files = os.listdir(self.conf["path_to_dcs_info"])
                dcs_file = [f for f in dcs_files if data["BatchID"] in f]
                if len(dcs_file) == 1:
                    dcs_file_path = os.path.join(self.conf["path_to_dcs_info"], dcs_file[0])
                    dcs_result = self.dcs_info(dcs_file_path)
                    data.update(dcs_result)
                    return data
                else:
                    raise Exception("DCS file for batch '{}' not found!".format(data["BatchID"]))
            else:
                return data
        else:
            return data

    def alternate_status(self, data):
        """Set to empty the status of the proof or responsible when someone changed the status"""
        if "ProofreaderStatus" in list(data.keys()):
            data["ResponsibleStatus"] = ""
            data["OverallStatus"] = data["ProofreaderStatus"]
        if "ResponsibleStatus" in list(data.keys()):
            if data["ResponsibleStatus"] != "":
                data["ProofreaderStatus"] = ""
                data["OverallStatus"] = data["ResponsibleStatus"]
        return data 
        
    def process_status_batch_form(self, data):
        """Process dict from, form received from update_status page"""
        data = self.func.remove_null(data)
        if len(data) == 1:
            raise Exception("No enough data to process!")
        data = self.set_default_proofreader(data)
        data = self.clear_start_date(data)
        data = self.update_ifstatus_toimport(data)
        data = self.update_ifstatus_finished(data)
        data = self.alternate_status(data)
        #Move if needed the folders
        self.folder.move_prepfile_in_assigned(data) #assign
        self.folder.move_assigned_in_tbchecked(data) #to be checked
        self.folder.move_tobchecked_in_tbimported(data) #to be imported
        self.folder.move_tbimported_in_finished(data) #finished
        self.folder.move_tbchecked_in_assigned(data) #rework
        self.folder.move_tobchecked_in_standby(data) #standby
        self.folder.move_tobchecked_in_unrecordable(data) #unrecordable
        #Update database with data
        indb = self.db.update_row("followup", data, "BatchID")
        #write data mail for each status change
        try:
            self.data_mail_for_send_mail(data)
            mailsent = True
        except:
            mailsent = False
        return indb, mailsent

        

    def delete_batch_or_file(self, data):
        """Delete batch along with the files attached to it or a file from fileshistory"""
        
        if data["BatchID"] == "" and data["FileToDelete"] == "":
            fup = self.db.delete_row("followup", {"BatchID": data["DefaultBatchID"]})
            hist = self.db.delete_row("fileshistory", {"AddedInBatch": data["DefaultBatchID"]})
            if fup and hist:
                return True
            else:
                if fup == False:
                    raise Exception("Changes not saved in followup!")
                if hist == False:
                    raise Exception("Changes not saved in fileshistory!")
        if len(data["BatchID"]) > 0:
            fup = self.db.delete_row("followup", {"BatchID": data["BatchID"]})
            hist = self.db.delete_row("fileshistory", {"AddedInBatch": data["BatchID"]})
            if fup and hist:
                return True
            else:
                if fup == False:
                    raise Exception("Changes not saved in followup!")
                if hist == False:
                    raise Exception("Changes not saved in fileshistory!")
        if len(data["FileToDelete"]) > 0:
            valli = data["FileToDelete"].split("//") #Ex: ym3SGI//EIS-SM2K-SM180731.XML//189209
            colrow_dict = {"AddedInBatch": valli[0], "FileName": valli[1], "FileSize": valli[2]}
            if not self.db.delete_row("fileshistory", colrow_dict):
                raise Exception("Changes not saved in fileshistory!")


