
def createAssignedDirFiles(unassignedBatch):
    import os, re, shutil
    from fup.utils.jsoninfo import configInfo, sessionInfo
    from fup.utils.commun import getfilespath_from, deletetree
    config = configInfo()
    session = sessionInfo()
    user = session['current_user_working']
    if re.search('@', user):
        user = user.split('@')[0]

    dir_unassigned = config["path_to_batches_prepfiles"] #changed from unassigned path to prepfiles path
    dir_assigned = config['path_to_batches_assigned']
    dir_frontend = config['path_to_frontend']
    dir_feli = os.listdir(dir_frontend)
    dir_feli = [f for f in dir_feli if re.search('.xlsm', f)]
    dir_feFile = [f for f in dir_feli if not re.search('BETA', f.upper())]
    dir_bidli = os.listdir(dir_unassigned)

    try:
        for biddir in dir_bidli:
            if re.search(unassignedBatch, biddir):
                #Get the unassigned and assigned folders paths
                opfile_dirunassigned = os.path.join(dir_unassigned, biddir)
                opfile_dirassigned = os.path.join(dir_assigned, str(user+'-'+biddir))
                #Make a new directory in the Assigned folder
                os.mkdir(opfile_dirassigned)
                #Copy the FE macro to the folder created
                fepathfile = os.path.join(dir_frontend, dir_feFile[0])
                shutil.copy2(fepathfile, opfile_dirassigned)
                #Create also here the OP FILE folder and copy here the files from unassigned
                opfilepath = os.path.join(opfile_dirassigned, 'OP FILE')
                os.mkdir(opfilepath)
                org_filesli = getfilespath_from(opfile_dirunassigned)
                org_files = [f for f in org_filesli if not re.search('Thumbs.db', f)]
                for file in org_files:
                    shutil.copy2(file, opfilepath)

                #Rename the FE macro
                filesinassigned = os.listdir(opfile_dirassigned)
                fenameold = [f for f in filesinassigned if re.search('.xlsm', f)][0]
                fefileold = os.path.join(opfile_dirassigned, fenameold)
                fenamenew = unassignedBatch+'-'+fenameold
                fefilenew = os.path.join(opfile_dirassigned, fenamenew)
                os.rename(fefileold, fefilenew)
                #delete the dir from prep files folder
                deletetree(os.path.join(dir_unassigned, biddir))

        return True

    except Exception as e:
        print("GOT: ", e)
        return False





def mergeDirBatches(batchidstrli):
    import os, re, shutil, time
    from fup.utils.commun import copytree, generateID, listifyString
    from fup.utils.jsoninfo import configInfo, sessionInfo
    config = configInfo()
    session = sessionInfo()
    try:
        user = session['current_user_working']
        if re.search('@', user):
            user = user.split('@')[0]

        batchidli = listifyString(batchidstrli)

        dir_assigned = config['path_to_batches_assigned']
        dirs_assigned = os.listdir(dir_assigned)

        #Make a dir for the merged batches
        mergedID = generateID()
        mergeddirpath = os.path.join(dir_assigned, '{}-___ A___ BID_{}'.format(user, mergedID))
        os.mkdir(mergeddirpath)

        #Get names of the folders from Assigned folder by checking the BID
        dirstomergeli = []
        for batchid in batchidli:
            dir_bidAssigned = [d for d in dirs_assigned if re.search(batchid, d)]
            dirstomergeli.append(dir_bidAssigned[0])

        #Copy contents of the old batches into the new created merged folder
        for folderName in  dirstomergeli:
            assignedPathOld = os.path.join(dir_assigned, folderName)
            src, dst = assignedPathOld, mergeddirpath
            copytree(src, dst, symlinks=False, ignore=None)
            files_not_deleted = True
            while files_not_deleted:
                try:
                    shutil.rmtree(assignedPathOld) #delete folders
                    files_not_deleted = False
                except:
                    print("Please close file(s) open in folder {}".format(assignedPathOld))
                    time.sleep(2)
                    

        mergedInfodict = {'mergedID': mergedID,
                          'mergeddirpath': mergeddirpath,
                          'batchidli': batchidli
                         }
        return mergedInfodict
    except Exception as e:
        print('mergeDirBatches/helpers Got :', e)
        return False



def createSplitDirs(splitFactor, batchid):
    import os, re, shutil
    from fup.utils.commun import copytree, deletetree, generateID
    from fup.utils.jsoninfo import configInfo
    from fup.helpers.batch import batchExists
    config = configInfo()

    if batchExists(batchid) == False:
        return False

    #Get path to ASSIGNED and filer by BID
    dir_assigned = config['path_to_batches_assigned']
    dirs_assigned = os.listdir(dir_assigned)
    dir_bidAssigned = [d for d in dirs_assigned if re.search(batchid, d)]
    if len(dir_bidAssigned) == 0:
        return False

    #Copy the main directory in the range of the splitFactor
    assignedPathOld = os.path.join(dir_assigned, dir_bidAssigned[0])

    oldDirName = dir_bidAssigned[0]
    respNameAC = ' '.join(oldDirName.split(' ')[0:-1])

    newSplitpathsd = {}
    idli = []
    for splitedID in range(splitFactor):
        newid = generateID()
        newdirName = respNameAC + ' BID_' + newid
        assignedPathNew = os.path.join(dir_assigned, newdirName)
        src, dst = assignedPathOld, assignedPathNew
        copytree(src, dst, symlinks=False, ignore=None)
        newSplitpathsd[newdirName] = assignedPathNew
        idli.append(newid)

    newSplitpathsd['newids'] = ', '.join(idli)
    newSplitpathsd['oldid'] = batchid

    deletetree(assignedPathOld)

    return newSplitpathsd


