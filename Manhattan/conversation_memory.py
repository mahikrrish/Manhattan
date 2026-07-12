import threading
import pandas as pd
import time
from datetime import datetime
from mysql.connector import DatabaseError

import database

class ConversationMemory(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.performance_log = {}
        self.performance_log['component'] = 'ConversationMemory'
    def run(self, nl_processed_data, conversation_id = None):
        self.performance_log['conversation_id'] = conversation_id
        memory_data = self.conversation_context(nl_processed_data)
        if memory_data:
            return memory_data
        else:
            return 'Error Occurred! Cannot be processed. Please check the logs.'
    def retrieve_conversation(self, row_limit = 10):
        try:
            past_conversation = database.log().retrieve_conversation(row_limit)
            past_conversation = past_conversation.loc[:, ['raw_text', 'processed_text', 'ai_response']]
            return past_conversation
        except (KeyError, DatabaseError) as e:
            raise
    def conversation_context(self, nl_processed_data):
        self.performance_log['start_time'] = time.time()
        try:
            conversation_history = []
            conversation = self.retrieve_conversation(row_limit=10)
            for i in range(conversation.index.start, conversation.index.stop):
                conversation_history.append({
                    "role": "user",
                    "content": conversation.processed_text[i],
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": conversation.ai_response[i]
                })
            conversation_history.append(
                {
                    "role": "user",
                    "content": nl_processed_data
                }
            )
            self.performance_log['status'] = 'Success'
            self.performance_log['error_message'] = None
            return conversation_history
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
        database.log().performance_monitor(data=self.performance_log)

