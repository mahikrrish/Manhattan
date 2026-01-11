from flask import Flask, render_template, request, stream_with_context, Response, jsonify, make_response
from OfflineAI.offlineai import AI_response
import database

app = Flask('OfflineAI Your Text')

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     # file = request.files['file']

@app.route('/process', methods=['POST'])
def analyse():
    '''
    1. render_template (Synchronous / Full Reload)
    Purpose: Used to send a brand-new HTML file from the server to the browser.
    User Experience: The browser screen "blinks" or refreshes because it has to discard the current page and draw a new one.

    2. jsonify (Asynchronous / Partial Update)
    Purpose: Used to send only data (as a JSON object) instead of a full webpage.
    User Experience: The page stays exactly as it is, and only the specific response part gets updated.

    Why jsonify is the "Professional" Choice?
    Speed (Low Latency): Sending a small JSON string (e.g., {"result": "Summary here"}) uses much less bandwidth.
    Maintaining State: If render_template is used, any text typed in the input box would disappear when the page reloads. With jsonify, the input stays visible while the AI "thinks".

    The Technical "Handshake"
    In Flask: jsonify converts the Python dictionary into a JSON string and automatically sets the correct HTTP headers (Content-Type: application/json) so the browser knows it’s receiving data, not a webpage.
    In JavaScript: The fetch() function in index.html is specifically designed to catch JSON data and "inject" it into outputBox without a refresh.
    '''
    
    user_input = request.form.get('text_data')
    response, model_name = AI_response(user_input=user_input)
    response_obj = make_response(jsonify({'result': response}))
    database.log(action=request.method, input_type= request.path, user_input=user_input, response=response, model_name=model_name, status_code=response_obj.status_code).queries()
    return response_obj


# @app.after_request
# def log_response_info(response):
#     # Extract the status code (e.g., 200, 404, 500)
#     status_code = response.status_code
#
#     # Extract the method (GET, POST, etc.)
#     method = request.method
#
#     # Extract the path (/process, /stt-listen, etc.)
#     path = request.path
#     database.log(action=method, input_type= path, user_input=g.user_input, response=g.response, model_name=g.model_name, status_code=status_code).queries()
#
#     return response  # You MUST return the response object

# @app.route('/stt-listen')
# def stt_listen():
#     # This is where you call your Vosk logic
#     # text = vosk_service.listen_and_transcribe()
#     # return jsonify({"text": text})

# @app.route('/speak', methods=['POST'])
# def speak():
#     response.json.get('text')
#     pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
