def create_table_followup():
    from fup.utils.dbwrap import execute_query
    from fup.models.sqlquery import create_table_followup
    return execute_query(create_table_followup)


def create_table_fileshistory():
    from fup.utils.dbwrap import execute_query
    from fup.models.sqlquery import create_table_fileshistory
    return execute_query(create_table_fileshistory)


def addBatch(infoaddDict, auto):
    from fup.utils.dbwrap import sql_insertDict
    from fup.helpers.files import saveFilesInfo
    from fup.utils.commun import deletetree#, cleanPath

    infoaddDict['Responsible'] = 'UNASSIGNED'
    infoaddDict['Proofreader'] = 'UNASSIGNED'
    infoaddDict['ResponsibleStatus'] = 'UNASSIGNED'
    infoaddDict['ProofreaderStatus'] = 'UNASSIGNED'
    infoaddDict['OverallStatus'] = 'UNASSIGNED'

    #print('addbatch: ', infoaddDict)

    #Check files added to this batch
    response = saveFilesInfo(infoaddDict, auto)
    if response == True:
        #infoaddDict['OriginalFilesPath'] = cleanPath(infoaddDict['OriginalFilesPath'])
        return sql_insertDict('followup', infoaddDict)
    else:
        #if new batch error then deletetree else(case new files added) don't
        if auto:
            deletetree(infoaddDict['OriginalFilesPath'])
            return response
        else:# DEFAULT IS AUTO! (all that is not auto is not taken into processing)
            return response


def checkOverallStatus():
    #if responsible and proofreader status are ASSIGNED set OverallStatus to ASSIGNED
    from fup.helpers.batch import checkAssignStatus
    from fup.utils.dbwrap import execute_query
    setOverallBatchToAssignedli = checkAssignStatus()
    update_followup_overallstatus = """UPDATE followup SET OverallStatus="{}" WHERE BatchID="{}";"""
    if len(setOverallBatchToAssignedli) != 0:
        for batch in setOverallBatchToAssignedli:
            if execute_query(update_followup_overallstatus.format("ASSIGNED", batch)) == True:
                pass
            else:
                return False
        return True
    else:
        return True



def assignBatchtoUser(batchID, assignedtoProofreader):
    from fup.utils.jsoninfo import sessionInfo
    from fup.utils.commun import current_date
    from fup.helpers.batch import getUnassignedBatch
    from fup.helpers.batchdirs import createAssignedDirFiles
    from fup.models.batch import checkOverallStatus
    from fup.utils.dbwrap import sql_updateDict
    from fup.helpers.batch import batchExists
    from fup.helpers.user import getuserProofreader


    if checkOverallStatus() == True:

        date = current_date()
        userinfo = sessionInfo()
        responsible_user = userinfo["current_user_working"]
        defaultProofreader = getuserProofreader(responsible_user)

        tableName = 'followup'

        updatedict = {"BatchID": batchID,
                      "Responsible": responsible_user,
                      "ResponsibleStatus": "ASSIGNED",
                      "Proofreader": defaultProofreader,
                      "ProofreaderStatus": "ASSIGNED",
                      "ChangesLog": ''
                     }
        if defaultProofreader == "UNASSIGNED":
            updatedict["ProofreaderStatus"] = "UNASSIGNED"

        updatedict_fallback = {"BatchID": batchID,
                               "Responsible": "UNASSIGNED",
                               "ResponsibleStatus": "UNASSIGNED",
                               "Proofreader": "UNASSIGNED",
                               "ProofreaderStatus": "UNASSIGNED",
                               "ChangesLog": ''
                              }

        colIDName = "BatchID"

        #print(updatedict)
        if (batchID == '' or batchExists(batchID)) and (assignedtoProofreader == True):
            unassignedBatch = getUnassignedBatch(batchID, 'ProofreaderStatus')
            updatedict["BatchID"] = unassignedBatch
            updatedict_fallback["BatchID"] = unassignedBatch
        elif (batchID == '' or batchExists(batchID)) and (assignedtoProofreader == False):
            unassignedBatch = getUnassignedBatch(batchID, 'ResponsibleStatus')
            updatedict["BatchID"] = unassignedBatch
            updatedict_fallback["BatchID"] = unassignedBatch

        if assignedtoProofreader == True:
            updatedict.pop("Responsible", None)
            updatedict.pop("ResponsibleStatus", None)
            updatedict.pop("ChangesLog", None)
            if sql_updateDict(tableName, updatedict, colIDName) == True:
                checkOverallStatus()
                return True
            else:
                print('1fallback', tableName, updatedict, colIDName)
                sql_updateDict(tableName, updatedict_fallback, colIDName)
                return False

        elif assignedtoProofreader == False:
            loginfo = "ASSIGNED to {} on {}".format(responsible_user, date)
            updatedict["ChangesLog"] = loginfo
            updatedict["StartDate"] = date
            if (sql_updateDict(tableName, updatedict, colIDName)) == True and (createAssignedDirFiles(updatedict["BatchID"]) == True):
                checkOverallStatus()
                return True
            else:
                print('2fallback', tableName, updatedict, colIDName)
                sql_updateDict(tableName, updatedict_fallback, colIDName)
                return False
    else:
        return False



