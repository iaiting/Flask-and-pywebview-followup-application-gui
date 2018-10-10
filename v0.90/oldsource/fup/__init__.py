import sys
import threading
import webview
from flask import Flask


def create_app():
    """Create flask app from blueprints"""

    app = Flask(__name__)

    # from fup.views.user import user
    # from fup.views.commun import comm
    # from fup.views.viewbatch import viewbatch
    # from fup.views.createbatch import createbatch
    # from fup.views.updatebatch import updatebatch

    # app.register_blueprint(user)
    # app.register_blueprint(comm)
    # app.register_blueprint(viewbatch)
    # app.register_blueprint(createbatch)
    # app.register_blueprint(updatebatch)
    

    return app
    
    
def run_server(run_in_browser=True, webview_name="App", width=1024, height=720):
    """Run in browser or in pywebview browser"""
    
    app = create_app()
    
    if run_in_browser:
        if __name__ == "__main__":
            app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        def start_server():
            app.run()
        if __name__ == '__main__':
            t = threading.Thread(target=start_server)
            t.daemon = True
            t.start()
            webview.create_window(webview_name, "http://127.0.0.1:5000/", width=width, height=height)
            sys.exit()