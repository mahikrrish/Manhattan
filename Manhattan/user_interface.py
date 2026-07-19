import threading
from pathlib import Path
import customtkinter
import pandas as pd
import warnings
warnings.filterwarnings('ignore') #To suppress all warnings across the entire script

# import natural_language_processing
# import customtkinter as ctk
# import time
import database
# from datetime import datetime
# import manhattan
# from Manhattan.speech_recognition import SpeechRecognition


# stt = SpeechRecognition()
# nlp = natural_language_processing.NaturalLanguageProcessing()
# manh = manhattan.Manhattan()
db = database.DatabaseManager()

# def process_conversation(conv_data):
#     conv_data['processed_text'] = nlp.run(raw_text=conv_data['raw_text'],
#                                           conversation_id=conv_data['conversation_id'])
#     conv_data['ai_response'], conv_data['conversationmemory_input'] = manh.run(nl_processed_data=conv_data['processed_text'],
#                                                                                conversation_id=conv_data['conversation_id'])
#     print('AI Response: ', conv_data['ai_response'])
#     conv_data['run_end_time'] = time.time()
#     if conv_data['ai_response'] is not None:
#         conv_data['status'] = 'Success'
#     else:
#         conv_data['status'] = 'Error'
#     conv_data['error_message'] = None
#     db.inject_conversation(conv_data=conv_data)

# print("Welcome to Manhattan")

# while True:
#     conv_data = {}
#     now = datetime.now()
#     conv_data['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
#     conv_data['input_mode'] = input("Please select type of input: \n"
#                        "1. Text \n"
#                        "2. Voice \n")
#     conv_data['run_start_time'] = time.time()
#     conv_data['conversation_id'] = db.create_conversation(input_mode = conv_data['input_mode'])
#     if conv_data['input_mode'] == "Voice":
#         conv_data['raw_text'] = stt.run(conversation_id=conv_data['conversation_id'])
#         print('User: ', conv_data['raw_text'])
#         if conv_data['raw_text'] is not None:
#             process_conversation(conv_data)
#     else:
#         conv_data['raw_text'] = input("User: ")
#         process_conversation(conv_data)
#     next_run = input('Do you want to continue ? (y/n): ')
#     if next_run.lower() == 'y':
#         pass
#     else:
#         break

class UserInterface(threading.Thread, customtkinter.CTk):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        customtkinter.CTk.__init__(self)
        self.BG_GRAY = "#ABB2B9"
        self.BG_COLOR = "#17202A"
        self.TEXT_COLOR = "#EAECEE"
    def run(self):
        self.window()
        self.mainloop()
    def window(self):
        self.title('Manhattan')
        self.geometry('1200x700')
        self.minsize(900,600)

        BASE_DIR = Path(__file__).resolve().parent
        ICON_PATH = BASE_DIR/"assets"/"Manhattan Icon.ico"
        self.iconbitmap(str(ICON_PATH))
        self.resizable(width=True, height=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header_frame()
        self.chat_frame()
        self.input_frame()

    def header_frame(self):
        header_frame = customtkinter.CTkFrame(self, fg_color="Blue", height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        label = customtkinter.CTkLabel(header_frame, text="Manhattan", bg_color=self.BG_COLOR, fg_color=self.TEXT_COLOR,
                                            pady=10,
                                            width=20, height=1)
        label.pack(pady=10)

    def chat_frame(self):
        chat_frame = customtkinter.CTkFrame(self, fg_color="Green")
        chat_frame.pack(fill='both', expand=True)
        chat_frame.pack_propagate(False)
        self.chat_messages = customtkinter.CTkScrollableFrame(chat_frame, fg_color="White")
        self.chat_messages.pack(fill='both', expand=True, padx=15, pady=15)
        self.conversation_history()


    def input_frame(self):
        input_frame = customtkinter.CTkFrame(self, fg_color="Red", height=100)
        input_frame.pack(fill='x')
        input_frame.pack_propagate(False)

        def read_textbox():
            all_text = self.textbox.get("0.0", "end")
            self.textbox.delete("0.0", "end")
            self.display_message(all_text, role ="user")

        self.textbox = customtkinter.CTkTextbox(input_frame)
        self.textbox.pack(side="left", expand=True, fill="x", padx=10, pady=20)
        self.submit_button = customtkinter.CTkButton(input_frame, text="Submit", command=read_textbox)
        self.submit_button.pack(padx=10, pady=20, side="right")

    def display_message(self, input_text, role):
        message_frame = customtkinter.CTkFrame(self.chat_messages, fg_color='Light Grey', corner_radius=20)
        message = customtkinter.CTkLabel(message_frame, text=f"{input_text}", wraplength=500)
        if role == 'user':
            message_frame.pack(anchor="e", pady=10, padx=10)
        else:
            message_frame.pack(anchor="w", pady=10, padx=10)
        message.pack(pady=10, padx=8)

    def conversation_history(self):
        df = db.retrieve_conversation(row_limit=10)
        df = df.loc[:, ['raw_text', 'ai_response']]
        for i in range(df.index.start, df.index.stop):
            if pd.notna(df.raw_text[i]) and pd.notna(df.ai_response[i]):
                self.display_message(df.raw_text[i], role ="user")
                self.display_message(df.ai_response[i], role ="ai")

if __name__ == '__main__':
    UserInterface().run()
