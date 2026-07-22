"""
Manhattan User Interface
========================

This module implements the graphical user interface (GUI)
for the Manhattan Offline AI Assistant.

The interface is developed using CustomTkinter and serves
as the primary interaction layer between the user and the
backend processing components.

Major responsibilities of this module include:

    • Constructing the application window.
    • Managing graphical user interface components.
    • Receiving user input through both keyboard and
      speech recognition.
    • Displaying user and assistant conversations.
    • Coordinating execution of Natural Language
      Processing and the Manhattan reasoning engine.
    • Managing conversation metadata and execution
      timing.
    • Recording conversation information for database
      persistence and performance monitoring.
    • Executing long-running backend operations using
      worker threads to maintain GUI responsiveness.
    • Providing exception handling and user feedback
      through graphical message dialogs.

Architecture
------------

The UserInterface class acts as the central coordinator
for all frontend activities.

The module communicates with the following backend
components:

    • SpeechRecognition
    • NaturalLanguageProcessing
    • Manhattan
    • DatabaseManager

Long-running operations such as speech recognition and
AI processing execute in background worker threads,
while all graphical interface updates are performed
within the main GUI thread using CustomTkinter's
event loop.

Author:
    Sai Krishna Mahidhar Devulapalli

Project:
    Manhattan - Offline AI Assistant
"""

from datetime import datetime
from pathlib import Path
import os
import warnings
import time
import threading
from CTkMessagebox import CTkMessagebox
import customtkinter
import pandas as pd
from PIL import Image
import manhattan
from Manhattan.speech_recognition import SpeechRecognition
import natural_language_processing
warnings.filterwarnings('ignore') #To suppress all warnings across the entire script
import database

