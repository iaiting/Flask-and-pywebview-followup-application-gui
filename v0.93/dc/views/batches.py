from flask import Blueprint
from flask import render_template, request, redirect, url_for

batches_bp = Blueprint('batches_bp', __name__)

from dc.models.batches import Batches
from dc.utils.commun import Commun

batch = Batches()
func = Commun()

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


@batches_bp.route("/update-status")
def showUpdateStatusPage():
    #context = batch.bid_options()
    #return render_template('tasks/update_status.html', context=context)
    return render_template('tasks/update_status.html')