import sys
import webview
import threading
from flask import Flask
from dc.utils.commun import Commun
from dc.utils.folders import Folders
from flask_mail import Mail, Message


folder = Folders()
folder.make_default_dirs()

class App:

    func = Commun()
    conf = func.config_info()

    def create_app(self):
        """Create the app from Blueprints"""
        
        app = Flask(__name__)

        from dc.views.users import user_bp
        from dc.views.commun import com_bp
        from dc.views.batches import batches_bp

        app.register_blueprint(user_bp)
        app.register_blueprint(com_bp)
        app.register_blueprint(batches_bp)

        return app
    

    def run_server(self, run_in_browser=True, webview_name="App", width=1024, height=720):
        """Run in browser or in pywebview browser"""
        
        app = self.create_app()
        if run_in_browser:
            port_nbr = int(self.conf["port"])
            app.run(host='127.0.0.1', port=port_nbr, debug=True)
        
        else:
            def start_server():
                app.run()
            if __name__ == '__main__':
                t = threading.Thread(target=start_server)
                t.daemon = True
                t.start()
                webview.create_window(webview_name, "http://127.0.0.1:{}/".format(self.conf["port"]), width=width, height=height)
                sys.exit()