from flask import Blueprint
from flask import render_template, request, redirect, url_for

#App imports
from fup.utils.jsoninfo import appSettings


comm = Blueprint('comm', __name__)



@comm.route('/success')
def showSuccessPage():
    return render_template('success.html')

@comm.route('/success/<string:message>')
def showSuccessPagewithMessage(message):
    context = {'message': message}
    return render_template('success_msg.html', context=context)


@comm.route('/failed/<string:errormessage>')
def showFailedPage(errormessage):
    context = {'failed': errormessage}
    return render_template('failed.html', context=context)

@comm.route('/app-settings/')
def showAppSettings():
    context = appSettings()
    return render_template('app_settings.html', context=context)
