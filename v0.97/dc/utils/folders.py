import os
from dc.utils.commun import Commun



class Folders:
    """Creation/manipulation of folders for this app"""

    cwd = os.getcwd()
    func = Commun()

    def create_needed_dirs(self):
        """Create the working directories if doesn't exist"""

        root_path = os.path.join(self.cwd, 'DC BATCHES IN WORK')

        sub_folders = ['0 NEW',
                    '1 UNASSIGNED',
                    '2 PREPARED FILES',
                    '3 ASSIGNED',
                    '4 TO BE CHECKED',
                    '5 TO BE IMPORTED',
                    '6 FINISHED',
                    '7 IN STANDBY',
                    '8 UNRECORDABLE']

        extraDirs = [root_path, 'excels exported', 'excels to be imported', 'FUDB', 'bin']

        for extradir in extraDirs:
            try:
                os.mkdir(extradir)
            except:
                pass

        for adir in sub_folders:
            subdir = os.path.join(root_path, adir)
            try:
                os.mkdir(subdir)
            except:
                pass



    def defaultconfig(self):
        """"Create default config.json file"""

        config_data = {
                "path_to_database": "FUDB/FOLLOWUP.DB",
                "path_to_frontend": "FUDB/",
                "path_to_dcs_info": "FUDB/",
                "path_to_bin": "bin/",
                "path_to_excels_exported_from_database": "excels exported/",
                "path_to_excels_to_be_imported_in_database": "excels to be imported/",
                "path_to_new_opfiles": "DC BATCHES IN WORK/0 NEW/",
                "path_to_batches_unassigned": "DC BATCHES IN WORK/1 UNASSIGNED/",
                "path_to_batches_prepfiles": "DC BATCHES IN WORK/2 PREPARED FILES/",
                "path_to_batches_assigned": "DC BATCHES IN WORK/3 ASSIGNED/",
                "path_to_batches_tobechecked": "DC BATCHES IN WORK/4 TO BE CHECKED/",
                "path_to_batches_tbimported": "DC BATCHES IN WORK/5 TO BE IMPORTED/",
                "path_to_batches_finished": "DC BATCHES IN WORK/6 FINISHED/",
                "path_to_batches_instandby": "DC BATCHES IN WORK/7 IN STANDBY/",
                "path_to_batches_unrecordable": "DC BATCHES IN WORK/8 UNRECORDABLE/",
                "batch_status_options_responsible": "PREP. OP FILE, IMPORTATION & SPLIT FILE, RELIABILITY & DATA UPGRADE, CHECK OP FILE, CHECK SPLIT FILE, CHECK FRONT END, **TO BE CHECKED",
                "batch_status_options_proofreader": "OP FILE OK, SPLIT FILE OK, FRONT END OK, **TO BE IMPORTED, **FINISHED, **REWORK, **STANDBY, **UNRECORDABLE",
                "batch_status_options_overall": "ONGOING, STANDBY, FINISHED, UNRECORDABLE",
                "aircrafts": "A300, A300-600, A310, A320, A330, A340, A350, A380",
                "split_batch_factor": "2, 3, 4, 5, 6, 7, 8, 9",
                "IDlentgh": "6",
                "port": "5000"
            }
        
        if not os.path.isfile(os.path.join(self.cwd, "config.json")):
            self.func.write_json(config_data, self.cwd, fname="config.json")



    def make_default_dirs(self):
        """Create default dirs and config.json if needed"""
        self.defaultconfig()
        self.create_needed_dirs()


    def db_exists(self):
        """Check if db exists in the path"""
        conf = self.func.config_info()
        return self.func.file_exists(conf["path_to_database"])

    
    def operator_aircraft_info(self, apath):
        """Get operator and aircraft info from the path given"""
        opfolder_path = apath.split("0 NEW")[-1]
        opfolder = opfolder_path.replace("/", "")
        opfolder = opfolder.replace("\\", "")
        opfolder = opfolder.split(" ")
        operator = opfolder[0].strip()
        aircraft = opfolder[1].strip()
        return operator, aircraft
            
    
    def get_files_info(self, files_paths):
        """Get files size and modification date in a dict"""
        
        files_info = {}      
        for file_path in files_paths:
            file_info = self.func.get_file_size_mtime(file_path)
            files_info[file_path] = file_info
        
        return files_info
        
    
    def new_opfiles_info(self):
        """Get info from new opfiles folders, files"""
        conf = self.func.config_info()
        new_folders = self.func.get_folders(conf["path_to_new_opfiles"])
        
        if len(new_folders) > 1 and len(new_folders) != 0:
            raise Exception("Only one folder must be in '0 NEW' folder!")
        else:
            folder = new_folders[0]            
            op, ac = self.operator_aircraft_info(folder)
            files = self.func.get_files(folder)
            files_info = self.get_files_info(files)

            opfiles_info = {
                "Path": folder,
                "Operator": op,
                "Aircraft": ac,
                "FilesInfo": files_info
            }

            return opfiles_info
                

    def bid_folder_name(self):
        """Ex: TCX 320 _WOVteA - remake the folder name of the batch"""
        bid_info = self.func.read_json("batch.json")
        folder_name = "{} {} _{}".format(bid_info["Operator"], bid_info["Aircraft"], bid_info["BatchID"]) 
        return folder_name

    
    def move_prepfile_in_assigned(self, data):
        """Move folder from prepared files to assigned folder"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()       

        if "Responsible" in list(data.keys()):
            prep_files = os.listdir(conf["path_to_batches_prepfiles"])
            if folder_name in prep_files:
                #Move folder from prepared to assgned
                src = os.path.join(conf["path_to_batches_prepfiles"], folder_name)
                dst = os.path.join(conf["path_to_batches_assigned"], folder_name)
                self.func.move_folder(src, dst)
                #Copy front end macro to assigned dir
                dir_feli = os.listdir(conf["path_to_frontend"])
                dir_feli = [f for f in dir_feli if f.endswith('.xlsm')]
                feFile = [f for f in dir_feli if 'BETA' not in f.upper()][0]
                fe_macro_path = os.path.join(conf["path_to_frontend"], feFile)
                fe_newpath = os.path.join(dst, "_{} {}".format(folder_name,  feFile))
                self.func.copy_file(fe_macro_path, fe_newpath)
                
                if not self.func.folder_exists(dst):
                    raise Exception("Folder {} not moved in '3 ASSIGNED'!".format(folder_name))
            else:
                raise Exception("Folder {} not found in '2 PREPARED FILES'!".format(folder_name))


    def move_assigned_in_tbchecked(self, data):
        """If ResponsibleStatus is X then move folder from src to dst"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  
        
        if "ResponsibleStatus" in list(data.keys()):
            if data["ResponsibleStatus"] == "TO BE CHECKED":
                files = os.listdir(conf["path_to_batches_assigned"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_assigned"], folder_name)
                    dst = os.path.join(conf["path_to_batches_tobechecked"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '4 TO BE CHECKED'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '3 ASSIGNED'!".format(folder_name))


    def move_tbchecked_in_assigned(self, data):
        """If ProofreaderStatus is X then move folder from src to dst"""   
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  

        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "REWORK":
                files = os.listdir(conf["path_to_batches_tobechecked"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_tobechecked"], folder_name)
                    dst = os.path.join(conf["path_to_batches_assigned"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '3 ASSIGNED'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '4 TO BE CHECKED'!".format(folder_name))
                    

    def move_tobchecked_in_tbimported(self, data):
        """If ProofreaderStatus is X then move folder from src to dst"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  

        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "TO BE IMPORTED":
                files = os.listdir(conf["path_to_batches_tobechecked"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_tobechecked"], folder_name)
                    dst = os.path.join(conf["path_to_batches_tbimported"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '5 TO BE IMPORTED'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '4 TO BE CHECKED'!".format(folder_name))
                


    def move_tbimported_in_finished(self, data):
        """If ProofreaderStatus is X then move folder from src to dst"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  

        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "FINISHED":
                files = os.listdir(conf["path_to_batches_tbimported"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_tbimported"], folder_name)
                    dst = os.path.join(conf["path_to_batches_finished"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '6 FINISHED'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '5 TO BE IMPORTED'!".format(folder_name))


    def move_tobchecked_in_standby(self, data):
        """If ProofreaderStatus is X then move folder from src to dst"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  

        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "STANDBY":
                files = os.listdir(conf["path_to_batches_tobechecked"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_tobechecked"], folder_name)
                    dst = os.path.join(conf["path_to_batches_instandby"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '7 IN STANDBY'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '4 TO BE CHECKED'!".format(folder_name))


    def move_tobchecked_in_unrecordable(self, data):
        """If ProofreaderStatus is X then move folder from src to dst"""
        conf = self.func.config_info()
        folder_name = self.bid_folder_name()  

        if "ProofreaderStatus" in list(data.keys()):
            if data["ProofreaderStatus"] == "UNRECORDABLE":
                files = os.listdir(conf["path_to_batches_tobechecked"])
                if folder_name in files:
                    src = os.path.join(conf["path_to_batches_tobechecked"], folder_name)
                    dst = os.path.join(conf["path_to_batches_unrecordable"], folder_name)
                    self.func.move_folder(src, dst)

                    if not self.func.folder_exists(dst):
                        raise Exception("Folder {} not moved in '8 UNRECORDABLE'!".format(folder_name))
                else:
                    raise Exception("Folder {} not found in '4 TO BE CHECKED'!".format(folder_name))
    


