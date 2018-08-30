
#Check for duplicates
def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

def checklifor_dups(ali):
    from fup.helpers.files import list_duplicates

    if len(ali) != len(set(ali)):
        dupsli = list_duplicates(ali)
        return dupsli
    else:
        return []


def checkNew():
    """Check if folder from new contain only files and no duplicates"""

    import os
    from fup.utils.jsoninfo import configInfo
    from fup.helpers.files import checklifor_dups

    config = configInfo()

    newFilesPath = config["path_to_new_opfiles"]
    newFilesPath = os.path.abspath(newFilesPath)
    newFiles = os.listdir(newFilesPath)

    opacli = []
    for folderName in newFiles:
        folderNameli = folderName.split(' ')
        nameli = [f.strip() for f in folderNameli]
        op = str(nameli[0])
        ac = str(nameli[1].replace('A', ''))
        opac = str(op+' '+ac)
        opacli.append(opac)
    
    dupsli = checklifor_dups(opacli)
    
    errtxt_path = os.path.join(newFilesPath, "Keep only files in these folders.txt")
    try:
        os.remove(errtxt_path)
    except:
        pass
    
    if len(dupsli) > 0:
        errtxt = open(errtxt_path, "a")
        errtxt.write("\n\nPlease delete duplicate Operator + AC mentioned below:\n\n\n")
        for folder in dupsli:
            errtxt.write(str(folder+"\n\n"))
            
        errtxt.write("\n\n\nFound {} folders/files which are not conform.\nRead the guideline for info about to proceeed next.".format(len(dupsli)))
        errtxt.close()
        msg = str("Please don't keep DUPLICATES in NEW folder (Like: TCX 300/TCX A300)! Check file 'Keep only files in these folders.txt' to correct the issue. Found {} folders not ok".format(len(dupsli)))
        return msg

    
    dirli = []
    for folder in newFiles:
        folderPath = os.path.join(newFilesPath, folder)

        if not os.path.isdir(folderPath):
            dirli.append(folder)
            continue
        
        if not len(folder.split(' ')) == 2:
            dirli.append(folder)
            continue
            
        files = os.listdir(folderPath)
        for file in files:
            filePath = os.path.join(folderPath, file)
            if file == "Thumbs.db":
                try:
                    os.remove(filePath)
                except:
                    msg = str("Please delete manually this {}".format(filePath))
                    return msg ,'', ''
            if os.path.isdir(filePath):
                dirli.append(folderPath)

    dirli = list(set(dirli))   
    

    if len(dirli) > 0:
        
        errtxt = open(errtxt_path, "a")
        errtxt.write("\n\nFolders must contain ONLY FILES\nThe shoulnd't be any files in 0 NEW\nMove/process bellow mentioned folders/files:\n\n\n\n")
        for d in dirli:
            folder = str(d).split("0 NEW")[-1].replace('\\', '')
            errtxt.write(str(folder+"\n\n"))
        errtxt.write("\n\n\nFound {} folders/files which are not conform.\nRead the guideline for info about to proceeed next.".format(len(dirli)))
        errtxt.close()
        msg = "Please keep ONLY FILES in NEW folder! Check file 'Keep only files in these folders.txt' to correct the issue. Found {} folders not ok".format(len(dirli))
        return str(msg)





