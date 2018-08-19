from flask import Blueprint
from flask import render_template, request, redirect, url_for
#Extra imports
import os
# pylint: disable=E0611
from werkzeug import secure_filename

#App imports
from fup.utils.jsoninfo import configInfo, sessionInfo
from fup.utils.commun import generateID, current_date, movetobin
from fup.models.batch import addBatch
from fup.helpers.batch import importFollowup, extractFollowup, importFileshistory, extractFileshistory
from fup.helpers.files import autoNewDirs, updateDBforNewFiles, unassignedtoPrepfiles

createbatch = Blueprint('createbatch', __name__)


@createbatch.route("/import-followup")
def applyimportfollowup():
    try:
        importFollowup()
        return redirect(url_for('comm.showSuccessPage'))
    except Exception as e:
        errormessage = str("Something went wrong when importing the excel into the database. Got: {}".format(e))
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))



@createbatch.route("/extract-followup")
def applyextractFollowup():
    try:
        extractFollowup()
        return redirect(url_for('comm.showSuccessPage'))
    except Exception as e:
        errormessage = str("Something went wrong when extracting the excel from database. Got: {}".format(e))
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))


@createbatch.route("/import-fileshistory")
def applyimportfileshistory():
    try:
        importFileshistory()
        return redirect(url_for('comm.showSuccessPage'))
    except Exception as e:
        errormessage = str("Something went wrong when importing excel in database. Got: {}".format(e))
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))



@createbatch.route("/extract-fileshistory")
def applyextractfileshistory():
    try:
        extractFileshistory()
        return redirect(url_for('comm.showSuccessPage'))
    except Exception as e:
        errormessage = str("Something went wrong when extracting the excel from database. Got: {}".format(e))
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))



@createbatch.route("/auto-create-unassigned")
def autoCreateUnassignedfromNew():
    infoDictli, auto, tobinli = autoNewDirs()
    #print(tobinli)
    if isinstance(infoDictli, str):
        errormessage = str(infoDictli)
        return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
    elif isinstance(infoDictli, list):
        if len(infoDictli) == 0:
            errormessage = "No new files found in NEW folder!"
            return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
        else:
            for infoaddDict in infoDictli:
                response = addBatch(infoaddDict, auto)
                if isinstance(response, str):
                    movetobin(tobinli)
                    errormessage = str(response)
                    return redirect(url_for('comm.showFailedPage', errormessage=errormessage))

            unassignedtoPrepfiles() #Copy files from UNASSIGNED to PREPARED FILES

            responseMove = movetobin(tobinli)
            if responseMove  == True:
                try:
                    response_newFiles = updateDBforNewFiles() #verify if new files were added to a existing batch if so, update db
                    if isinstance(response_newFiles, str):
                        print("response_newFiles error: ", response_newFiles)
                        #return response_newFiles
                except Exception as e:
                    print("[ERROR] updateDBforNewFiles: ",e)
                    pass
                return redirect(url_for('comm.showSuccessPage'))
            else:
                errormessage = "These where deleted from NEW folder --> " + str(responseMove)
                return redirect(url_for('comm.showFailedPage', errormessage=errormessage))




# # "/upload-create-batch" - not used (replaced by "/auto-create-unassigned")
# @createbatch.route("/upload-create-batch", methods=["POST", "GET"])
# def uploadFilesCreateBatch():
#     config = configInfo()
#     fileobli = request.files.getlist("files2upload")
#     operator = request.form['operator'].strip().upper()
#     aircraft = request.form['aircraft'].strip().upper()
#     batchID = generateID()
#     batchNameFolder = operator+' '+ aircraft +' BID_'+batchID
#     #print(batchID)
#     try:
#         path = str(config['path_to_batches_unassigned'] + batchNameFolder)
#         path = os.path.abspath(path)
#         os.mkdir(path)
#         filesnameli = []
#         pathsli = []
#         fileIDli = []
#         for fileob in fileobli:
#             filename = secure_filename(fileob.filename)
#             fileid = generateID()
#             newFileName = 'FID_'+fileid+' '+filename
#             save_path = os.path.join(path, newFileName)
#             fileob.save(save_path)

#             filesnameli.append(filename)
#             pathsli.append(path)
#             fileIDli.append(fileid)

#         orgfilesname = ', '.join(filesnameli)
#         orgfilespath = list(set(pathsli))[0]
#         filesId = ', '.join(fileIDli)
#         addedDate = current_date()
#         infoaddDict =  {'BatchID': batchID,
#                         'Aircraft': aircraft,
#                         'Operator': operator,
#                         'OriginalFilesName': orgfilesname,
#                         'OriginalFilesPath': orgfilespath,
#                         'FilesID': filesId,
#                         'AddedDate': addedDate
#                         }
#         response = addBatch(infoaddDict, auto=False)
#         if isinstance(response, str):
#             errormessage = str(response)
#             return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
#         else:
#             return redirect(url_for('comm.showSuccessPage'))

#     except Exception as e:
#         errormessage = "Changes not saved into the database! Got: {}".format(str(e))
#         return redirect(url_for('comm.showFailedPage', errormessage=errormessage))
































#
