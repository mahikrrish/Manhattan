"""
Application Configuration Utility

This script performs the initial one-time configuration required before
running the Offline AI application.

The configuration utility:

1. Verifies required application prerequisites.
2. Installs or downloads supported dependencies when required.
3. Creates the application database and tables.
4. Generates the database_configuration.py file containing the user's
   database connection settings.

Only the database configuration values below should be modified.
All remaining code should remain unchanged.

After successful configuration, run user_interface.py to start the
application.
"""
try:
    import os
    import customtkinter
    from CTkMessagebox import CTkMessagebox
    import mysql.connector
    from pathlib import Path
    import subprocess
    import socket
except (ModuleNotFoundError, ImportError) as e:
    from tkinter import messagebox
    messagebox.showerror(title="Error", message= f"It looks like required packages have not been installed. Kindly run pip install -r requirements.txt "
                                                 f"before running this file. Error: {type(e).__name__}: {e}", icon="error")
    exit()



DB_HOST = "<DB Host Nam>" #Edit with your local host name
DB_PORT = "<DB Port>" #Kindly unquote and replace with integer. Remove the quotes.
DB_USER = "<DB User>" #Edit with your user here
DB_PASSWORD = "<DB Password>" #Edit with your local passoword here


# No changes are required below this point.
# Only update the configuration values above.

