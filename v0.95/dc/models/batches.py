import os
import pandas as pd
from dc.utils.commun import Commun
from dc.utils.dbwrap import Dbwrap
from dc.utils.folders import Folders
from dc.models.users import User


class Batches:

    func = Commun()
    conf = func.config_info()
    db = Dbwrap(conf["path_to_database"])
    folder = Folders()
    user = User()

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
                      "ResponsibleStatus": "UNASSIGNED",
                      "ProofreaderStatus": "UNASSIGNED",
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

    def get_batch(self, bid=""):
        """Get batch id if specified"""
        bid_data = self.db.select_row("followup", "BatchID", bid)
        data = {}
        for col, val in bid_data.items():
            data[col] = val[0]

        return data



    def bid_options(self):
        """Batch status options from config.json file"""
        
        batch_opt = {
            "status_user" : self.func.listify_string(self.conf["batch_status_options_responsible"]),
            "status_proofreader" : self.func.listify_string(self.conf["batch_status_options_proofreader"]),
            "status_overall" : self.func.listify_string(self.conf["batch_status_options_overall"]),
            "aircrafts" : self.func.listify_string(self.conf["aircrafts"]),
            "split_batch_factor" : self.func.listify_string(self.conf["split_batch_factor"]),
        }

        disable_data = self.user.context_disable()

        try:
            bid_data = self.func.read_json("batch.json")
            batch_opt.update(bid_data)
            batch_opt.update(disable_data)
        except:
            print("batch.json not found")
            pass

        
        return batch_opt


    def process_status_batch_form(self, data):
        """Process dict from form received from update_status page"""
        data = self.func.remove_null(data)
        return self.db.update_row("followup", data, "BatchID")