from flask import Flask, render_template, request
from Summarize.summarize import summarize

app = Flask('Summarize Your Text')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarizer():
    text_to_summarize = request.form.get('text_to_summarize')
    response = summarize(text_to_summarize)

    return render_template('index.html', original_text=text_to_summarize, summary_result=response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