class Configuration(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.config_message = ""
        self.withdraw()
        self.base_dir = Path(__file__).resolve().parent
        self.timeout = 5
        self.host = "8.8.8.8" # Connects to 8.8.8.8 (Google's DNS) via port 53, which is optimized for quick pings.
        self.port = 53
    def run(self):
        try:
            self.ollama_installation()
            self.spacy_installation()
            self.whisper_installation()
            self.database_configuration()
            return CTkMessagebox(title="Success", message=self.config_message, icon="check")
        finally:
            self.destroy()
    def socket_test(self):
        s = None
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            return True
        except (socket.error, socket.timeout) as e:
            CTkMessagebox(title="Error", message=f"Internet connectivity seems broken. Error - {type(e).__name__}: {e}", icon="cancel", sound=True).get()
            return False
        finally:
            if s:
                s.close()
    def ollama_installation(self):
        if self.socket_test():
            try:
                ollama_config = subprocess.run(['ollama', 'pull', 'llama3.2:3b'],check=True)
                if ollama_config.returncode == 0:
                    self.config_message += "Ollama model available.\n"
                    CTkMessagebox(title="Success", message="Ollama model available.", icon="check", sound=True).get()
            except FileNotFoundError as e:
                user_choice = CTkMessagebox(title="Error", message=f'Ollama is not installed. '
                                                     f'Would you like to install Ollama automatically? '
                                                     f'Administrator privileges will be required.'
                                                     f'{type(e).__name__}: {e}', icon="question",
                                            option_1="Yes", option_2="No", sound=True)
                if str(user_choice.get()).lower() == 'yes':
                    try:
                        CTkMessagebox(title='Note', message= 'Windows Defender may block this installation.\n '
                                                             'If blocked, please install Ollama manually from:\n'
                                                             'https://ollama.com/download/windows', icon="warning", sound=True).get()
                        subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", "irm https://ollama.com/install.ps1 | iex"], check=True)
                        ollama_config = subprocess.run(['ollama', 'pull', 'llama3.2:3b'], check=True)
                        if ollama_config.returncode == 0:
                            self.config_message += "Ollama model available.\n"
                            CTkMessagebox(title="Success", message="Ollama model available.", icon="check", sound=True).get()
                    except Exception as e:
                        CTkMessagebox(title="Error", message=f"{type(e).__name__}: {e}", icon="cancel", sound=True).get()
                else:
                    self.config_message += ("Ollama is not installed. Ollama is a pre-requisite installation. "
                                            "Kindly install Ollama application from "
                                            "https://ollama.com/download/windows before running the "
                                            "user_interface.py file\n\n")
                    CTkMessagebox(title="Report", message= "Ollama is not installed. "
                                                           "Ollama is a pre-requisite installation.\n\n",
                                  icon="warning", sound=True).get()
                    CTkMessagebox(title="Report",message="Kindly install Ollama application from "
                                                         "https://ollama.com/download/windows before running the "
                                                         "user_interface.py file\n\n", icon="warning", sound=True).get()
    def spacy_installation(self):
        try:
            import spacy
            if self.socket_test():
                try:
                    if not spacy.util.is_package('en_core_web_sm'):
                        user_choice = CTkMessagebox(title="Error", message='spaCy is not installed. Would you like to proceed with installation?\n\n', icon="question",
                                                    option_1="Yes", option_2="No", sound=True)
                        if str(user_choice.get()).lower() == 'yes':
                            spacy_config = subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'],
                                                          check=True)
                            if spacy_config.returncode == 0:
                                self.config_message += "spaCy model verified.\n\n"
                                CTkMessagebox(title="Success", message="spaCy model verified.\n\n", icon="check",
                                              sound=True).get()
                            else:
                                self.config_message += "spaCy model not verified.\n\n"
                                CTkMessagebox(title="Error", message="spaCy model not verified.\n\n", icon="cancel",
                                              sound=True).get()
                        else:
                            self.config_message += "spaCy model not installed.\n\n Kindly run python -m spacy download en_core_web_sm in command prompt."
                            CTkMessagebox(title="Error", message="spaCy model not installed.\n\n Kindly run python -m spacy download en_core_web_sm in command prompt.", icon="cancel",
                                          sound=True).get()
                    else:
                        self.config_message += "spaCy model verified.\n\n"
                        CTkMessagebox(title="Success", message= "spaCy model verified.\n\n", icon="check", sound=True).get()
                except Exception as e:
                    CTkMessagebox(title="Error", message= f"{type(e).__name__}:  {e}", icon="cancel", sound=True).get()
        except (ModuleNotFoundError, ImportError) as e:
            CTkMessagebox(title="spaCy Import Error", message= f"spaCy could not be imported.\n\n"
                                 f"This usually indicates that the Python environment or one of "
                                 f"spaCy's dependencies is not installed correctly.\n\n"
                                 f"Error:{type(e).__name__}: {e}", icon="cancel", sound=True).get()
        except Exception as e:
            CTkMessagebox(title="Error", message= f"{type(e).__name__}:  {e}", icon="cancel", sound=True).get()
    def whisper_installation(self):
        try:
            import whisper
            if self.socket_test():
                try:
                    model = whisper.load_model("base")
                    if model:
                        self.config_message += "Whisper model verified.\n\n"
                        CTkMessagebox(title="Success", message= "Whisper model verified.\n\n", icon="check", sound=True).get()
                    else:
                        self.config_message += "Whisper model not verified.\n\n"
                        CTkMessagebox(title="Error", message= "Whisper model not verified.\n\n", icon="cancel", sound=True).get()
                except Exception as e:
                    CTkMessagebox(title="Error", message= f"{type(e).__name__}: {e}", icon="cancel", sound=True).get()
                finally:
                    CTkMessagebox(title='Success', message= f'Application prerequisites have been verified.\n\n'
                                        f'{self.config_message}\n\n'
                                        'Database configuration will now begin\n\n', icon="check", sound=True).get()
        except Exception as e:
            CTkMessagebox(title="Error", message= f"{type(e).__name__}:  {e}", icon="cancel", sound=True).get()
    def database_configuration(self):
        try:
            config_file = os.path.join(self.base_dir, "database_configuration.py")
            if os.path.exists(config_file):
                CTkMessagebox(title="Info", message= "Database and Tables already Configured. "
                                                     "The pre-requisites has already been configured.\n\n"
                                                     "Run user_interface.py instead.\n\n", sound=True).get()
                exit()
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            try:
                mydb = mysql.connector.connect(host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD)
                mycursor = mydb.cursor()
                with open(os.path.join(self.base_dir, 'database_schema.sql'), 'r') as file:
                    queries = file.readlines()
                    for query in queries:
                        if query.strip() != "":
                            mycursor.execute(query)
                            mydb.commit()
                with open(os.path.join(self.base_dir, 'database_configuration.py'), 'w') as file:
                    file.write(f'DB_HOST = "{DB_HOST}"\n')
                    file.write(f'DB_PORT = {DB_PORT}\n')
                    file.write(f'DB_USER = "{DB_USER}"\n')
                    file.write(f'DB_PASSWORD = "{DB_PASSWORD}"\n')
                    file.write('DB_NAME = "offlineai"\n')
                CTkMessagebox(title="Success", message= "Configuration completed successfully. "
                                               "The database, tables and database_configuration.py have been created. "
                                               "You can now run user_interface.py. "
                                               "Database name is offlineai.\n\n", icon="check", sound=True).get()
            except Exception as e:
                CTkMessagebox(title="Configuration Error", message=f"{type(e).__name__}: {e}", icon="cancel", sound=True).get()
            finally:
                if 'mycursor' in locals():
                    mycursor.close()
                if 'mydb' in locals() and mydb.is_connected():
                    mydb.close()

if __name__ == "__main__":
    Configuration().run()