def moveDirName(dirName, cfg_olddir, cfg_newdir):
    #Move a folder from one path to another, delete the old one
    import os, re, shutil
    from fup.utils.commun import copytree, deletetree
    from fup.utils.jsoninfo import configInfo

    try:
        config = configInfo()
        olddir = config[cfg_olddir]
        newdir = config[cfg_newdir]

        dirtobeMoved = os.listdir(olddir)
        dir_bidtbMoved = [d for d in dirtobeMoved if re.search(dirName, d)]

        pathOld = os.path.join(olddir, dir_bidtbMoved[0])

        pathNew = os.path.join(newdir, dir_bidtbMoved[0])

        src, dst = pathOld, pathNew
        copytree(src, dst, symlinks=False, ignore=None)

        deletetree(pathOld)
        return True
    except:
        return False




def moveDirsforUpdate(infoBatchdict):
    import os, re
    from fup.helpers.batchdirs import moveDirName
    from fup.utils.jsoninfo import configInfo
    from fup.helpers.files import dcsinfo
    from fup.utils.dbwrap import sql_updateDict
    from fup.utils.commun import current_date

    #infoBatchdict = {'ResponsibleStatus': 'TO BE CHECKED', 'BatchID': 'VqUSKc'}
    batchid = infoBatchdict['BatchID']
    config = configInfo()

    for kcol, val in infoBatchdict.items():
        #print(kcol, val)
        if kcol == 'ResponsibleStatus' and val == 'TO BE CHECKED':
            ok = moveDirName(batchid, "path_to_batches_assigned", "path_to_batches_tobechecked")
            if ok:
                return True
            else:
                print("[info]Batch {} not found in ASSIGNED folder".format(batchid))
                return False

        elif kcol == 'ProofreaderStatus' and val == 'REWORK':
            ok = moveDirName(batchid, "path_to_batches_tobechecked", "path_to_batches_assigned")
            if ok:
                return True
            else:
                print("[info]Batch {} not found in TO BE CHECKED folder".format(batchid))
                return False

        elif kcol == 'ProofreaderStatus' and val == 'STANDBY':
            ok = moveDirName(batchid, "path_to_batches_tobechecked", "path_to_batches_instandby")
            if ok:
                return True
            else:
                print("[info]Batch {} not found in TO BE CHECKED folder".format(batchid))
                return False

        elif kcol == 'ProofreaderStatus' and val == 'UNRECORDABLE':
            ok = moveDirName(batchid, "path_to_batches_tobechecked", "path_to_batches_unrecordable")
            if ok:
                return True
            else:
                print("[info]Batch {} not found in TO BE CHECKED folder".format(batchid))
                return False

        elif kcol == 'ProofreaderStatus' and val == 'TO BE IMPORTED':
            try:
                dcspath = config['path_to_dcs_info']
                dcsli = os.listdir(dcspath)
                dcsli = [f for f in dcsli if re.search(batchid, f)]
                dcsli = [f for f in dcsli if re.search('DCS', f)]
                dcsli = [f for f in dcsli if re.search('.xml', f)]

                dcsfilepath = os.path.join(dcspath, dcsli[0])
                dcsdictinfo = dcsinfo(dcsfilepath)
                dcsdictinfo['BatchID'] = batchid

                if sql_updateDict('followup', dcsdictinfo, 'BatchID') == False:
                    print("Cannot update the DCS information to database!")
                    return False

                ok =  moveDirName(batchid, "path_to_batches_tobechecked", "path_to_batches_tbimported")
                if ok:
                    return True
                else:
                    print("Batch {} not found in TO BE CHECKED folder".format(batchid))
                    return False
            except:
                print('Cannot open/read the DCS xml file!')
                return False


        elif kcol == 'ProofreaderStatus' and val == 'FINISHED':
            ok = moveDirName(batchid, "path_to_batches_tbimported", "path_to_batches_finished")
            if ok:
                cdate = current_date()
                importedDatedict = {'BatchID': batchid, 
                                    'ImportedDateISAIM': cdate,
                                    'ResponsibleStatus': 'FINISHED'
                                    }
                sql_updateDict('followup', importedDatedict, 'BatchID')
            else:
                print("Batch {} not found in TO BE IMPORTED folder".format(batchid))
                return False



def renameAssgnDir(dictInfo):
    import os, re
    from fup.utils.jsoninfo import configInfo
    
    newuser = dictInfo["Responsible"]
    bid = dictInfo["BatchID"]

    config = configInfo()
    dir_assigned = config['path_to_batches_assigned']
    dir_assignedli = os.listdir(dir_assigned)

    dirtoRename = [d for d in dir_assignedli if re.search(bid, d)]

    if len(dirtoRename) == 1:
        originalDirName = dirtoRename[0]
        dhead = newuser
        dtail = originalDirName.split('-')[1]
        newBatchdirName = dhead+'-'+dtail
        src = os.path.join(dir_assigned, originalDirName)
        dst = os.path.join(dir_assigned, newBatchdirName)
        try:
            os.rename(src, dst)
        except:
            print('Cannot rename{} to {}'.format(src, dst))
            return False
        return True
    else:
        return False




































#