def autoNewDirs():

    #do a check before generating batches

    resultCheckNew = checkNew() 
    if isinstance(resultCheckNew, str):
        return resultCheckNew, '', ''

    import os, shutil
    from fup.helpers.files import originalFilesPaths, getfileSizeMtime
    from fup.utils.commun import generateID, current_date
    from fup.utils.jsoninfo import configInfo
    

    config = configInfo()
    bindir = os.path.abspath(config["path_to_bin"])

    filesinfodict = originalFilesPaths(infoDict={}, auto=True)
    
    #print('filesinfodict', str(filesinfodict).encode("utf-8"))

    newdirsNames = list(filesinfodict.keys())
    unassignedpath = os.path.abspath(config['path_to_batches_unassigned'])
    unassigneddirli = os.listdir(unassignedpath)

    unsdict = {}
    for d in unassigneddirli:
        commName = d.split('BID_')[0].strip()
        unsdict[commName] = d

    unassigneddirNames = list(unsdict.keys())
    communliBatch = list(set(newdirsNames).intersection(unassigneddirNames))

    auto = False
    infoDictli = []
    tobinli = []
    for opac, vdict in filesinfodict.items():
        #similar to uploadFilesCreateBatch, but without flask file object
        print("Operator - Aircraft: ", opac)
        batchID = generateID()
        operator = opac.split(' ')[0]
        aircraft = opac.split(' ')[1]
        bindir_batch = os.path.join(bindir, batchID)

        if opac not in communliBatch:
            batchNameFolder = operator+' '+ aircraft +' BID_'+batchID
            path = os.path.join(unassignedpath, batchNameFolder)
            os.mkdir(path)
        else:
            auto = True
            communOpAc = list(set([opac]).intersection(communliBatch))
            batchNameFolder = unsdict[communOpAc[0]]
            path = os.path.join(unassignedpath, batchNameFolder)

            existingBatchID = batchNameFolder.split('BID_')[-1].replace('_', '')
            bindir_batch = os.path.join(bindir, existingBatchID)

        tobinli.append({'source': vdict['rootpath'], 'destination': bindir_batch})

        filesnameli = []
        fileIDli = []

        for filepath in vdict['files']:
            if auto:
                fileinfo = getfileSizeMtime(filepath)
                #print("autoNewDirs: getfileSizeMtime, fileinfo> ", fileinfo)
                fileinfo["FileName"] = filepath.split("\\")[-1]
                responseFileInfo = checkFileInfo(fileinfo)
                if responseFileInfo != True:
                    return responseFileInfo, auto, auto
            filename = filepath.split('\\')[-1]
            #print("autoNewDirs: filename> ", filename, file)
            fileid = generateID()
            newFileName = 'FID_'+fileid+' '+filename
            save_path = os.path.join(path, newFileName)

            try:
                shutil.copy2(filepath, save_path)
                filesnameli.append(filename)
                fileIDli.append(fileid)
            except Exception as e:
                errmsg = "Make sure that all folders from NEW contains ONLY FILES! Got: {}".format(str(e))
                return str(errmsg), str(e), str(e)

        orgfilesname = ', '.join(filesnameli)
        orgfilespath = path
        filesId = ', '.join(fileIDli)
        addedDate = current_date()


        infoaddDict =  {'BatchID': batchID,
                        'Aircraft': aircraft,
                        'Operator': operator,
                        'OriginalFilesName': orgfilesname,
                        'OriginalFilesPath': orgfilespath,
                        'FilesID': filesId,
                        'AddedDate': addedDate
                        }

        infoDictli.append(infoaddDict)

    print("yuhuuu infoDictli, auto, tobinli", infoDictli, auto, tobinli)
    return infoDictli, auto, tobinli



def originalFilesPaths(infoDict, auto=False):
    import os, re
    from fup.utils.commun import getDirs
    from fup.utils.jsoninfo import configInfo

    

    config = configInfo()

    newFilesPath = config["path_to_new_opfiles"]
    newFilesPath = os.path.abspath(newFilesPath)
    orgdirli = os.listdir(newFilesPath)

    if auto:
        orgdirs = [os.path.join(newFilesPath, adir) for adir in orgdirli]
        orgdirs = getDirs(orgdirs)

        dirsdict = {}
        for path in orgdirs:
            try:
                #print(path)
                op = path.split('\\')[-1].split(' ')[0].strip()
                ac = str(path.split('\\')[-1].split(' ')[1].strip())
                if not re.search('A', ac):
                    ac = 'A'+ac
                opac = op+' '+ac
                infoDict['Operator'] = op
                infoDict['Aircraft'] = ac
                filespath = originalFilesPaths(infoDict, auto=False) #recursive
                dirsdict[opac] = {'files': filespath, 'rootpath':path}
                #print(dirsdict[opac])
            except Exception as e:#in case there is no op or ac
                #print("originalFilesPaths", str(e))
                pass

        #print(dirsdict)
        return dirsdict

    else:
        #Get original files paths to the new files added to batch
        try:
            orgdirli = [p for p in orgdirli if re.search(infoDict['Operator'], p)]
            orgdirli = [p for p in orgdirli if re.search(infoDict['Aircraft'], p) or re.search(infoDict['Aircraft'][1:], p)]
        except:
            response = "Can't collect Operator and Aircraft info.."
            return response

        if len(orgdirli) == 1:
            orgdir = orgdirli[0]
        else:
            response = "Operator '{}' with Aircraft '{}' was not found in NEW folder or possible duplicate!".format(infoDict['Operator'], infoDict['Aircraft'])
            return response

        orgpath = os.path.join(newFilesPath, orgdir)
        filespath = [os.path.join(orgpath, filepath) for filepath in os.listdir(orgpath)]
        #print('asd',filespath)

        return filespath




