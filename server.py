from flask import Flask, render_template, request, stream_with_context, Response, jsonify
from OfflineAI.offlineai import AI_response

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
    
    text_to_analyse = request.form.get('text_data')
    response = AI_response(text_to_analyse)
    with open('D:/Excel Datasets/Project Summarize/Log Sheet.xlsx', 'a+') as file:
        file.write(time.strftime('%m-%d-%Y'))
    return jsonify({'result': response[47:]}) #Sliced the response to skip the header part '<|start_header_id|>assistant<|end_header_id|>'

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
