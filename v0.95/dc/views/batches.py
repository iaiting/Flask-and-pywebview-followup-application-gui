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
    context = batch.followup_reversed()
    return render_template('view_batches.html', context=context)



@batches_bp.route("/update-batch-page", defaults={'batchlink': ''})
@batches_bp.route("/update-batch-page/<string:batchlink>")
def showUpdateBatchPage(batchlink):
    context = batch.get_batch(batchlink)
    func.write_json(context, "batch.json")
    return render_template('tasks/update_batch.html', context=context)


@batches_bp.route("/updatestatus")
def showUpdateStatusPage():
    context = batch.bid_options()
    return render_template('tasks/update_status.html', context=context)
    
@batches_bp.route("/updatebatchstatus", methods=["POST", "GET"])
def updateBatchStatus():
    
    data = func.read_json("batch.json")
    session = user.session_info()
    
    update_data = {}

    update_data["BatchID"] = data["BatchID"]
    update_data["Aircraft"] = request.form['aircraft']
    update_data["Operator"] = request.form['operator']

    
    update_data["ResponsibleStatus"] = str(request.form['responsibleStatus']).replace("**", "")
    update_data["ProofreaderStatus"] = str(request.form['proofreaderStatus']).replace("**", "")
    
    if session["Rights"] == "user":
        update_data["ResponsibleComment"] = request.form['comments']
    else:
        update_data["ProofreaderComment"] = request.form['comments']
    
    update_data["OverallStatus"] = request.form['overallStatus']
    update_data["EstimatedTaskNbr"] = request.form['estimatedtasks']
    update_data["EstimatedFdgNbr"] = request.form['estimatedfindings']


    if batch.process_status_batch_form(update_data):
        return redirect(url_for('com_bp.showSuccessPage'))
    else:
        return redirect(url_for('com_bp.showFailedPage', errormessage="Changes not applied to database!"))
   
