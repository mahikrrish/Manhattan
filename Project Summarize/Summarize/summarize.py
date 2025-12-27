import ollama

def summarize(text_to_summarize):
    """
        Connects to the local Ollama instance and summarizes the text.
    """
    try:
        response = ollama.chat(model='llama3.2:1b', messages=[
            {
                'role': 'user',
                'content': f'Summarize the following text concisely: \n\n{text_to_summarize}'
            }
        ])
        return response['message']['content']
    except Exception as e:
        return f'Error connecting to Ollama : {str(e)}'