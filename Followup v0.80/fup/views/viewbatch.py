from flask import Blueprint
from flask import render_template, request, redirect, url_for

#App imports
from fup.helpers.batch import viewBatches, updateBatchOptions



viewbatch = Blueprint('viewbatch', __name__)


@viewbatch.route('/view-batches')
def showViewBatches():
    context = viewBatches()
    return render_template('view_batches.html', context=context)


@viewbatch.route("/create-new-batch")
def showCreateNewBatchPage():
    context = updateBatchOptions()
    return render_template("tasks/create_new_batch.html", context=context)


@viewbatch.route("/take-batch")
def showTakeBatchPage():
    context = updateBatchOptions()
    return render_template('tasks/take_batch.html', context=context)

@viewbatch.route("/update-batch", defaults={'batchlink': ''})
@viewbatch.route("/update-batch/<string:batchlink>")
def showUpdateBatchPage(batchlink):
    context = updateBatchOptions(batchlink)
    return render_template('tasks/update_batch.html', context=context)


@viewbatch.route("/import-export")
def showimportexport():
    context = updateBatchOptions()
    return render_template('tasks/import_export.html', context=context)









#