class UserInterface(customtkinter.CTk):
    """
    Graphical user interface for the Manhattan Offline AI Assistant.

    The UserInterface class serves as the primary frontend of
    the Manhattan application and coordinates all interactions
    between the user and backend processing components.

    The class is responsible for:

        • Constructing and managing the graphical user interface.
        • Receiving user input through both keyboard and
          speech recognition.
        • Displaying conversations between the user and the
          Manhattan AI Assistant.
        • Managing conversation metadata throughout the
          execution lifecycle.
        • Coordinating Natural Language Processing, Large
          Language Model inference and database operations.
        • Recording execution statistics for performance
          monitoring.
        • Executing long-running operations using worker
          threads to maintain a responsive user interface.
        • Providing graphical feedback through dialog boxes
          and status messages.

    The class owns instances of the following backend
    components:

        • SpeechRecognition
        • NaturalLanguageProcessing
        • Manhattan
        • DatabaseManager

    Inheritance:

        customtkinter.CTk

            Provides the root application window and the
            CustomTkinter event loop used throughout the
            application.
    """
    def __init__(self):
        """
        Initialize the Manhattan graphical user interface.

        This constructor initializes the root CustomTkinter window,
        creates all backend component instances required by the GUI,
        and prepares the application's visual configuration.

        Backend components including Speech Recognition, Natural
        Language Processing, Manhattan reasoning engine and Database
        Manager are instantiated once during application startup and
        remain available throughout the lifetime of the application.

        The constructor also initializes the shared conversation
        dictionary used to exchange data between GUI events,
        backend processing components and database logging.

        In addition, visual settings such as colors, fonts,
        corner radius and project resource paths are configured
        for later use while constructing the interface.

        Attributes:

            stt (SpeechRecognition):
                Speech recognition component responsible for
                converting microphone audio into text.

            nlp (NaturalLanguageProcessing):
                Component responsible for preprocessing user
                input before language model inference.

            manh (Manhattan):
                Large Language Model reasoning component.

            db (DatabaseManager):
                Database interface used for conversation
                persistence and performance logging.

            conv_data (dict):
                Shared dictionary containing execution data
                exchanged between GUI and backend components.
        """
        super().__init__()
        self.stt = SpeechRecognition()
        self.nlp = natural_language_processing.NaturalLanguageProcessing()
        self.manh = manhattan.Manhattan()
        self.db = database.DatabaseManager()
        self.base_dir = Path(__file__).resolve().parent
        self.conv_data = {}
        self.conv_data['input_mode'] = "Text"
        self.window_color = "#F2F2F2"
        self.header_frame_fg_color = "#1F3A5F"
        self.chat_frame_color = "#F2F2F2"
        self.chat_scrollable_frame_color = "#F2F2F2"
        self.user_bubble_color = "#DACFFA"
        self.ai_bubble_color = "#C9F1E2"
        self.input_frame_color = "#F2F2F2"
        self.button_fg_color = "#F2F2F2"
        self.textbox_border_color = "#FFC0CB"
        self.corner_radius = 20
        self.font = customtkinter.CTkFont(family = "Aptos (Body)", size = 18)

    def run(self):
        """
        Start the Manhattan desktop application.

        This method serves as the public entry point for the
        graphical interface.

        It first constructs the complete application window
        by calling the window() method and then transfers
        execution control to CustomTkinter's main event loop.

        The application remains active until the user closes
        the main window.

        Returns:

            None
        """
        self.window()
        self.mainloop()

    def window(self):
        """
        Configure the main application window.

        This method applies all top-level window properties
        including title, dimensions, minimum size, icon,
        resizing behaviour and grid configuration.

        Once the main window has been configured, it
        constructs each major section of the interface by
        creating:

            - Header Frame
            - Chat Frame
            - Input Frame

        Finally, keyboard shortcuts are registered,
        allowing the Enter key to submit user input.

        Returns:

            None
        """
        self.title('Manhattan')
        self.geometry('1200x700')
        self.minsize(900,600)
        self.configure(fg_color=self.window_color)

        window_icon_path = os.path.join(self.base_dir,"assets","Manhattan Icon.ico")
        self.iconbitmap(str(window_icon_path))
        self.resizable(width=True, height=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header_frame()
        self.chat_frame()
        self.input_frame()
        self.textbox.bind("<Return>", self.enter_key_action)

    def header_frame(self):
        """
        Create the application header.

        This method constructs the header section displayed
        at the top of the application window.

        The header contains the project title along with
        developer information and applies the project's
        visual styling including colours, fonts and
        positioning.

        Returns:

            None
        """
        header_frame = customtkinter.CTkFrame(self, fg_color=self.header_frame_fg_color, height=70,
                                              corner_radius=self.corner_radius, border_color=None)
        header_frame.pack(fill='x', padx = 100)
        header_frame.pack_propagate(False)
        title_label = customtkinter.CTkLabel(header_frame, text="Manhattan - Offline AI Assistant",
                                             fg_color="transparent", pady=10, text_color="White",
                                            width=20, height=1,
                                             font=customtkinter.CTkFont(family = "Cooper Black",
                                                                        size = 28),
                                             anchor="center")
        title_label.place(relx=0.5, rely=0.5, anchor="center")
        developer_label = customtkinter.CTkLabel(header_frame,
                                                 text="Developed by Sai Krishna "
                                                      "Mahidhar Devulapalli",
                                                 fg_color="transparent",
                                                 pady=10, text_color="White",
                                                 width=20, height=1,
                                                 font=customtkinter.CTkFont(family = "Cooper Black",
                                                                            size = 10))
        developer_label.place(relx = 0.98, rely = 0.85, anchor = "se")

    def retrieve_conversation(self):
        """
        Retrieve and display previous conversations.

        This method requests recent conversation history
        through the conversation_history() method.

        If retrieval completes successfully, a confirmation
        message is displayed to the user.

        If conversation retrieval fails, error handling is
        performed by conversation_history().

        Returns:

            None
        """
        action_response = self.conversation_history()
        if action_response:
            self.after(
                0,
                lambda: CTkMessagebox(title="Success",
                                      message="Previous Data Retrieved", icon="check")
            )

    def chat_frame(self):
        """
        Create the conversation display area.

        This method constructs the primary chat region of
        the application.

        A scrollable frame is created to display both user
        and assistant messages.

        The conversation retrieval button is also created.
        If the associated image resource cannot be loaded,
        a text-based fallback button is created instead,
        allowing the application to continue operating.

        After construction, the scroll position is moved to
        the bottom of the conversation window.

        Returns:

            None
        """
        chat_frame = customtkinter.CTkFrame(self, fg_color=self.chat_frame_color)
        chat_frame.pack(fill='both', expand=True)
        chat_frame.pack_propagate(False)
        self.chat_messages = customtkinter.CTkScrollableFrame(chat_frame,
                                                              fg_color=self.chat_scrollable_frame_color)
        self.chat_messages.pack(fill='both', expand=True, padx=100, pady=30)

        try:
            retrieve_button_icon_path = os.path.join(self.base_dir, "assets", "data-retrieval.png")
            retrieve_button_raw_image = Image.open(retrieve_button_icon_path)
            retrieve_button_image = customtkinter.CTkImage(light_image=retrieve_button_raw_image,
                                                           size=(40, 40))

            self.retrieve_conversation_button = customtkinter.CTkButton(chat_frame,
                                                                        fg_color=self.button_fg_color,
                                                                        text="",
                                                                        image=retrieve_button_image,
                                                                        command=self.retrieve_conversation,
                                                                        corner_radius=self.corner_radius,
                                                                        width=0, height=45)
            self.retrieve_conversation_button.pack(side="right", padx=10, pady=10)
        except Exception as e:
            self.after(
                0,
                lambda: CTkMessagebox(title="Warning Message!",
                                      message=f'Image loading failed. {type(e).__name__}: {e}. '
                                              f'But messages will retrieve ', icon="warning")
            )
            self.retrieve_conversation_button = customtkinter.CTkButton(chat_frame,
                                                                        fg_color=self.button_fg_color,
                                                                       text="Retrieve",
                                                                       command=self.retrieve_conversation,
                                                                       corner_radius=self.corner_radius,
                                                                       width=0, height=45)
            self.retrieve_conversation_button.pack(side="right", padx=10, pady=10)

        self.update_idletasks()
        self.after(
            100,
            lambda: self.chat_messages._parent_canvas.yview_moveto(1.0)
        )

    def input_frame(self):
        """
        Create the user input section.

        This method constructs the lower input area of the
        application.

        The section contains:

            - Multi-line text input
            - Microphone button
            - Submit button

        Button images are loaded from the project assets.
        If image loading fails, equivalent text-based
        buttons are created so that application
        functionality remains available.

        Returns:

            None
        """
        input_frame = customtkinter.CTkFrame(self, fg_color=self.input_frame_color,
                                             height=100, border_color=None, corner_radius=0)
        input_frame.pack(fill='x')
        input_frame.pack_propagate(False)

        self.textbox = customtkinter.CTkTextbox(input_frame,
                                                corner_radius=self.corner_radius,
                                                border_color=self.textbox_border_color,
                                                border_width=2,
                                                font=self.font)
        self.textbox.pack(side="left", expand=True, fill="x", padx=(100, 0), pady=15)

        try:
            send_button_icon_path = os.path.join(self.base_dir, "assets", "send-button.png")
            send_button_raw_image = Image.open(send_button_icon_path)
            button_image = customtkinter.CTkImage(light_image=send_button_raw_image,
                                                  size=(40, 40))

            microphone_icon_path = os.path.join(self.base_dir, "assets", "microphone.png")
            microphone_raw_image = Image.open(microphone_icon_path)
            microphone_raw_image = Image.open(microphone_icon_path)
            microphone_image = customtkinter.CTkImage(light_image=microphone_raw_image,
                                                      size=(40, 40))

            self.microphone = customtkinter.CTkButton(input_frame, width=0, text="",
                                                      command=self.microphone_recording,
                                                      corner_radius=self.corner_radius,
                                                      height=45, image=microphone_image,
                                                      fg_color=self.button_fg_color)
            self.microphone.pack(side="left", pady=15, padx=(10, 10))
            self.submit_button = customtkinter.CTkButton(input_frame, width=0, text="",
                                                         command=self.read_textbox,
                                                         corner_radius=self.corner_radius,
                                                         height=45, image=button_image,
                                                         fg_color=self.button_fg_color)
            self.submit_button.pack(padx=(3, 73), pady=15, side="right")
        except Exception as e:
            self.after(
                0,
                lambda: CTkMessagebox(title="Warning Message!", message=f'Image loading failed. {type(e).__name__}: {e}. '
                                                                        f'But program will work ', icon="warning")
            )
            self.microphone = customtkinter.CTkButton(input_frame, width=0, text="Mic",
                                                      command=self.microphone_recording,
                                                      corner_radius=self.corner_radius,
                                                      height=45, fg_color=self.button_fg_color)
            self.microphone.pack(side="left", pady=15, padx=(10, 10))
            self.submit_button = customtkinter.CTkButton(input_frame, width=0, text="Submit",
                                                         command=self.read_textbox,
                                                         corner_radius=self.corner_radius,
                                                         height=45, fg_color=self.button_fg_color)
            self.submit_button.pack(padx=(3, 73), pady=15, side="right")

    def display_message(self, input_text, role):
        """
        Display a chat message within the conversation area.

        This method creates and displays a message bubble inside
        the scrollable chat window.

        The appearance of the message is determined by the role
        parameter. User messages are right-aligned using the
        configured user bubble colour, while assistant messages
        are left-aligned using the assistant bubble colour.

        After displaying the message, the scrollable frame is
        automatically moved to the bottom so that the latest
        conversation remains visible without requiring manual
        scrolling.

        Args:

            input_text (str):
                Text message to be displayed within the chat
                interface.

            role (str):
                Specifies the sender of the message.

                Supported values:

                    "user"
                        Displays the message using the user
                        message style.

                    "ai"
                        Displays the message using the assistant
                        message style.

        Returns:

            None
        """
        if role == "user":
            fg_color = self.user_bubble_color
            anchor = "e"
        else:
            fg_color = self.ai_bubble_color
            anchor = "w"
        message_frame = customtkinter.CTkFrame(self.chat_messages,
                                               fg_color=fg_color,
                                               corner_radius=self.corner_radius)
        message = customtkinter.CTkLabel(message_frame, text=f"{input_text}",
                                         wraplength=700, font=self.font,
                                         justify="left", compound="center")
        message_frame.pack(anchor=anchor, pady=10, padx=10)
        message.pack(pady=15, padx=15)
        self.update_idletasks()
        self.after(
            10,
            lambda: self.chat_messages._parent_canvas.yview_moveto(1.0)
        )

    def conversation_history(self):
        """
        Retrieve and display previous conversations.

        This method retrieves the latest conversation records
        from the database and displays them sequentially within
        the chat interface.

        Only records containing both the user message and
        assistant response are displayed. Incomplete records
        are ignored to avoid presenting partially processed
        conversations.

        If retrieval succeeds, the method returns True.

        If an exception occurs during database retrieval or
        message display, an error dialog is presented to the
        user and False is returned.

        Returns:

            bool

                True
                    Conversation history was successfully
                    retrieved and displayed.

                False
                    Conversation retrieval failed due to an
                    unexpected exception.
        """
        try:
            df = self.db.retrieve_conversation(row_limit=30)
            df = df.loc[:, ['raw_text', 'ai_response']]
            for i in range(df.index.start, df.index.stop):
                if pd.notna(df.raw_text[i]) and pd.notna(df.ai_response[i]):
                    self.display_message(df.raw_text[i], role="user")
                    self.display_message(df.ai_response[i], role="ai")
            return True
        except Exception as e:
            self.after(
                0,
                lambda: CTkMessagebox(title="Error",
                                      message=f'{type(e).__name__}: {e}',
                                      icon="cancel")
            )
            return False

    def read_textbox(self):
        """
        Read user text input and initiate AI processing.

        This method serves as the primary entry point for text-
        based interactions.

        The method first validates that the textbox contains
        non-empty input after removing leading and trailing
        whitespace.

        If valid input exists, the following operations are
        performed:

            • Store the user's raw text.
            • Capture the process start time.
            • Clear the textbox.
            • Disable user controls.
            • Display the user's message.
            • Create conversation metadata.
            • Start the AI processing worker thread.

        Long-running AI operations are executed within a
        background thread to prevent the graphical interface
        from becoming unresponsive.

        Empty or whitespace-only input is ignored.

        Returns:

            None
        """
        if self.textbox.get("0.0", "end").strip():
            self.conv_data['raw_text'] = self.textbox.get("0.0", "end")
            if not self.conv_data.get('run_start_time'):
                self.conv_data['run_start_time'] = time.time()
            self.textbox.delete("0.0", "end")
            self.toggle_controls(state="disabled")
            self.display_message(self.conv_data['raw_text'], role="user")
            self.process_initiate()
            worker = threading.Thread(
                target=self.process_carry_forward,
                daemon=True
            )
            worker.start()

    def microphone_recording(self):
        """
        Initiate voice-based user input.

        This method serves as the entry point for microphone
        interaction.

        Before speech recognition begins, user controls are
        disabled to prevent multiple simultaneous requests.

        The input mode is updated to indicate voice input,
        conversation metadata is initialized and execution
        timing begins.

        Speech recognition is executed within a background
        worker thread to ensure that the graphical interface
        remains responsive while audio is being processed.

        Returns:

            None
        """
        self.toggle_controls(state="disabled")
        self.conv_data['input_mode'] = "Voice"
        self.process_initiate()
        self.conv_data['run_start_time'] = time.time()
        microphone_worker = threading.Thread(
            target = self.voice_worker,
            daemon = True,
        )
        microphone_worker.start()

    def voice_worker(self):
        """
        Execute speech recognition in a background thread.

        This worker method performs speech recognition without
        blocking the graphical user interface.

        The Speech Recognition component records audio,
        transcribes speech into text and returns the recognized
        result.

        If speech recognition succeeds, the recognized text is
        inserted into the textbox, allowing the user to review
        and edit the transcription before submitting it for AI
        processing.

        If speech recognition fails, an error dialog is
        displayed requesting the user to try again.

        Regardless of success or failure, all user controls are
        re-enabled before the worker terminates.

        This method is intended to execute only within a worker
        thread.

        Returns:

            None
        """
        try:
            microphone_text = self.stt.run(conversation_id=self.conv_data['conversation_id'])
            if microphone_text:
                self.after(
                    0,
                    lambda: self.toggle_controls(state="normal")
                )
                self.after(
                    0,
                    lambda: self.textbox.insert("end", microphone_text)
                )
            else:
                raise Exception
        except Exception as e:
            self.after(
                0,
                lambda: CTkMessagebox(title="Error!",
                                      message=f'Speech Recognition failed. {type(e).__name__}: {e}. '
                                              f'Kindly try again. ',
                                      icon="warning")
            )
        finally:
            self.after(
                0,
                lambda: self.toggle_controls(state="normal")
            )

    def process_initiate(self):
        """
        Initialize conversation metadata.

        This method prepares conversation information required
        by backend processing before NLP and AI execution begin.

        If a conversation timestamp has not already been
        assigned, the current date and time are recorded.

        If a conversation identifier has not already been
        created, a new conversation entry is generated within
        the database and its identifier is stored for use
        throughout the remainder of the processing pipeline.

        Existing values are preserved when continuing an
        existing execution.

        Returns:

            None
        """
        now = datetime.now()
        if not self.conv_data.get('created_at'):
            self.conv_data['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        if not self.conv_data.get('conversation_id'):
            self.conv_data['conversation_id'] = self.db.create_conversation(
                input_mode=self.conv_data['input_mode'])

    def process_carry_forward(self):
        """
        Execute the complete backend processing pipeline.

        This worker method performs the primary processing
        workflow for text-based user interaction.

        The following operations are executed sequentially:

            • Natural Language Processing
            • Manhattan reasoning engine
            • Response validation
            • Display assistant response
            • Record execution status
            • Persist conversation data
            • Reset execution state

        If processing completes successfully, the assistant
        response is displayed and the execution status is
        recorded as Success.

        If any component fails, execution status is recorded
        as Error, the associated error message is stored and
        an error dialog is presented to the user.

        Regardless of execution outcome, conversation data is
        persisted within the database, execution timing is
        completed, temporary conversation state is cleared and
        GUI controls are restored.

        This method is intended to execute only within a worker
        thread.

        Returns:

            None
        """
        try:
            self.conv_data['processed_text'] = self.nlp.run(raw_text=self.conv_data['raw_text'],
                                                       conversation_id=self.conv_data['conversation_id'])
            self.conv_data['ai_response'], self.conv_data['conversationmemory_input'] = self.manh.run(
                nl_processed_data=self.conv_data['processed_text'],
                conversation_id=self.conv_data['conversation_id'])
            if self.conv_data['ai_response'] is not None:
                self.conv_data['status'] = 'Success'
                self.conv_data['error_message'] = None
            else:
                raise Exception
            self.after(
                0,
                lambda: self.display_message(self.conv_data['ai_response'], role="ai")
            )
        except Exception as e:
            self.conv_data['status'] = 'Error'
            self.conv_data['error_message'] = f'{type(e).__name__}: {e}'
            self.after(
                0,
                lambda: CTkMessagebox(title="Error",
                                      message=self.conv_data['error_message'],
                                      icon="cancel")
            )
        finally:
            self.conv_data['run_end_time'] = time.time()
            self.db.inject_conversation(conv_data=self.conv_data)
            self.conv_data.clear()
            self.conv_data['input_mode'] = "Text"
            self.after(
                0,
                lambda: self.toggle_controls(state = "normal")
            )

    def toggle_controls(self, state):
        """
        Enable or disable user interface controls.

        This method updates the interactive state of all user
        input controls within the application.

        The following controls are updated simultaneously:

            • User textbox
            • Microphone button
            • Submit button
            • Conversation retrieval button

        Disabling controls prevents users from initiating
        multiple concurrent requests while backend processing
        or speech recognition is in progress.

        Args:

            state (str):
                Desired widget state.

                Supported values:

                    "normal"
                        Enables all controls.

                    "disabled"
                        Disables all controls.

        Returns:

            None
        """
        self.textbox.configure(state=state)
        self.microphone.configure(state=state)
        self.submit_button.configure(state=state)
        self.retrieve_conversation_button.configure(state=state)

    def enter_key_action(self, event):
        """
        Handle Enter key submission.

        This method is invoked whenever the user presses the
        Enter key while the textbox has keyboard focus.

        The current textbox contents are processed in the same
        manner as clicking the Submit button.

        Returning the string "break" prevents the default
        textbox behaviour of inserting a newline character,
        thereby allowing the Enter key to function as a
        message submission shortcut.

        Args:

            event (tkinter.Event):
                Keyboard event automatically supplied by
                CustomTkinter.

        Returns:

            str

                "break"
                    Prevents further processing of the Enter
                    key event by the textbox widget.
        """
        self.read_textbox()
        return "break"

if __name__ == '__main__':
    def close_splash():
        splash.destroy() # Close the splash window
        UserInterface().run() # Open the main program window
    splash = customtkinter.CTk()
    splash.geometry("550x550")
    splash.overrideredirect(True)
    base_dir = Path(__file__).resolve().parent
    image_path = os.path.join(base_dir, "assets", "Manhattan Icon.png")
    raw_img = Image.open(image_path)
    splash_img = customtkinter.CTkImage(light_image=raw_img, size=(550, 550))
    img_label = customtkinter.CTkLabel(splash, text="", image=splash_img)
    img_label.pack(expand=True)
    splash.after(3000, close_splash)
    splash.mainloop()