def matchOriginalinNew(orgfiles, newfiles):
    #take 2 lists and see if original is found in new, return a dict
    import re
    fid_pattern = r"^FID_[a-zA-Z0-9]{6}\n*"
    
    newfilesdict = {}
    for file in newfiles:
        if re.match(fid_pattern, file):
            fid = str(re.search(fid_pattern, file).group()).replace('FID_', '')
            fileName = str(file.replace(str('FID_' + fid), '')).strip()
            #print("fid, file ", fid, fileName)
            newfilesdict[fid] = fileName

    return newfilesdict

    


def getFileId(filepath, matchedFilesdict):
    from fup.utils.commun import delPunctuationMarks
    
    file = filepath.split('\\')[-1]
    #print('getFileIdfunc: ', file, matchedFilesdict)
    for kid, vfname in matchedFilesdict.items():
        if delPunctuationMarks(vfname) == delPunctuationMarks(file):
            #print(kid, vfname)
            return kid, vfname





def getfileSizeMtime(filepath):
    import os, time
    from time import mktime
    from datetime import datetime
    try:
        #print("getfileSizeMtime: ", filepath)
        metadata = os.stat(filepath)
        file_size = str(metadata.st_size) # bytes
        filetime = time.localtime(metadata.st_mtime)
        dt = datetime.fromtimestamp(mktime(filetime))
        creation_date = dt.strftime('%d-%m-%Y')
    except Exception as e:
        errmsg = str("Can't get Size and Time for this file {}\nGot erorr: {}".format(filepath, str(e)))
        #print("error on getfileSizeMtime: ", filepath, errmsg)
        return errmsg

    fileinfodict = {'FileSizeBytes':file_size,
                    'ModificationDate': creation_date
                    }

    return fileinfodict


def checkFileInfo(fileinfo):
    import re
    import pandas as pd
    from fup.utils.dbwrap import sql2df
    from fup.helpers.files import delDirsnotindb
    from fup.utils.commun import delPunctuationMarks

    #print("fileinfo ",fileinfo)

    histdf = sql2df('fileshistory')

    filedict = {}
    for k, v in fileinfo.items():
        filedict[k] = [v]

    filedf = pd.DataFrame.from_dict(filedict)
    #print("yuhuu filedict", filedict)

    merged_name = filedf.merge(histdf, left_on=['FileName'], right_on=['FileName'], suffixes=('', '_y'))
    colstodel = [col for col in merged_name.columns.tolist() if re.search('_y', col)]
    for col in colstodel:
        merged_name.drop(col, axis=1, inplace=True)

    merged_size = filedf.merge(histdf, left_on=['FileSizeBytes'], right_on=['FileSizeBytes'], suffixes=('', '_y'))
    colstodel = [col for col in merged_size.columns.tolist() if re.search('_y', col)]
    for col in colstodel:
        merged_size.drop(col, axis=1, inplace=True)

    merged_mtime = filedf.merge(histdf, left_on=['ModificationDate'], right_on=['ModificationDate'], suffixes=('', '_y'))
    colstodel = [col for col in merged_mtime.columns.tolist() if re.search('_y', col)]
    for col in colstodel:
        merged_mtime.drop(col, axis=1, inplace=True)

    if (merged_name.shape[0] == 0):
        return True
    elif (merged_name.shape[0] == 0) and (merged_size.shape[0] == 0):
        return True
    elif (merged_name.shape[0] == 0) and (merged_size.shape[0] == 0) and (merged_mtime.shape[0] == 0):
        return True
    else:
        try:
            filename_merge = merged_name['FileName'].tolist()[0]

            for fname in histdf['FileName']:

                if delPunctuationMarks(fname) == delPunctuationMarks(filename_merge):

                    histdf_filtered = histdf[histdf['FileName'] == fname]

                    filename_hist = histdf_filtered['FileName'].tolist()
                    batchid_hist = histdf_filtered['AddedInBatch'].tolist()
                    fileid_hist = histdf_filtered['FileID'].tolist()

                    delDirsnotindb()

                    response = "File '{}' was probably added before! Check BID_{}, FID_{}".format(filename_hist[0], batchid_hist[0], fileid_hist[0])
                    #print(response)
                    return response
        except Exception as e:
            return str("Probably files in NEW are already inserted. Got: {}".format(e))



