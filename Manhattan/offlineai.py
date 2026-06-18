try:
    from ollama import chat
except ModuleNotFoundError:
    print('ModuleNotFoundError')
try:
    from Manhattan import database
except ModuleNotFoundError:
    print('ModuleNotFoundError')
try:
    import pandas as pd
except ModuleNotFoundError:
    print('ModuleNotFoundError')


def history():
    past_conversation = database.log(action='GET').queries()
    past_conversation = past_conversation.loc[:, ['User_Input', 'Response']]
    history = []
    for i in range(past_conversation.index.start, past_conversation.index.stop):
        # 1. Wrap the User's question
        history.append({
            "role": "user",
            "content": past_conversation['User_Input'][i]
        })

        # 2. Wrap the AI's previous answer
        history.append({
            "role": "assistant",
            "content": past_conversation['Response'][i]
        })
    return history



def AI_response(user_input, history=history()):
    """"
    Connects to the local Ollama instance and summarizes the text.
    """
    model_name = 'llama3.2:3b'
    messages = [
        {
            'role': 'system',
            'content': (
            "You are a direct execution engine. "
            "Output ONLY the final answer. "
            "Never describe the task. Never list context. Never show reasoning. "
            "If you cannot answer, say 'Insufficient data'. "
            "Response format: RAW TEXT ONLY."

        )
        },
        {
            'role': 'user',
            'content': f'Below is a request from a user along with history. Please identify the task and execute it accurately using the provided context. user_input = {user_input}.'
                       f'And this is history = {history}. Only use the history if its relevant for the current task else discard the history and work on user input.'
        }
    ]
    try:
        response = chat(model=model_name, messages=messages,
                        options={'temperature': 0.3, 'num_ctx': 8192, 'keep_alive': '10m'},
                        stream=False
                        )

        return response['message']['content'], model_name, response['message']['role']
        # print(response['message']['content'])
    except Exception as e:
        return f'Error connecting to Ollama : {str(e)}'
# AI_response("What ia the capital of India?")