import natural_language_processing
import time
import database
from datetime import datetime
import manhattan
from Manhattan.speech_recognition import SpeechRecognition
import pandas as pd

stt = SpeechRecognition()
nlp = natural_language_processing.NaturalLanguageProcessing()
manh = manhattan.Manhattan()
db = database.DatabaseManager()

def process_conversation(conv_data):
    conv_data['processed_text'] = nlp.run(raw_text=conv_data['raw_text'],
                                          conversation_id=conv_data['conversation_id'])
    conv_data['ai_response'], conv_data['conversationmemory_input'] = manh.run(nl_processed_data=conv_data['processed_text'],
                                                                               conversation_id=conv_data['conversation_id'])
    print('AI Response: ', conv_data['ai_response'])
    conv_data['run_end_time'] = time.time()
    if conv_data['ai_response'] is not None:
        conv_data['status'] = 'Success'
    else:
        conv_data['status'] = 'Error'
    conv_data['error_message'] = None
    db.inject_conversation(conv_data=conv_data)

print("Welcome to Manhattan")
df = db.retrieve_conversation(row_limit=10)
df = df.loc[:, ['raw_text', 'ai_response']]
for i in range(df.index.start, df.index.stop):
    if pd.notna(df.raw_text[i]) and pd.notna(df.ai_response[i]):
        print('User: ', df.raw_text[i])
        print('AI Response: ', df.ai_response[i])
while True:
    conv_data = {}
    now = datetime.now()
    conv_data['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
    conv_data['input_mode'] = input("Please select type of input: \n"
                       "1. Text \n"
                       "2. Voice \n")
    conv_data['run_start_time'] = time.time()
    conv_data['conversation_id'] = db.create_conversation(input_mode = conv_data['input_mode'])
    if conv_data['input_mode'] == "Voice":
        conv_data['raw_text'] = stt.run(conversation_id=conv_data['conversation_id'])
        print('User: ', conv_data['raw_text'])
        if conv_data['raw_text'] is not None:
            process_conversation(conv_data)
    else:
        conv_data['raw_text'] = input("User: ")
        process_conversation(conv_data)
    next_run = input('Do you want to continue ? (y/n): ')
    if next_run.lower() == 'y':
        pass
    else:
        break
