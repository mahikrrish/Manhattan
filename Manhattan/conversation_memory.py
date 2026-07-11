import threading
import pandas as pd
import time
from datetime import datetime
import database

class ConversationMemory(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.performance_log = {}
        self.performance_log['component'] = 'MemoryManagement'
    def run(self, nl_processed_data, conversation_id = None):
        self.performance_log['conversation_id'] = conversation_id
        return self.memory_management(nl_processed_data)
    def retrieve_conversation(self, row_limit = 10):
        past_conversation = database.log().retrieve_conversation(row_limit)
        past_conversation = past_conversation.loc[:, ['raw_text', 'processed_text', 'memorymgmt_input', 'ai_response']]
        return past_conversation
    def memory_management(self, nl_processed_data):
        self.performance_log['start_time'] = time.time()
        memorymgmt_input = []
        conversation = self.retrieve_conversation(row_limit = 10)
        for i in range(conversation.index.start, conversation.index.stop):
            memorymgmt_input.append({
                "role": "user",
                "content": conversation.processed_text[i],
            })
            memorymgmt_input.append({
                "role": "assistant",
                "content": conversation.ai_response[i]
            })
        memorymgmt_input.append(
            {
                "role": "user",
                "content": nl_processed_data
            }
        )
        self.performance_log['end_time'] = time.time()
        self.performance_log['status'] = 'Success'
        self.performance_log['error_message'] = None
        return memorymgmt_input

    def performance_monitor(self):
        now = datetime.now()
        self.performance_log['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.performance_log['duration'] = (self.performance_log['end_time'] -
                                            self.performance_log['start_time'])
        database.log().performance_monitor(data=self.performance_log)