def mergeBatches(batchidstrli):
    from fup.helpers.batchdirs import mergeDirBatches
    from fup.utils.commun import current_date, listifyString
    from fup.helpers.batch import batchInfo
    from fup.utils.dbwrap import sql_insertDict, sql_updateDict, sql_deleteRow
    import pandas as pd

    mergedInfodict = mergeDirBatches(batchidstrli)

    bidli = listifyString(batchidstrli)

    if isinstance(mergedInfodict, dict):
        prevInfodict = {}
        for batch in mergedInfodict['batchidli']:
            previnfo = batchInfo(batch)
            previnfo.pop('EstimatedTaskNbr', None)
            previnfo.pop('EstimatedFdgNbr', None)
            prevInfodict[batch] = previnfo
    else:
        print('Cannot merge dirs!')
        return False

    #gather prev info in a df then a dict
    dfli = []
    for bid in prevInfodict.keys():
        df = pd.DataFrame.from_dict(prevInfodict[bid]) #make df from dict
        dfli.append(df)

    dfall = pd.concat(dfli, axis=0)
    prevInfoDictAll = dfall.to_dict('list')

    prevInfoDictAll['BatchID'] = mergedInfodict['mergedID']
    infolog = 'Batch merged from "{}" on {}'.format(batchidstrli, current_date())
    prevlog = [str(l) for l in prevInfoDictAll['ChangesLog']]
    prevInfoDictAll['ChangesLog'] = ', '.join(list(set(prevlog))) + ', ' + infolog
    prevInfoDictAll['AddedDate'] = current_date()


    if sql_insertDict('followup', prevInfoDictAll) == False:
        return False

    for bid in bidli:
        if sql_deleteRow('followup', 'BatchID', bid) == False:
            return False

    return mergedInfodict['mergedID']



def appendNewFilesToBatch(batchID, orgfilesname, newfilespath, filesId):
    from fup.utils.dbwrap import sql_updateDict
    from fup.utils.commun import listifyString, uniquelist
    from fup.helpers.batch import batchInfo
    from fup.utils.commun import current_date, cleanPath

    colstoChange = ['OriginalFilesName', 'OriginalFilesPath', 'FilesID', 'ChangesLog', 'BatchID']
    infodict_previous = batchInfo(batchID)

    changeInfodict = {}
    for kcol, val in infodict_previous.items():
        if kcol in colstoChange:
            if kcol == 'ChangesLog':
                changeInfodict[kcol] = val[0] + ', New files added on {}'.format(current_date())

            elif kcol == 'OriginalFilesName':
                changeInfodict[kcol] = val[0] + ',\n' + orgfilesname

            elif kcol == 'OriginalFilesPath':
                #print("newfilespath", val[0], ' yuhuu ',newfilespath)
                if newfilespath in uniquelist(listifyString(val[0])):
                    changeInfodict[kcol] = cleanPath(newfilespath)

            elif kcol == 'FilesID':
                changeInfodict[kcol] = val[0] + ',\n' + filesId

            elif kcol == 'BatchID':
                changeInfodict[kcol] = batchID

    if sql_updateDict('followup', changeInfodict, 'BatchID') == False:
        return False
    else:
        return True





