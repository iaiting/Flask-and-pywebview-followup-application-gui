


def viewBatches(user_batches=False):
    from fup.utils.dbwrap import get_dftable
    from fup.utils.jsoninfo import sessionInfo
    import pandas
    df = get_dftable('followup')
    if user_batches == True:
        session = sessionInfo()
        user_working = session['current_user_working']
        df_batchesinWork = df[df['Responsible'] == user_working]
        df_dictinWork = df_batchesinWork.reindex(index=df_batchesinWork.index[::-1]).to_dict('list')
        return df_dictinWork
    else:
        df_dict = df.reindex(index=df.index[::-1]).to_dict('list')
        return df_dict


def updateBatchOptions(batchlink=''):
    #get batch update options depending on the user type (user/responsible, admin or proofreader)
    from fup.utils.commun import listifyString
    from fup.utils.jsoninfo import configInfo, sessionInfo
    from fup.helpers.user import get_usersdict
    from fup.helpers.batch import viewBatches
    from fup.helpers.batch import batchInfo

    #print('updateBatchOptions: ', batchlink)

    config = configInfo()
    update_options_responsible = listifyString(config['batch_status_options_responsible'])
    update_options_proofreader = listifyString(config['batch_status_options_proofreader'])
    update_options_overall = listifyString(config['batch_status_options_overall'])
    aircraft = listifyString(config['aircraft'])
    split_batch_factor = listifyString(config['split_batch_factor'])
    allusers = get_usersdict(True)

    session = sessionInfo()
    current_user_rights = session['current_user_rights']
    
    infoBatch = batchInfo(batchlink)
    try:
        infoBatch["Operator"]
    except:
        infoBatch = {'Operator': '', 'Aircraft': '', 'OverallStatus': '', 'AddedDate':'', 'StartDate':'', 'ImportedDateISAIM': ''}

    update_batch_dict = {"responsibleStatus": update_options_responsible,
                         "proofreaderStatus": update_options_proofreader,
                         "overallStatus": update_options_overall,
                         "aircraft": aircraft,
                         "splitBatch": split_batch_factor,
                         "allusers": allusers,
                         "batchlink": batchlink,
                         "userBatches": viewBatches(user_batches=True),
                         "disableCommentResponsible": '',
                         "disableCommentProofreader": '',
                         "disableCheckbox": '',
                         "infoBatch": infoBatch
                         }

    if current_user_rights == 'user':
        update_batch_dict["proofreaderStatus"] = ['You cannot change this']
        update_batch_dict["allusers"] = ['You cannot change this']
        update_batch_dict["overallStatus"] = ['You cannot change this']
        update_batch_dict["disableCommentProofreader"] = "disabled"
        update_batch_dict["disableCheckbox"] = "disabled"
        return update_batch_dict
    elif current_user_rights == 'proofreader':
        update_batch_dict["responsibleStatus"] = ['You cannot change this']
        update_batch_dict["disableCommentResponsible"] = "disabled"
        return update_batch_dict
    elif current_user_rights == 'admin':
        return update_batch_dict




def getUnassignedBatch(batchID, usertype):
    #Select an UNASSIGNED batch from the followup by batchID if found or
    #return first met UNASSIGNED batch
    from fup.utils.dbwrap import get_dftable
    import pandas

    df = get_dftable('followup')
    df_unassigned = df[df[usertype] == 'UNASSIGNED']
    df_batch = df_unassigned[df_unassigned['BatchID'] == batchID]
    try:
        if df_batch.shape[0] == 0:
            df_batchUnassigned = df[df[usertype] == 'UNASSIGNED'].head(1)
            selected_Unassigned = df_batchUnassigned['BatchID'].tolist()[0]
            return selected_Unassigned
        else:
            selected_BatchID = df_batch['BatchID'].tolist()[0]
            return selected_BatchID
    except Exception as e:
        #print("\n\ngetUnassignedBatch error: {}, \n df {}\n\n".format(e, df_batch.shape[0]))
        return False



def getChangesLog(batchID):
    #get change log for batch ID as a list
    from fup.utils.dbwrap import get_dftable
    import pandas
    df = get_dftable('followup')
    df_batch = df[df['BatchID'] == batchID]
    return df_batch['ChangesLog'].tolist()


def checkAssignStatus():
    from fup.utils.dbwrap import get_dftable
    import pandas as pd

    df = get_dftable('followup')

    df_assignedUser = df[df['ResponsibleStatus'] == 'ASSIGNED']
    df_assignedProof = df[df['ProofreaderStatus'] == 'ASSIGNED']
    assignedBatchesUser = df_assignedUser['BatchID'].tolist()
    assignedBatchesProof = df_assignedProof['BatchID'].tolist()
    communliBatch = list(set(assignedBatchesUser).intersection(assignedBatchesProof))
    return communliBatch