def delDirsnotindb():
    import os
    from fup.utils.jsoninfo import configInfo
    from fup.utils.commun import deletetree
    from fup.helpers.batch import batchExists

    config = configInfo()
    unassignedpath = os.path.abspath(config['path_to_batches_unassigned'])
    unassigneddirli = os.listdir(unassignedpath)

    todelDirs = {}
    for batchNameFolder in unassigneddirli:
        bid = batchNameFolder.split('BID_')[-1].replace('_', '')
        if batchNameFolder == '_info.txt': 
            continue
        if not batchExists(bid):
            todelDirs[bid] = batchNameFolder

    for kbid, vdirName in todelDirs.items():
        deldir = os.path.join(unassignedpath, vdirName)
        deletetree(deldir)


def updateDBforNewFiles():
    #Verify if new files were added to a existing batch if so, update db
    import os, re
    import pandas as pd
    from fup.utils.dbwrap import sql_insertDict, sql_updateDict, get_dftable, sql_deleteRow
    from fup.helpers.batch import batchInfo
    from fup.helpers.files import getfileSizeMtime
    from fup.utils.commun import list_duplicates

    #Update followup with the new file added to the batch

    followupdf = get_dftable('followup')
    orgpaths = followupdf['OriginalFilesPath'].tolist()
    orgpaths_nodups = list(set(orgpaths))

    newtempbid = {}
    for opath in orgpaths_nodups:
        bid = opath.split("\\")[-1].split('BID_')[-1].strip()

        followupdf_bid = followupdf[followupdf['OriginalFilesPath'].str.contains('|'.join([bid]), na=False)]

        bids = followupdf_bid["BatchID"].tolist()
        bidtodelli = [b for b in bids if b != bid]

        tempd = {}
        for biddel in bidtodelli:
            infobatch_previous = batchInfo(biddel)
            if infobatch_previous != False:
                for k in list(infobatch_previous.keys()):
                    if k not in ['OriginalFilesName', 'FilesID', 'ChangesLog', 'BatchID']:
                        infobatch_previous.pop(k, None)
                tempd["prevInfo"] = infobatch_previous
            # else:
            #     response_notfound = "BatchID {} is not in database! Please delete from unassigned folder {}!".format(existingBatchID, existingBatchID)
            #     tempd["prevInfo"] = response_notfound
            #     #return response_notfound, response_notfound, response_notfound

            newtempbid[bid] = tempd

    orgpaths_dups = list_duplicates(orgpaths)

    existingbid = {}
    for opath in orgpaths_dups:
        tempd = {}
        bid = opath.split("\\")[-1].split('BID_')[-1].strip()

        infobatch_previous = batchInfo(bid)
        if infobatch_previous != False:
            for k in list(infobatch_previous.keys()):
                if k not in ['OriginalFilesName', 'FilesID', 'ChangesLog', 'BatchID']:
                    infobatch_previous.pop(k, None)
            #print('OK ',infobatch_previous)
            tempd["prevInfo"] = infobatch_previous
        # else:
        #     response_notfound = "BatchID {} is not in database! Please delete from unassigned folder {}!".format(existingBatchID, existingBatchID)
        #     #print('NOK ',response_notfound)
        #     tempd["prevInfo"] = response_notfound
        #     #return response_notfound, response_notfound, response_notfound

        existingbid[bid] = tempd


    tempbidtodel = []
    for bidorg, dorg in existingbid.items():
        for bidtemp, dtemp in newtempbid.items():
            if bidorg == bidtemp:
                #make df from dict
                dforg = pd.DataFrame.from_dict(dorg['prevInfo']) 
                dftemp = pd.DataFrame.from_dict(dtemp['prevInfo'])

                todelli = dftemp['BatchID'].tolist()
                for b in todelli:
                    tempbidtodel.append(b)

                bidtodelli = list(set(tempbidtodel))

                dfconcat = pd.concat([dforg, dftemp], axis=0)
                dfdict = dfconcat.to_dict('list')

                #Create dict to update followup
                joineddict = {}
                for kcol, vrow in dfdict.items():
                    if kcol == "BatchID":
                        vrow = list(set(vrow).difference(set(bidtodelli)))
                    try:
                        li = list(set(filter(None, vrow)))
                        vrow = ', '.join(li)
                    except:
                        pass

                    joineddict[kcol] = vrow

                if sql_updateDict('followup', joineddict, 'BatchID') == False:
                    updatefup_failed = "Update in followup failed for BID_{} file {}..".format(joineddict['BatchID'], joineddict['OriginalFilesName'])
                    #print(updatefup_failed)
                    return updatefup_failed
                #Delete new temp bid from db
                for bid in bidtodelli:
                    if sql_deleteRow('followup', 'BatchID', bid):
                        pass
                    else:
                        #print("NOK")
                        return "Please delete from database {}".format(str(bidtodelli))


    #Update fileshistory table in db

    fileshistorydf = get_dftable('fileshistory')

    fileInfoli = []
    for fpath in orgpaths_nodups:
        fileInfo = {}
        bid = fpath.split("\\")[-1].split('BID_')[-1].strip()
        fhistdf_filtered = fileshistorydf[fileshistorydf["AddedInBatch"] == bid]
        fids = fhistdf_filtered["FileID"].tolist()
        files = os.listdir(fpath)

        fidorgli = []
        for file in files:
            fidorg = file.split(' ')[0].split('_')[-1]
            fidorgli.append(fidorg)

        newfid = list(set(fids).symmetric_difference(set(fidorgli))) # difference of/from 2 lists [1,2] and [1,2,3] => [3]

        #print(newfid)

        newfilepathli = []
        for fid in newfid:
            for file in files:
                if fid == file.split(' ')[0].split('_')[-1]:
                    #print(fid, file)
                    newfilepath = os.path.join(fpath, file)
                    newfilepathli.append(newfilepath)

            for newfilepath in newfilepathli:
                fileSpec = getfileSizeMtime(newfilepath)    
                fileName = ' '.join(newfilepath.split('\\')[-1].split(' ')[1:])
                fileInfo = {'FileID': newfid, 
                            'AddedInBatch': [bid], 
                            'ModificationDate': [fileSpec['ModificationDate']], 
                            'FileName': [fileName], 
                            'FileSizeBytes': [fileSpec['FileSizeBytes']]}

                fileInfoli.append(fileInfo)

    for finfodict in fileInfoli:
        if sql_insertDict('fileshistory', finfodict) == False:
            return "Please update manually in fileshistory {}".format(str(finfodict))
            #print("update manually")


    #print("return True")
    return True





