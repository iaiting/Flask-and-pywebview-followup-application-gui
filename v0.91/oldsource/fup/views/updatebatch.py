from flask import Blueprint
from flask import render_template, request, redirect, url_for
# pylint: disable=E0611
from werkzeug import secure_filename

#App imports
import re, os
from fup.models.batch import assignBatchtoUser
from fup.utils.jsoninfo import configInfo
from fup.utils.dbwrap import sql_insertDict
from fup.helpers.batch import batchInfo, checkupdate
from fup.models.batch import mergeBatches, appendNewFilesToBatch, splitBatches, updateBatchinFollowup, cleanBatchPath
from fup.utils.commun import generateID, current_date
from fup.helpers.files import getfileSizeMtime, checkFileInfo


updatebatch = Blueprint('updatebatch', __name__)



@updatebatch.route("/assign-batch", methods=["POST", "GET"])
def assignBatch():
    #Refresh the database and assign a batch to the user
    batchID = request.form["batchid"]
    #print('yuhuu', batchID)
    try:
        assignedtoProofreader = request.form['assignedtoProofreader']
        assignedtoProofreader = True
    except:
        assignedtoProofreader = False

    if assignBatchtoUser(batchID, assignedtoProofreader):
        return redirect(url_for('comm.showSuccessPage'))
    else:
        errormessage = "No UNASSIGNED batches foun or 'path_to_files_needed' are not set correctly!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))



@updatebatch.route('/merge-batches/<string:batches>')
def applyMergeBatches(batches):
    result = mergeBatches(batches)
    if result != False:
        cleanBatchPath(result)
        message = 'Your new merged batch is: {}'.format(result)
        return redirect(url_for('comm.showSuccessPagewithMessage', message=message))
    else:
        errormessage = "Can't merge batches, check if batches exists!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))




@updatebatch.route('/split-batches/<string:splitFactor_Batch>')
def applySplitBatches(splitFactor_Batch):
    result = splitBatches(splitFactor_Batch)
    if result != False:
        cleanBatchPath(result)
        message = 'Your new splited batches are: {}'.format(result)
        return redirect(url_for('comm.showSuccessPagewithMessage', message=message))
    else:
        errormessage = "Can't split batches! Check guide to see what to do next!"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))



@updatebatch.route("/apply-update-batch", methods=["POST"])
def applyUpdateBatchChanges():
    batchChangesdict = {}
    config = configInfo()
    batchChangesdict['BatchID'] = request.form['batchid']
    batchid = batchChangesdict['BatchID']

    #print('applyUpdateBatchChanges: ', batchid)

    batchChangesdict['ResponsibleStatus'] = str(request.form['responsibleStatus']).replace("**", "")
    batchChangesdict['ProofreaderStatus'] = str(request.form['proofreaderStatus']).replace("**", "")
    batchChangesdict['OverallStatus'] = request.form['overallStatus']
    batchChangesdict['Aircraft'] = request.form['aircraft']
    batchChangesdict['Responsible'] = request.form['reAssignBatch']
    try:
        batchChangesdict['splitBatchFactor'] = request.form['splitBatch'] 
        splitFactor = batchChangesdict['splitBatchFactor']
    except:
        pass
    try:
        fileobli = request.files.getlist("files2upload")
        batchChangesdict['filestoupload'] = len(fileobli)
    except:
        pass

    try:
        batchChangesdict['EstimatedTaskNbr'] = request.form['aproxtasknr']
    except:
        batchChangesdict['EstimatedTaskNbr'] = ''
        pass

    try:
        batchChangesdict['EstimatedFdgNbr'] = request.form['aproxfdgnr']
    except:
        batchChangesdict['EstimatedFdgNbr'] = ''
        pass

    try:
        batchChangesdict['comments'] = request.form['comments']
    except:
        batchChangesdict['comments'] = ''
        pass

    updateResponse = checkupdate(batchChangesdict)
    print('updateResponse: ', updateResponse)

    if updateResponse  != False:
        if updateResponse == 'merge':
            #Deal with Merge Batches
            batches = str(batchid)
            return redirect(url_for('updatebatch.applyMergeBatches', batches=batches))
        elif updateResponse == 'add':
            batchStatus = batchInfo(batchid)
            batchStatus = batchStatus['OverallStatus'][0]
            #Deal with the adding more files to one batch
            if batchStatus != False:
                if batchStatus != "UNASSIGNED":
                    bidDirAssigned = os.path.abspath(config['path_to_batches_assigned'])
                    assginedDirsli = os.listdir(bidDirAssigned)
                    assignedDir = [folderName for folderName in assginedDirsli if re.search(batchid, folderName)][0]
                    path = os.path.join(bidDirAssigned, assignedDir)
                    
                    filesnameli = []
                    pathsli = []
                    fileIDli = []
                    for fileob in fileobli:
                        filename = secure_filename(fileob.filename)
                        fileid = generateID()
                        newFileName = 'FID_'+fileid+' '+filename
                        save_path = os.path.join(path, newFileName)
                        fileob.save(save_path)
                        #Check if file was added before
                        fileinfo = getfileSizeMtime(save_path)
                        fileinfo['FileID'], fileinfo['FileName'] =  fileid, filename
                        fileinfo['AddedInBatch'] = batchid
                        responseFileInfo = checkFileInfo(fileinfo)
                        if responseFileInfo != True:
                            os.remove(save_path)
                            errormessage = responseFileInfo
                            return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
                        else:
                            sql_insertDict('fileshistory', fileinfo)
                        
                        filesnameli.append(filename)
                        pathsli.append(path)
                        fileIDli.append(fileid)

                    orgfilesname = ', '.join(filesnameli)
                    newfilespath = ', '.join(pathsli)
                    filesId = ', '.join(fileIDli)
                    if appendNewFilesToBatch(batchid, orgfilesname, newfilespath, filesId) == True:
                        return redirect(url_for('comm.showSuccessPage'))
                    else:
                        errormessage = "Changes not saved into the database!"
                        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))

                
                elif batchStatus == "UNASSIGNED":
                    errormessage = "Barch is UNASSIGNED! You can add new files using this method only if this batch is ASSIGNED!"
                    return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
        
        
        elif updateResponse == 'split':
            #Deal with the splitBatch
            splitFactor_Batch = str(splitFactor) + '_' + str(batchid)
            return redirect(url_for('updatebatch.applySplitBatches', splitFactor_Batch=splitFactor_Batch))

        elif updateResponse == 'update':
            #Just update the batch in the database
            if updateBatchinFollowup(batchChangesdict):
                return redirect(url_for('comm.showSuccessPage'))
            else:
                errormessage = str("Moving BID_{} folders failed or DCS info not found! Check docs for more info..".format(batchid))
                return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
    else:
        print(updateResponse)
        errormessage = "Only one change can be applyed for options with  '*'  sign! Reset to defaults by clicking '| Update Batches' title"
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))




















































#
