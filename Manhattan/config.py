"""
Application configuration.

Update the values below to match your local
MySQL installation.
"""

import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="mahi" #Please edit with your local password here
    )

    mycursor = mydb.cursor()
    mycursor.execute("USE offlineai;")

except mysql.connector.Error as e:
    mycursor.execute("CREATE DATABASE IF NOT EXISTS offlineai;")
    mycursor.execute("USE offlineai;")
    mycursor.execute('''CREATE TABLE IF NOT EXISTS conversation_history (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        input_mode VARCHAR(20),
        created_at DATETIME,
        raw_text LONGTEXT,
        processed_text JSON,
        langchain_input LONGTEXT,
        conversationmemory_input LONGTEXT,
        ai_response LONGTEXT,
        run_start_time DOUBLE,
        run_end_time DOUBLE,
        run_duration DOUBLE,
        status VARCHAR(50),
        error_message TEXT
    ) AUTO_INCREMENT = 1001;''')
    mycursor.execute('''CREATE TABLE IF NOT EXISTS performance_monitor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        conversation_id BIGINT,
        created_at DATETIME NOT NULL,
        component VARCHAR(200) NOT NULL,
        start_time DOUBLE NOT NULL,
        end_time DOUBLE NOT NULL,
        duration DOUBLE NOT NULL,
        status VARCHAR(100) NOT NULL,
        error_message TEXT,

        CONSTRAINT fk_performance_monitor_conversation
            FOREIGN KEY (conversation_id)
            REFERENCES conversation_history(id)
    );''')
    mydb.commit()


finally:
    # 4. Clean up and close connections
    if 'mycursor' in locals():
        mycursor.close()
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_NAME = "offlineai"
    DB_PASSWORD = "mahi"
