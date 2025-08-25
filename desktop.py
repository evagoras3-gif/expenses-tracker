import threading
import webview
from app import app  # Replace 'app' with the name of your Flask app file if different

def start_server():
    app.run(debug=False)

# Start Flask in a separate thread
threading.Thread(target=start_server).start()

# Open a desktop window with your app
webview.create_window("Expense Tracker", "http://127.0.0.1:5000", width=900, height=700, resizable=True)
webview.start()
