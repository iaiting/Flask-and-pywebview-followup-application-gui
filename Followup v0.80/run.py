import webview
import threading, sys

from fup import create_app

app = create_app()


def runInBrowser(run=True):
    #run in browser or in pywebview browser
    if run:
        if __name__ == "__main__":
            app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        def start_server():
            app.run()

        if __name__ == '__main__':
            t = threading.Thread(target=start_server)
            t.daemon = True
            t.start()
            webview.create_window("FollowUp-DC", "http://127.0.0.1:5000/", width=1024, height=720)
            sys.exit()


runInBrowser(run=True)
