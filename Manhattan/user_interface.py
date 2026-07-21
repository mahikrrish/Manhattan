import threading
from pathlib import Path
import customtkinter
import pandas as pd
import warnings
from PIL import Image
warnings.filterwarnings('ignore') #To suppress all warnings across the entire script

import natural_language_processing
import time
import database
from datetime import datetime
import manhattan
from Manhattan.speech_recognition import SpeechRecognition


stt = SpeechRecognition()
nlp = natural_language_processing.NaturalLanguageProcessing()
manh = manhattan.Manhattan()
db = database.DatabaseManager()



class UserInterface(threading.Thread, customtkinter.CTk):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        customtkinter.CTk.__init__(self)
        self.base_dir = Path(__file__).resolve().parent
        self.conv_data = {}
        self.conv_data['input_mode'] = "Text"
        self.window_color = "#F2F2F2"

        self.header_frame_fg_color = "#1F3A5F"
        # self.header_frame_bg_color = "#F2F2F2"
        self.BG_GRAY = "#ABB2B9"
        self.BG_COLOR = "#17202A"
        self.TEXT_COLOR = "#EAECEE"

        self.chat_frame_color = "#F2F2F2"
        self.chat_scrollable_frame_color = "#F2F2F2"
        self.user_bubble_color = "#DACFFA"
        self.ai_bubble_color = "#C9F1E2"

        self.input_frame_color = "#F2F2F2"
        self.textbox_border_color = "#FFC0CB"

        self.corner_radius = 20

        self.font = customtkinter.CTkFont(family = "Aptos (Body)", size = 18)
    def run(self):
        self.window()
        self.mainloop()
    def window(self):
        self.title('Manhattan')
        self.geometry('1200x700')
        self.minsize(900,600)
        self.configure(fg_color=self.window_color)

        window_icon_path = self.base_dir/"assets"/"Manhattan Icon.ico"
        self.iconbitmap(str(window_icon_path))
        self.resizable(width=True, height=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header_frame()
        self.chat_frame()
        self.input_frame()

    def header_frame(self):
        header_frame = customtkinter.CTkFrame(self, fg_color=self.header_frame_fg_color, height=70,
                                              corner_radius=self.corner_radius, border_color=None)
        header_frame.pack(fill='x', padx = 100)
        header_frame.pack_propagate(False)
        title_label = customtkinter.CTkLabel(header_frame, text="Manhattan - Offline AI Assistant", fg_color="transparent",
                                            pady=10, text_color="White",
                                            width=20, height=1, font=customtkinter.CTkFont(family = "Cooper Black", size = 28), anchor="center")
        title_label.place(relx=0.5, rely=0.5, anchor="center")
        developer_label = customtkinter.CTkLabel(header_frame, text="Developed by Sai Krishna Mahidhar Devulapalli", fg_color="transparent",
                                                 pady=10, text_color="White",
                                                 width=20, height=1, font=customtkinter.CTkFont(family = "Cooper Black", size = 10))
        developer_label.place(relx = 0.98, rely = 0.85, anchor = "se")

    def chat_frame(self):
        chat_frame = customtkinter.CTkFrame(self, fg_color=self.chat_frame_color)
        chat_frame.pack(fill='both', expand=True)
        chat_frame.pack_propagate(False)
        self.chat_messages = customtkinter.CTkScrollableFrame(chat_frame, fg_color=self.chat_scrollable_frame_color)
        self.chat_messages.pack(fill='both', expand=True, padx=100, pady=30)
        self.conversation_history()
        self.update_idletasks()
        self.after(
            100,
            lambda: self.chat_messages._parent_canvas.yview_moveto(1.0)
        )

    def input_frame(self):
        input_frame = customtkinter.CTkFrame(self, fg_color=self.input_frame_color,
                                             height=100, border_color=None, corner_radius=0)
        input_frame.pack(fill='x')
        input_frame.pack_propagate(False)

        send_button_icon_path = self.base_dir/"assets"/"send-button.png"
        send_button_raw_image = Image.open(send_button_icon_path)
        button_image = customtkinter.CTkImage(light_image=send_button_raw_image, size=(40,40))

        microphone_icon_path = self.base_dir/"assets"/"microphone.png"
        microphone_raw_image = Image.open(microphone_icon_path)
        microphone_image = customtkinter.CTkImage(light_image=microphone_raw_image, size=(40,40))

        self.textbox = customtkinter.CTkTextbox(input_frame, corner_radius=self.corner_radius, border_color=self.textbox_border_color, border_width=2,
                                                font = self.font)
        self.textbox.pack(side="left", expand=True, fill="x", padx=(100,0), pady=15)
        self.microphone = customtkinter.CTkButton(input_frame, width=0, text="", command=self.microphone_recording, corner_radius=self.corner_radius,
                                                  height=45, image=microphone_image, fg_color="transparent", hover_color=None)
        self.microphone.pack(side="left", pady=15, padx=(10,10))
        self.submit_button = customtkinter.CTkButton(input_frame, width=0, text="", command=self.read_textbox, corner_radius=self.corner_radius,
                                                     height=45, image=button_image,fg_color="transparent",  hover_color=None)
        self.submit_button.pack(padx=(3,73), pady=15, side="right")

    def display_message(self, input_text, role):
        if role == "user":
            fg_color = self.user_bubble_color
            # border_color = "#FADADD"
            anchor = "e"
        else:
            fg_color = self.ai_bubble_color
            # border_color = "#E6E6FA"
            anchor = "w"
        message_frame = customtkinter.CTkFrame(self.chat_messages, fg_color=fg_color, corner_radius=self.corner_radius)
        message = customtkinter.CTkLabel(message_frame, text=f"{input_text}", wraplength=700, font=self.font, justify="left", compound="center")
        message_frame.pack(anchor=anchor, pady=10, padx=10)
        message.pack(pady=15, padx=15)
        self.update_idletasks()
        self.after(
            10,
            lambda: self.chat_messages._parent_canvas.yview_moveto(1.0)
        )


    def conversation_history(self):
        df = db.retrieve_conversation(row_limit=10)
        df = df.loc[:, ['raw_text', 'ai_response']]
        for i in range(df.index.start, df.index.stop):
            if pd.notna(df.raw_text[i]) and pd.notna(df.ai_response[i]):
                self.display_message(df.raw_text[i], role ="user")
                self.display_message(df.ai_response[i], role ="ai")

    def read_textbox(self):
        self.conv_data['raw_text'] = self.textbox.get("0.0", "end")
        if not self.conv_data.get('run_start_time'):
            self.conv_data['run_start_time'] = time.time()
        self.textbox.delete("0.0", "end")
        self.display_message(self.conv_data['raw_text'], role="user")
        self.process_initiate()
        self.process_carry_forward()
    def microphone_recording(self):
        self.conv_data['input_mode'] = "Voice"
        self.process_initiate()
        self.conv_data['run_start_time'] = time.time()
        microphone_text = stt.run(conversation_id=self.conv_data['conversation_id'])
        self.textbox.insert("end", microphone_text)

    def process_initiate(self):
        now = datetime.now()
        self.conv_data['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        if not self.conv_data.get('conversation_id'):
            self.conv_data['conversation_id'] = db.create_conversation(input_mode=self.conv_data['input_mode'])
    def process_carry_forward(self):
        try:
            self.conv_data['processed_text'] = nlp.run(raw_text=self.conv_data['raw_text'],
                                                       conversation_id=self.conv_data['conversation_id'])
            self.conv_data['ai_response'], self.conv_data['conversationmemory_input'] = manh.run(
                nl_processed_data=self.conv_data['processed_text'],
                conversation_id=self.conv_data['conversation_id'])
            self.display_message(self.conv_data['ai_response'], role="ai")
            if self.conv_data['ai_response'] is not None:
                self.conv_data['status'] = 'Success'
                self.conv_data['error_message'] = None
            else:
                raise Exception
        except Exception as e:
            self.conv_data['status'] = 'Error'
            self.conv_data['error_message'] = f'{type(e).__name__}: {e}'
        finally:
            self.conv_data['run_end_time'] = time.time()
            db.inject_conversation(conv_data=self.conv_data)
            self.conv_data.clear()
            self.conv_data['input_mode'] = "Text"


if __name__ == '__main__':
    def close_splash():
        splash.destroy() # Close the splash window
        UserInterface().run() # Open the main program window
    splash = customtkinter.CTk()
    splash.geometry("550x550")
    splash.overrideredirect(True)
    base_dir = Path(__file__).resolve().parent
    image_path = base_dir/"assets"/"Manhattan Icon.png"
    raw_img = Image.open(image_path)
    splash_img = customtkinter.CTkImage(light_image=raw_img, size=(550, 550))
    img_label = customtkinter.CTkLabel(splash, text="", image=splash_img)
    img_label.pack(expand=True)
    splash.after(3000, close_splash)
    splash.mainloop()
