import sys
import webview
import threading



class App:

    
    def create_app(self):
        
        """Create the app from Blueprints"""
        from flask import Flask

        app = Flask(__name__)

        from dc.views.users import user_bp
        from dc.views.commun import com_bp
        # from fup.views.viewbatch import viewbatch
        # from fup.views.createbatch import createbatch
        # from fup.views.updatebatch import updatebatch

        app.register_blueprint(user_bp)
        app.register_blueprint(com_bp)
        # app.register_blueprint(viewbatch)
        # app.register_blueprint(createbatch)
        # app.register_blueprint(updatebatch)
        

        return app
    

    def run_server(self, run_in_browser=True, webview_name="App", width=1024, height=720):
        """Run in browser or in pywebview browser"""
        
        app = self.create_app()
        
        if run_in_browser:
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