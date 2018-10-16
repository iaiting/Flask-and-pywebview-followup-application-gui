from flask import Blueprint
from flask import render_template, request, redirect, url_for


com_bp = Blueprint('com_bp', __name__)


@com_bp.route('/success')
def showSuccessPage():
    return render_template('success.html')

@com_bp.route('/success/<string:message>')
def showSuccessPagewithMessage(message):
    context = {'message': message}
    return render_template('success_msg.html', context=context)

@com_bp.route('/failed/<string:errormessage>')
def showFailedPage(errormessage):
    context = {'failed': errormessage}
    return render_template('failed.html', context=context)

