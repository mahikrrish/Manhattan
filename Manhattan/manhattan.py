import json
from ollama import chat
import time
from datetime import datetime
import threading
import database
import conversation_memory

class Manhattan(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.model_name = 'llama3.2:3b'
        self.performance_log = {}
        self.performance_log['component'] = 'Manhattan'
    def run(self, nl_processed_data, conversation_id = None):
        self.performance_log['conversation_id'] = conversation_id
        memory_data  = conversation_memory.ConversationMemory().run(nl_processed_data, conversation_id)
        if memory_data != 'Error Occurred! Cannot be processed. Please check the logs.':
            return self.chat(memory_data), memory_data
        else:
            return memory_data
    def chat(self, user_input):
        try:
            self.performance_log['start_time'] = time.time()
            messages = [
                {
                    'role': 'system',
                    'content': ('''
                    You are Manhattan, an offline AI assistant.
                    Personality:
                        - Intelligent, witty and occasionally sarcastic.
                        - Use light, playful sarcasm when it naturally fits the conversation.
                        - Never use sarcasm to insult, belittle or humiliate the user.
                        - Keep humor brief and relevant.
                    Behavior:
                        - Answer the user's latest request accurately.
                        - Use previous conversation only when relevant.
                        - Do not reveal internal reasoning.
                        - If there is insufficient information, say so clearly.
                        - Respond in plain text.
                    '''
                    )
                }
            ]
            messages.extend(user_input)
            response = chat(model=self.model_name, messages=messages,
                            options={'temperature': 0.3, 'num_ctx': 16384, 'keep_alive': '10m'},
                            stream=False
                            )
            self.performance_log['status'] = 'Success'
            self.performance_log['error_message'] = None
            return response['message']['content']
        except Exception as e:
            self.performance_log['status'] = 'Error'
            self.performance_log['error_message'] = f'{type(e).__name__}: {e}'
            return None
        finally:
            self.performance_log['end_time'] = time.time()
            self.performance_monitor()
    def performance_monitor(self):
        now = datetime.now()
        self.performance_log['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.performance_log['duration'] = (self.performance_log['end_time'] -
                                            self.performance_log['start_time'])
        database.log().performance_monitor(perf_data=self.performance_log)