def splitBatches(splitFactor_batchid):
    from fup.helpers.batchdirs import createSplitDirs
    from fup.helpers.batch import batchInfo
    from fup.utils.commun import current_date, listifyString
    from fup.utils.dbwrap import sql_insertDict, sql_deleteRow

    splitBatchidli = splitFactor_batchid.split('_')
    splitFactor, batchid = int(splitBatchidli[0]), splitBatchidli[1]
    oldBatchinfo = batchInfo(batchid)

    infodirs = createSplitDirs(splitFactor, batchid)
    if infodirs != False:
        prevBatchID = infodirs['oldid']
        newBatchID = infodirs['newids']
    else:
        return False

    prevloginfo = [str(l) for l in oldBatchinfo['ChangesLog']]
    loginfo =  ''.join(prevloginfo) + ', Batch "{}" was splited in batches: "{}", on {}'.format(prevBatchID, newBatchID, current_date())
    oldBatchinfo['ChangesLog'] = loginfo

    newBIDli = listifyString(newBatchID)
    for bid in newBIDli:
        oldBatchinfo['BatchID'] = bid
        oldBatchinfo.pop('EstimatedTaskNbr', None)
        oldBatchinfo.pop('EstimatedFdgNbr', None) 
        if sql_insertDict('followup', oldBatchinfo) == False:
            return False

    if sql_deleteRow('followup', 'BatchID', batchid) == False:
        return False

    return newBatchID




def updateBatchinFollowup(batchdict):
    from fup.utils.dbwrap import sql_updateDict, tb_cols_placeholder
    from fup.utils.commun import cleanDict
    from fup.utils.jsoninfo import sessionInfo
    from fup.helpers.batchdirs import moveDirsforUpdate, renameAssgnDir
    from fup.models.batch import verifyStatus, resetStartDate

    #print('updateBatchinFollowup: ', batchdict)

    session = sessionInfo()

    try:
        cleanedBatch = cleanDict(batchdict)
        comment = cleanedBatch['comments']
        cleanedBatch.pop('comments', None)

        if session["current_user_rights"] == 'user':
            cleanedBatch['ResponsibleComment'] = comment
        elif session["current_user_rights"] == 'proofreader' or session["current_user_rights"] == 'admin':
            cleanedBatch['ProofreaderComment'] = comment
    except: #no comments
        pass

    followupCols = list(tb_cols_placeholder('followup')['columns'])
    infoBatchdict = {}
    for k, v in cleanedBatch.items():
        if k in followupCols:
            infoBatchdict[k] = v

    #print('updateBatchinFollowup-infoBatchdict: ', infoBatchdict)
    movedir_response = moveDirsforUpdate(infoBatchdict)
    #print(movedir_response)
    if movedir_response == False:
        return False

    infoBatchdict = verifyStatus(infoBatchdict)
    resetStartDate(infoBatchdict)
    #print('infoBatchdict ', infoBatchdict)
    try:
        if isinstance(infoBatchdict['Responsible'], str): 
            renameAssgnDir(infoBatchdict)
    except:
        pass

    if sql_updateDict('followup', infoBatchdict, 'BatchID') == False:
        return False
    else:
        return True


