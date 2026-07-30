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
    messagebox.showerror(title="Error", message= f"It looks like required packages have "
                                                 f"not been installed. Kindly run pip "
                                                 f"install -r requirements.txt "
                                                 f"before running this file. Error: "
                                                 f"{type(e).__name__}: {e}", icon="error")
    exit()



DB_HOST = "<DB Host Nam>" #Edit with your local host name
DB_PORT = "<DB Port>" #Kindly unquote and replace with integer. Remove the quotes.
DB_USER = "<DB User>" #Edit with your user here
DB_PASSWORD = "<DB Password>" #Edit with your local passoword here


# No changes are required below this point.
# Only update the configuration values above.

class Configuration(customtkinter.CTk):
    """
    Application configuration utility for the Manhattan Offline AI Assistant.

    This class performs the one-time setup required before the application can
    be used. It verifies external application prerequisites, assists the user
    with installing missing dependencies where possible, creates the project
    database and tables, and generates the database_configuration.py module
    containing the user's database connection settings.

    The configuration workflow is intended to be executed only once during
    initial installation. After successful completion, subsequent executions
    of the application should begin from user_interface.py.

    Workflow:

        1. Verify internet connectivity.
        2. Verify or install Ollama.
        3. Verify the required spaCy language model.
        4. Verify the Whisper speech recognition model.
        5. Create the application database and tables.
        6. Generate database_configuration.py.
        7. Display a summary of the completed configuration.

    Attributes:

        config_message (str):
            Stores a cumulative summary of successful and unsuccessful
            configuration tasks.

        base_dir (Path):
            Directory containing the configuration script and supporting files.

        timeout (int):
            Socket timeout used during internet connectivity tests.

        host (str):
            Remote host used to verify internet connectivity.

        port (int):
            TCP port used during internet connectivity verification.
    """
    def __init__(self):
        """
        Initialize the configuration utility.

        The constructor prepares the hidden CustomTkinter root window used
        for message dialogs, initializes configuration status tracking,
        stores the application directory, and configures the parameters
        required for internet connectivity testing.

        The graphical window itself is never displayed since this utility
        communicates exclusively through message boxes.
        """
        super().__init__()
        self.config_message = ""
        self.withdraw()
        self.base_dir = Path(__file__).resolve().parent
        self.timeout = 5
        self.host = "8.8.8.8" # Connects to 8.8.8.8 (Google's DNS) via port 53
        self.port = 53
    def run(self):
        """
        Execute the complete application configuration workflow.

        This method serves as the entry point for the configuration utility.
        Each configuration stage is executed sequentially so that required
        application prerequisites are verified before database creation
        begins.

        Configuration stages include:

            1. Ollama verification and installation.
            2. spaCy language model verification.
            3. Whisper model verification.
            4. Database creation.
            5. Generation of database_configuration.py.

        After all stages complete, a summary of the configuration results
        is presented to the user.

        Returns:

            CTkMessagebox:
                Displays a summary of the completed configuration process.

        Notes:

            The hidden CustomTkinter root window is destroyed before
            exiting regardless of success or failure.
        """
        try:
            self.ollama_installation()
            self.spacy_installation()
            self.whisper_installation()
            self.database_configuration()
            return CTkMessagebox(title="Success", message=self.config_message, icon="check")
        finally:
            self.destroy()
    def socket_test(self):
        """
        Verify internet connectivity.

        This method attempts to establish a TCP connection with Google's
        public DNS server. Successful connection indicates that internet
        access is available and prerequisite downloads may proceed.

        Returns:

            bool:

                True
                    Internet connectivity is available.

                False
                    Internet connectivity could not be established.

        Notes:

            The socket is always closed before the method returns.
        """
        s = None
        try:
            socket.setdefaulttimeout(self.timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            return True
        except (socket.error, socket.timeout) as e:
            CTkMessagebox(title="Error", message=f"Internet connectivity seems broken. "
                                                 f"Error - {type(e).__name__}: {e}",
                          icon="cancel", sound=True).get()
            return False
        finally:
            if s:
                s.close()
    def ollama_installation(self):
        """
        Verify availability of the Ollama language model.

        The method first verifies internet connectivity before attempting
        to download the required Llama 3.2:3B model using Ollama.

        If Ollama is not installed, the user is given the option to install
        it automatically through the official PowerShell installation script.
        If automatic installation is declined, instructions are provided
        for manual installation.

        Configuration results are appended to the configuration summary.

        Returns:

            None
        """
        if self.socket_test():
            try:
                ollama_config = subprocess.run(['ollama', 'pull', 'llama3.2:3b'],check=True)
                if ollama_config.returncode == 0:
                    self.config_message += "Ollama model available.\n"
                    CTkMessagebox(title="Success",
                                  message="Ollama model available.\n",
                                  icon="check", sound=True).get()
            except FileNotFoundError as e:
                user_choice = CTkMessagebox(title="Error",
                                            message=f'Ollama is not installed. '
                                                    f'Would you like to install Ollama '
                                                    f'automatically? '
                                                    f'Administrator privileges will be required. '
                                                    f'{type(e).__name__}: {e}', icon="question",
                                            option_1="Yes", option_2="No", sound=True)
                if str(user_choice.get()).lower() == 'yes':
                    try:
                        CTkMessagebox(title='Note',
                                      message= 'Windows Defender may block this installation.\n '
                                               'If blocked, please install Ollama manually from:\n'
                                               'https://ollama.com/download/windows',
                                      icon="warning", sound=True).get()
                        subprocess.run(
                            [
                                "powershell",
                                "-ExecutionPolicy",
                                "Bypass",
                                "-Command",
                                "irm https://ollama.com/install.ps1 | iex"
                            ],
                            check=True
                        )
                        ollama_config = subprocess.run(
                            [
                                'ollama',
                                'pull',
                                'llama3.2:3b'
                            ],
                            check=True)
                        if ollama_config.returncode == 0:
                            self.config_message += "Ollama model available.\n"
                            CTkMessagebox(title="Success",
                                          message="Ollama model available.\n",
                                          icon="check", sound=True).get()
                    except Exception as e:
                        CTkMessagebox(title="Error",
                                      message=f"{type(e).__name__}: {e}",
                                      icon="cancel", sound=True).get()
                else:
                    self.config_message += ("Ollama is not installed. "
                                            "Ollama is a pre-requisite installation. "
                                            "Kindly install Ollama application from "
                                            "https://ollama.com/download/windows "
                                            "before running the "
                                            "user_interface.py file\n")
                    CTkMessagebox(title="Report",
                                  message= "Ollama is not installed. "
                                           "Ollama is a pre-requisite installation.\n",
                                  icon="warning", sound=True).get()
                    CTkMessagebox(title="Report",
                                  message="Kindly install Ollama application from "
                                          "https://ollama.com/download/windows before running the "
                                          "user_interface.py file\n",
                                  icon="warning", sound=True).get()
    def spacy_installation(self):
        """
        Verify the required spaCy language model.

        The spaCy package is expected to have already been installed through
        requirements.txt. This method verifies whether the required English
        language model is available.

        If the model is missing, the user may choose to download it
        automatically. If the user declines, manual installation instructions
        are provided.

        Configuration results are appended to the configuration summary.

        Returns:

            None
        """
        try:
            import spacy
            if self.socket_test():
                try:
                    if not spacy.util.is_package('en_core_web_sm'):
                        user_choice = CTkMessagebox(title="Error",
                                                    message='spaCy is not installed. '
                                                            'Would you like to proceed '
                                                            'with installation?\n',
                                                    icon="question",
                                                    option_1="Yes", option_2="No",
                                                    sound=True)
                        if str(user_choice.get()).lower() == 'yes':
                            spacy_config = subprocess.run(
                                [
                                    'python',
                                    '-m',
                                    'spacy',
                                    'download',
                                    'en_core_web_sm'
                                ],
                                check=True)
                            if spacy_config.returncode == 0:
                                self.config_message += "spaCy model verified.\n"
                                CTkMessagebox(title="Success",
                                              message="spaCy model verified.\n",
                                              icon="check",
                                              sound=True).get()
                            else:
                                self.config_message += "spaCy model not verified.\n"
                                CTkMessagebox(title="Error",
                                              message="spaCy model not verified.\n",
                                              icon="cancel",
                                              sound=True).get()
                        else:
                            self.config_message += ("spaCy model not installed.\n"
                                                    "Kindly run python -m spacy "
                                                    "download en_core_web_sm "
                                                    "in command prompt.")
                            CTkMessagebox(title="Error",
                                          message="spaCy model not installed.\n"
                                                  "Kindly run python -m spacy "
                                                  "download en_core_web_sm in "
                                                  "command prompt.",
                                          icon="cancel",
                                          sound=True).get()
                    else:
                        self.config_message += "spaCy model verified.\n"
                        CTkMessagebox(title="Success",
                                      message= "spaCy model verified.\n",
                                      icon="check", sound=True).get()
                except Exception as e:
                    CTkMessagebox(title="Error",
                                  message= f"{type(e).__name__}:  {e}",
                                  icon="cancel", sound=True).get()
        except (ModuleNotFoundError, ImportError) as e:
            CTkMessagebox(title="spaCy Import Error",
                          message= f"spaCy could not be imported.\n"
                                   f"This usually indicates that the Python "
                                   f"environment or one of "
                                   f"spaCy's dependencies is not "
                                   f"installed correctly.\n"
                                   f"Error:{type(e).__name__}: {e}",
                          icon="cancel", sound=True).get()
        except Exception as e:
            CTkMessagebox(title="Error",
                          message= f"{type(e).__name__}:  {e}",
                          icon="cancel", sound=True).get()
    def whisper_installation(self):
        """
        Verify the Whisper speech recognition model.

        The method loads the Whisper 'base' model. If the model has not been
        downloaded previously, the Whisper library automatically downloads it
        from the official source.

        Successful model loading confirms that Whisper is ready for use by
        the speech recognition component.

        After verification completes, a summary of all prerequisite checks
        performed so far is presented to the user before database
        configuration begins.

        Returns:

            None
        """
        try:
            import whisper

            if self.socket_test():
                try:
                    model = whisper.load_model("base")
                    if model:
                        self.config_message += "Whisper model verified.\n"
                        CTkMessagebox(title="Success",
                                      message= "Whisper model verified.\n",
                                      icon="check", sound=True).get()
                    else:
                        self.config_message += "Whisper model not verified.\n"
                        CTkMessagebox(title="Error",
                                      message= "Whisper model not verified.\n",
                                      icon="cancel", sound=True).get()
                except Exception as e:
                    CTkMessagebox(title="Error",
                                  message= f"{type(e).__name__}: {e}",
                                  icon="cancel", sound=True).get()
                finally:
                    CTkMessagebox(title='Success',
                                  message= f'Application prerequisites have been verified.\n'
                                           f'{self.config_message}\n'
                                           f'Database configuration will now begin\n',
                                  icon="check", sound=True).get()
        except Exception as e:
            CTkMessagebox(title="Error",
                          message= f"{type(e).__name__}:  {e}",
                          icon="cancel", sound=True).get()
    def database_configuration(self):
        """
        Create the application database and generate database_configuration.py.

        This method first checks whether database_configuration.py already
        exists. If the file is present, the application is assumed to have
        already been configured.

        Otherwise, the method:

            1. Connects to the MySQL server.
            2. Executes all SQL statements contained in database_schema.sql.
            3. Creates database_configuration.py containing the user's
               database connection settings.
            4. Informs the user that configuration has completed successfully.

        Database connections and cursors are always closed before the method
        returns.

        Returns:

            None
        """
        try:
            config_file = os.path.join(self.base_dir, "database_configuration.py")
            if os.path.exists(config_file):
                CTkMessagebox(title="Info",
                              message= "Database and Tables already Configured. "
                                       "The pre-requisites has already been configured.\n"
                                       "Run user_interface.py instead.\n",
                              sound=True).get()
                exit()
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            try:
                mydb = mysql.connector.connect(host=DB_HOST,
                                               port=int(DB_PORT),
                                               user=DB_USER,
                                               password=DB_PASSWORD)
                mycursor = mydb.cursor()
                with open(os.path.join(self.base_dir, 'database_schema.sql'), 'r',
                          encoding='utf-8') as file:
                    queries = file.readlines()
                    for query in queries:
                        if query.strip() != "":
                            mycursor.execute(query)
                            mydb.commit()
                with open(os.path.join(self.base_dir, 'database_configuration.py'), 'w',
                          encoding='utf-8') as file:
                    file.write(f'DB_HOST = "{DB_HOST}"\n')
                    file.write(f'DB_PORT = {DB_PORT}\n')
                    file.write(f'DB_USER = "{DB_USER}"\n')
                    file.write(f'DB_PASSWORD = "{DB_PASSWORD}"\n')
                    file.write('DB_NAME = "offlineai"\n')
                CTkMessagebox(title="Success",
                              message= "Configuration completed successfully. "
                                       "The database, tables and "
                                       "database_configuration.py have been created. "
                                       "You can now run user_interface.py. "
                                       "Database name is offlineai.\n",
                              icon="check", sound=True).get()
            except Exception as e:
                CTkMessagebox(title="Configuration Error",
                              message=f"{type(e).__name__}: {e}",
                              icon="cancel", sound=True).get()
            finally:
                if 'mycursor' in locals():
                    mycursor.close()
                if 'mydb' in locals() and mydb.is_connected():
                    mydb.close()

if __name__ == "__main__":
    Configuration().run()
