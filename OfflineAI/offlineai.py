from ollama import chat
import database

def AI_response(user_input):
    """"
    Connects to the local Ollama instance and summarizes the text.
    """
    model_name = 'llama3.2:3b'
    messages = [
        {
            'role': 'system',
            'content': "You are a concise execution engine. Your output must contain ONLY the final result. Do not provide a preamble, do not explain your process, and do not repeat the instructions. Direct answer only."
                       "Constraint: Use professional, objective language. "
                       "Constraint: Format the lists as bullet points, if it's visually appealing. "
                       "Constraint: Hide your reasoning and logical thinking process, and return only the response"
                       "Constraint: Only return the final result."
                       "Constraint: Do not include introductory or concluding remarks."
        },
        {
            'role': 'user',
            'content': f'Below is a request from a user. Please identify the task and execute it accurately using the provided context. {user_input}'
        }
    ]
    try:
        response = chat(model=model_name, messages=messages,
                        options={'temperature': 0.1, 'num_ctx': 8192, 'keep_alive': '10m'},
                        stream=False
                        )
        return response['message']['content'], model_name
    except Exception as e:
        return f'Error connecting to Ollama : {str(e)}'