def saveFilesInfo(infoDict, auto):
    import os
    import pandas
    from fup.helpers.files import getfileSizeMtime, matchOriginalinNew, getFileId, originalFilesPaths, checkFileInfo, updateDBforNewFiles
    from fup.utils.dbwrap import sql_insertDict, sql2df
    from fup.utils.commun import deletetree

    path = infoDict['OriginalFilesPath']
    #print("yuhuu ",path)

    newfiles = os.listdir(path)

    orgfilespath = originalFilesPaths(infoDict)
    if isinstance(orgfilespath, str):
        return orgfilespath #response

    orgfiles = [path.split('\\')[-1] for path in orgfilespath]

    matchedFiles = matchOriginalinNew(orgfiles, newfiles)

    for filepath in orgfilespath:
        fileinfo = getfileSizeMtime(filepath)
        fileinfo['FileID'], fileinfo['FileName'] = getFileId(filepath, matchedFiles)
        fileinfo['AddedInBatch'] = infoDict['BatchID']
        responseFileInfo = checkFileInfo(fileinfo)
        #print(filepath)
        if responseFileInfo != True:
            deletetree(path)
            return responseFileInfo

        else:
            if auto:
                pass
            else:
                if sql_insertDict('fileshistory', fileinfo) == False:
                    return False
    
    return True


