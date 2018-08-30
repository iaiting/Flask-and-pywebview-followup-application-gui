# "python.linting.pylintArgs": [
# 	"--disable=C0111"
# ],

def create_app():
    from flask import Flask

    app = Flask(__name__)

    from fup.views.user import user
    from fup.views.commun import comm
    from fup.views.viewbatch import viewbatch
    from fup.views.createbatch import createbatch
    from fup.views.updatebatch import updatebatch

    app.register_blueprint(user)
    app.register_blueprint(comm)
    app.register_blueprint(viewbatch)
    app.register_blueprint(createbatch)
    app.register_blueprint(updatebatch)
    

    return app