def batchExists(batchid):
    from fup.utils.dbwrap import get_dftable
    import pandas

    df = get_dftable('followup')
    df_batch = df[df['BatchID'] == batchid]
    if df_batch.shape[0] != 0:
        return True
    else:
        return False


def batchInfo(batchid):
    from fup.utils.dbwrap import get_dftable
    from fup.helpers.batch import batchExists
    import pandas

    if batchExists(batchid):
        df = get_dftable('followup')
        df_batchDict = df[df['BatchID'] == batchid].to_dict('list')
        return df_batchDict
    else:
        return False



def checkupdate(batchChangesdict):
    #check for *
    import re

    #print(batchChangesdict)

    splitFactor = batchChangesdict['splitBatchFactor']
    batch = batchChangesdict['BatchID']
    filestoadd = batchChangesdict['filestoupload']

    signdict = {'merge': False, 'split': False, 'add': False}

    if re.search(',', batch):
        signdict['merge'] = True

    if len(splitFactor) != 0:
        signdict['split'] = True

    if filestoadd != 0:
        signdict['add'] = True


    signli = list(signdict.values())
    size = signli.count(True)

    if size == 0:
        #print("return 'update'")
        return 'update'
    elif size == 1:
        excludeli = ['splitBatchFactor', 'BatchID', 'filestoupload']
        for opr, val in signdict.items():
            if val == True:
                #print('Operation: ',opr)
                li = []
                for k, v in batchChangesdict.items():
                    if k in excludeli:
                        pass
                    else:
                        if v == '' or v == 0:
                            pass
                        else:
                            li.append(1)
                if len(li) == 0:
                    #print('return operation: ', opr)
                    return opr
                else:
                    #print('return False')
                    return False
    elif size > 1:
        #print("return FFalse")
        return False



def importFollowup():
    #check if the excel contains the columns needed and import it if it has
    import pandas as pd
    from fup.utils.dbwrap import tb_cols_placeholder, df2sql
    from fup.utils.jsoninfo import configInfo


    config = configInfo()
    followup_columns = list(tb_cols_placeholder('followup')['columns'])

    df = pd.read_excel(config['path_to_excels_to_be_imported_in_database'] + 'followup.xlsx')
    xlfollowupColsli = df.columns.tolist()
    cols_diff = list(set(followup_columns).difference(set(xlfollowupColsli)))
    if len(cols_diff) == 0:
        df2sql(df, 'followup')
        return True
    else:
        colsneeded = ', '.join(followup_columns)
        response = "The followup.xlsx must contain theese columns: " + colsneeded
        return response


def extractFollowup(user_batches=False):
    import os
    import pandas as pd
    from fup.utils.dbwrap import sql2df
    from fup.utils.jsoninfo import configInfo, sessionInfo
    from fup.helpers.files import extendRowsFollowup

    config = configInfo()
    xlpath = config['path_to_excels_exported_from_database']
    df = sql2df('followup')

    if  user_batches == True:
        session = sessionInfo()
        user_working = session['current_user_working']
        df_batchesinWork = df[df['Responsible'] == user_working]
        save_path = os.path.join(xlpath, '{} batches.xlsx'.format(user_working))
        df_batchesinWork.to_excel(save_path, index=False)
    else:
        save_path = os.path.join(xlpath, 'followup.xlsx')
        df.to_excel(save_path, index=False)
        extendRowsFollowup()


#importFileshistory, extractFileshistory

def importFileshistory():
    #check if the excel contains the columns needed and import it if it has
    import pandas as pd
    from fup.utils.dbwrap import tb_cols_placeholder, df2sql
    from fup.utils.jsoninfo import configInfo


    config = configInfo()
    fileshistory_columns = list(tb_cols_placeholder('fileshistory')['columns'])

    df = pd.read_excel(config['path_to_excels_to_be_imported_in_database'] + 'fileshistory.xlsx')
    xlfileshistoryColsli = df.columns.tolist()
    cols_diff = list(set(fileshistory_columns).difference(set(xlfileshistoryColsli)))
    if len(cols_diff) == 0:
        df2sql(df, 'fileshistory')
        return True
    else:
        colsneeded = ', '.join(fileshistory_columns)
        response = "The fileshistory.xlsx must contain theese columns: " + colsneeded
        return response


def extractFileshistory():
    import os
    import pandas as pd
    from fup.utils.dbwrap import sql2df
    from fup.utils.jsoninfo import configInfo
    from fup.utils.commun import xllook

    config = configInfo()
    xlpath = config['path_to_excels_exported_from_database']
    df = sql2df('fileshistory')
    save_path = os.path.join(xlpath, 'fileshistory.xlsx')
    df.to_excel(save_path, index=False)
    xllook(save_path, 'A1:E1', close=False)






















#