def verifyStatus(infoBatchdict):
    #print('verifyStatus: ',infoBatchdict)
    try:
        try:#if user
            #'TO BE CHECKED'
            if infoBatchdict['ResponsibleStatus'] == 'TO BE CHECKED':
                infoBatchdict['OverallStatus'] = 'TO BE CHECKED'
                return infoBatchdict
            elif infoBatchdict['ResponsibleStatus'] != 'UNASSIGNED':
                infoBatchdict['OverallStatus'] = 'ONGOING'
                return infoBatchdict
        except:#if proofreader
            #"TO BE IMPORTED, FINISHED, REWORK, STANDBY, UNRECORDABLE"
            if infoBatchdict['ProofreaderStatus'] == 'REWORK':
                infoBatchdict['OverallStatus'] = 'REWORK'
                infoBatchdict['ResponsibleStatus'] = 'REWORK'
                return infoBatchdict
            elif infoBatchdict['ProofreaderStatus'] == 'STANDBY':
                
                from fup.helpers.batch import batchInfo
                from fup.utils.commun import current_date
                from fup.utils.dbwrap import sql_updateDict

                prevInfoDictAll = batchInfo(infoBatchdict['BatchID'])
                prevlog = [str(l) for l in prevInfoDictAll['ChangesLog']]
                infolog = str("SET to STANDBY on {}".format(current_date()))
                log = ', '.join(list(set(prevlog))) + ',\n' + infolog
                upd = {"ChangesLog": log, "StartDate": "-", "BatchID": infoBatchdict['BatchID']}
                sql_updateDict('followup', upd, "BatchID")
                infoBatchdict['OverallStatus'] = 'STANDBY'
                infoBatchdict['ResponsibleStatus'] = 'STANDBY'
                return infoBatchdict
            elif infoBatchdict['ProofreaderStatus'] == 'UNRECORDABLE':
                infoBatchdict['OverallStatus'] = 'UNRECORDABLE'
                infoBatchdict['ResponsibleStatus'] = 'UNRECORDABLE'
                return infoBatchdict
            elif infoBatchdict['ProofreaderStatus'] == 'FINISHED':
                infoBatchdict['OverallStatus'] = 'FINISHED'
                infoBatchdict['ResponsibleStatus'] = 'FINISHED'
                return infoBatchdict
            elif infoBatchdict['ProofreaderStatus'] == 'TO BE IMPORTED':
                infoBatchdict['OverallStatus'] = 'TO BE IMPORTED'
                return infoBatchdict
    except:
        return infoBatchdict



def resetStartDate(infodict):
    from fup.helpers.batch import batchInfo
    from fup.utils.commun import current_date
    from fup.utils.dbwrap import sql_updateDict

    bid = infodict["BatchID"]#"eyi0hT"
    newStatus = infodict["OverallStatus"]

    prevInfoDictAll = batchInfo(bid)

    standby = prevInfoDictAll['OverallStatus'][0] == 'STANDBY'
    startdate = prevInfoDictAll['StartDate'][0] == '-'
    if standby and startdate and newStatus != "STANDBY":
        date = current_date()
        sql_updateDict('followup', {"StartDate": date, "BatchID": bid}, "BatchID")




def cleanBatchPath(batchstr):
    from fup.utils.commun import cleanPath, listifyString
    from fup.helpers.batch import batchInfo
    from fup.utils.dbwrap import sql_updateDict

    batches = listifyString(batchstr)

    for batch in batches:
        infoBatch = batchInfo(batch)

        #Prepare dict for sql_updateDict func (in future maybe move this to sql_updateDict func)
        prepinfoBatch = {}
        for k, v in infoBatch.items():
            if isinstance(v, list):
                val = v[0]
                if val == 'None' or val == None:
                    val = ''
                prepinfoBatch[k] = val
            else:
                prepinfoBatch[k] = v

        prepinfoBatch['OriginalFilesPath'] = cleanPath(prepinfoBatch['OriginalFilesPath'])
        sql_updateDict('followup', prepinfoBatch, 'BatchID')













































#
