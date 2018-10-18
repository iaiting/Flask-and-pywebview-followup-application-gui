from flask import Blueprint
from flask import render_template, request, redirect, url_for

batches_bp = Blueprint('batches_bp', __name__)

from dc.models.batches import Batches
from dc.utils.commun import Commun
from dc.models.users import User

batch = Batches()
func = Commun()
user = User()

@batches_bp.route("/generate-batch")
def generateBatch():
    try:
        bid_created = batch.add_batch()
        message= "Batch '{}' succesfully created!".format(bid_created)
        return redirect(url_for('com_bp.showSuccessPagewithMessage', message=message))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage=str(err)))


@batches_bp.route('/view-batches')
def viewBatches():
    session = user.session_info()
    if session["Rights"] == "user":
        context = batch.followup_for_responsible()
    else:
        context = batch.followup_reversed()
    return render_template('view_batches.html', context=context)


@batches_bp.route('/view-files')
def viewFiles():
    context = batch.fileshistory_table()
    return render_template('view_files.html', context=context)


@batches_bp.route("/update-batch-page", defaults={'batchlink': ''})
@batches_bp.route("/update-batch-page/<string:batchlink>")
def showUpdateBatchPage(batchlink):
    context_selected = batch.get_batch(batchlink)
    
    func.write_json(context_selected, "batch.json")
    
    context_selected['BatchID_'] = context_selected['BatchID']
    context_selected['Operator_'] = context_selected['Operator']
    context_selected['Aircraft_'] = context_selected['Aircraft'] 
    context_selected['AddedDate_'] = context_selected['AddedDate']
    context_selected['StartDate_'] = context_selected['StartDate']
    context_selected['ImportedDateISAIM_'] = context_selected['ImportedDateISAIM'] 
    context_selected['OverallStatus_'] = context_selected['OverallStatus']
    
    for col in ['BatchID', 'Operator', 'Aircraft', 'AddedDate', 'StartDate', 'ImportedDateISAIM', 'OverallStatus']:
        context_selected.pop(col, None)

    
    context_status = batch.bid_options()
    context_delete = batch.bid_options(get_followup=True, get_filehistory=True)

    context = {}
    context.update(context_status)
    context.update(context_delete)
    context.update(context_selected)

    return render_template('tasks/update_batch.html', context=context)


    
@batches_bp.route("/updatebatchstatus", methods=["POST", "GET"])
def updateBatchStatus():
    
    data = func.read_json("batch.json")
    session = user.session_info()
    
    update_data = {}

    update_data["BatchID"] = data["BatchID"]
    update_data["ResponsibleStatus"] = str(request.form['responsibleStatus']).replace("**", "")
    
    if session["Rights"] != "user":
        update_data["Proofreader"] = request.form['newproofreader']
        update_data["Responsible"] = request.form['reAssignBatch']
        update_data["ProofreaderStatus"] = str(request.form['proofreaderStatus']).replace("**", "")
        update_data["OverallStatus"] = request.form['overallStatus']

    if session["Rights"] == "user":
        update_data["ResponsibleComment"] = func.remove_punctuation(request.form['comments'])
    else:
        update_data["ProofreaderComment"] = func.remove_punctuation(request.form['comments'])
    
    update_data["EstimatedTaskNbr"] = request.form['estimatedtasks']
    update_data["EstimatedFdgNbr"] = request.form['estimatedfindings']

    try:
        indb, mailsent = batch.process_status_batch_form(update_data)
        if indb and mailsent:
            return redirect(url_for('com_bp.showSuccessPage'))
        elif indb and mailsent == False:
            return redirect(url_for('com_bp.showFailedPage', errormessage="Changes saved in the database but email not sent!"))
        else:
            return redirect(url_for('com_bp.showFailedPage', errormessage="Changes not applied to database!"))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage=str(err)))


@batches_bp.route("/delete-batch", methods=["POST", "GET"])
def deleteBatchFileHistory():
    data = func.read_json("batch.json")
    delete_data = {}
    delete_data["DefaultBatchID"] = data["BatchID"]
    try:
        delete_data["BatchID"] = request.form['batchtodelete']
    except:
        delete_data["BatchID"] = ""
    try:
        delete_data["FileToDelete"] = request.form['filetodelete']
    except:
        delete_data["FileToDelete"] = ""
    try:
        batch.delete_batch_or_file(delete_data)
        message= "Saved in database! Please delete the batch or file you selected from disk!"
        return redirect(url_for('com_bp.showSuccessPagewithMessage', message=message))
    except Exception as err:
        errmsg = func.write_traceback(err)
        print(errmsg)
        return redirect(url_for('com_bp.showFailedPage', errormessage=str(err)))


