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

import mysql.connector
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import subprocess
import socket

DB_HOST = "<DB Host name>" #Edit with your local host name
DB_PORT = "<DB port>" #Kindly unquote and replace with integer. Remove the quotes.
DB_USER = "<DB username>" #Edit with your user here
DB_PASSWORD = "<DB password>" #Edit with your local passoword here


# No changes are required below this point.
# Only update the configuration values above.

base_dir = Path(__file__).resolve().parent
host="8.8.8.8" # Connects to 8.8.8.8 (Google's DNS) via port 53, which is optimized for quick pings.
port=53
timeout=5
config_message = ''

root = tk.Tk()
root.withdraw()


try:


    # Verify that Ollama is installed and ensure the required Llama 3.2:3b
    # model is available.
    #
    # If Ollama is not installed, the user is given the option to install it
    # automatically using the official PowerShell installer. Administrator
    # privileges are required.
    #
    # If automatic installation is declined, the user is instructed to install
    # Ollama manually before running the application.


    s = None
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        try:
            ollama_config = subprocess.run(
                [
                    'ollama',
                    'pull',
                    'llama3.2:3b'
                ],
                capture_output=True,
                check=True)
            if ollama_config.returncode == 0:
                config_message += "Ollama model available.\n"
        except FileNotFoundError as e:
            user_choice = messagebox.askquestion("Error",
                                                 f'Ollama is not installed. '
                                                 f'Would you like to install Ollama automatically? '
                                                 f'Administrator privileges will be required.'
                                                 f'{type(e).__name__}: {e}')
            if user_choice == 'yes':
                try:
                    subprocess.run(
                        [
                            "powershell",
                            "-ExecutionPolicy", "Bypass",
                            "-Command",
                            "irm https://ollama.com/install.ps1 | iex"
                        ],
                        check=True
                    )
                    ollama_config = subprocess.run(['ollama', 'pull', 'llama3.2:3b'], capture_output=True,
                                                   check=True)
                    if ollama_config.returncode == 0:
                        config_message += "Ollama model available.\n"
                except Exception as e:
                    messagebox.showerror("Error",
                                         f"{type(e).__name__}: {e}")
            else:
                messagebox.showerror("Error",
                                     "Ollama is not installed. "
                                     "Ollama is a pre-requisite installation."
                                     )
                messagebox.showinfo("Note",
                                    r"Kindly install Ollama application from "
                                    r"https://ollama.com/download/windows before running the "
                                    r"user_interface.py file"
                                    )
    except (socket.error, socket.timeout) as e:
        messagebox.showerror("Error", f"{type(e).__name__}: {e}")
    finally:
        if s:
            s.close()


    # Verify that the required spaCy language model is available.
    #
    # If the en_core_web_sm model is not installed, it is downloaded
    # automatically. Existing installations are reused.


    s = None
    try:
        import spacy
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        try:
            if not spacy.util.is_package('en_core_web_sm'):
                spacy_config = subprocess.run(
                    ['python', '-m', 'spacy', 'download', 'en_core_web_sm'],
                    capture_output=True,
                    check=True)
                if spacy_config.returncode == 0:
                    config_message += "spaCy model verified.\n"
                else:
                    config_message += "spaCy model not verified.\n"
            else:
                config_message += "spaCy model verified.\n"
        except Exception as e:
            messagebox.showerror("Error",
                                 f"{type(e).__name__}: {e}")
    except (socket.error, socket.timeout) as e:
        messagebox.showerror("Error", f"{type(e).__name__}: {e}")
        root.destroy()
        exit()
    finally:
        if s:
            s.close()


    # Verify that the FFmpeg executable is available.
    #
    # FFmpeg is an external dependency and must be installed separately.
    # This script only verifies its availability and does not install it.


    try:
        ffmpeg_config = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        if ffmpeg_config.returncode == 0:
            config_message += "FFmpeg detected.\n"
    except FileNotFoundError as e:
        messagebox.showerror("Error",
                             '''Kindly download FFmpeg from https://ffmpeg.org/download.html''')


    # Verify that the required Whisper model is available.
    #
    # If the model has not previously been downloaded, Whisper automatically
    # downloads it during the first execution. Existing cached models are
    # loaded without downloading them again.


    s = None
    try:
        import whisper
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        try:
            model = whisper.load_model("base")
            if model:
                config_message += "Whisper model verified.\n"
            else:
                config_message += "Whisper model not verified.\n"
        except Exception as e:
            messagebox.showerror("Error",
                                 f"{type(e).__name__}: {e}")
        finally:
            messagebox.showinfo('Success',
                                f'Application prerequisites have been verified.\n\n'
                                f'{config_message}\n\n'
                                'Database configuration will now begin\n\n')
    except (socket.error, socket.timeout) as e:
        messagebox.showerror("Error", f"{type(e).__name__}: {e}")
        root.destroy()
        exit()
    finally:
        if s:
            s.close()


    # Create the application database configuration.
    #
    # If database_configuration.py already exists, the application has already
    # been configured and no further database setup is required.
    #
    # Otherwise, the script:
    #
    # - Connects to the MySQL server.
    # - Executes the SQL schema.
    # - Creates the application database and tables.
    # - Generates database_configuration.py.


    try:
        config_file = os.path.join(base_dir, "database_configuration.py")
        if os.path.exists(config_file):
            messagebox.showinfo(
                "Already Configured",
                "The application has already been configured.\n\n"
                "Run user_interface.py instead."
            )
            exit()
        else:
            raise FileNotFoundError
    except FileNotFoundError:

        try:
            mydb = mysql.connector.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASSWORD
            )
            mycursor = mydb.cursor()
            with open(os.path.join(base_dir, 'database_schema.sql'), 'r') as file:
                queries = file.readlines()
                for query in queries:
                    if query.strip() != "":
                        mycursor.execute(query)
                        mydb.commit()

            # Generate the database_configuration.py module.
            # This file stores the user's database connection settings and is imported
            # by the application during normal execution, eliminating the need for the
            # user to repeatedly enter database configuration values.

            with open(os.path.join(base_dir, 'database_configuration.py'), 'w') as file:
                file.write(f'DB_HOST = "{DB_HOST}"\n')
                file.write(f'DB_PORT = {DB_PORT}\n')
                file.write(f'DB_USER = "{DB_USER}"\n')
                file.write(f'DB_PASSWORD = "{DB_PASSWORD}"\n')
                file.write('DB_NAME = "offlineai"\n')
            messagebox.showinfo("Success", "Configuration completed successfully. "
                                           "The database, tables and database_configuration.py have been created."
                                           "You can now run user_interface.py.")

        except Exception as e:
            messagebox.showerror(
                "Configuration Error",
                f"{type(e).__name__}: {e}"
            )

        # Release application resources.
        # Close all open database connections, cursors and sockets before exiting
        # the configuration utility.

        finally:
            if 'mycursor' in locals():
                mycursor.close()
            if 'mydb' in locals() and mydb.is_connected():
                mydb.close()
finally:
    root.destroy()