def unassignedtoPrepfiles():
    #Copy batches from UNASSIGNED to PREPARED FILES 
    import re, os, shutil
    from fup.utils.jsoninfo import configInfo
    from fup.utils.commun import copytree

    config = configInfo()

    unassignedpath = os.path.abspath(config['path_to_batches_unassigned'])
    prepfilespath = os.path.abspath(config['path_to_batches_prepfiles'])
    
    unassigneddirli = os.listdir(unassignedpath)

    for folder in unassigneddirli:
        src = os.path.join(unassignedpath, folder)
        if re.search("Please check these Batches.txt", src): 
            continue #skip
        dst = os.path.join(prepfilespath, folder)
        try:
            os.mkdir(dst)
            copytree(src, dst)
        except:#copy new files added to the batch
            src_filesli = os.listdir(src)
            dst_fileli = os.listdir(dst)
            if len(src_filesli) > len(dst_fileli):
                for srcFile in src_filesli:
                    s = os.path.join(src, srcFile)
                    d = os.path.join(dst, srcFile)
                    try:
                        shutil.copy2(s, d)
                    except:
                        pass
 


def dcsinfo(dcspath):
    from lxml import etree
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

    infodcs = {"TotalRowsNbr": totalRows,
               "MPDTaskRowsNbr": mpdtask,
               "OperatorRowsNbr": optask,
               "FindingsRowsNbr": findings
              }

    return infodcs




def extendRowsFollowup():    
    import os
    import pandas as pd
    pd.options.mode.chained_assignment = None  # default='warn'
    from fup.utils.jsoninfo import configInfo
    from fup.utils.commun import current_date, listifyString, xllook

    config = configInfo()
    xlpath = config['path_to_excels_exported_from_database']
    xlfilepath = os.path.join(xlpath, 'followup.xlsx')

    #xllook(xlfilepath, 'A1:W1', close=True)

    fupdf = pd.read_excel(xlfilepath)

    #Append to a list of dfs, bids that have more than one file 
    orgfilesdfsli = []
    bidtodel = []
    for i, cell in enumerate(fupdf["OriginalFilesName"].tolist()):
        cellli = listifyString(str(cell)) 
        if len(cellli) > 1:
            bid = fupdf.loc[i, "BatchID"]
            bidtodel.append(bid)
            for j, orgfile in enumerate(cellli):
                #print(orgfile, bid)
                fup_bid = fupdf[fupdf['BatchID'] == bid]
                fup_bid.loc[i, "OriginalFilesName"] = orgfile
                fidli = listifyString(fup_bid.loc[i, "FilesID"])
                fup_bid.loc[i, "FilesID"] = fidli[j]
                orgfilesdfsli.append(fup_bid)

    #Make one df from df list created up
    orgfilesdf = pd.concat(orgfilesdfsli)

    #Remove from df batches that have more than one file
    fupdf = fupdf[~fupdf["BatchID"].str.contains('|'.join(bidtodel), na=False)]

    extended_fup = pd.concat([fupdf, orgfilesdf])
    extended_fup.reset_index(drop=True, inplace=True)

    extfilepath = os.path.join(xlpath, "followup {} DO NOT IMPORT THIS IN DATABASE.xlsx".format(current_date()))
    extended_fup.to_excel(extfilepath, index=False)

    xllook(extfilepath, 'A1:W1', close=False)
