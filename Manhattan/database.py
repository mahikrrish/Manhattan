import time
import mysql
import mysql.connector
import pandas as pd
import random
import os
import threading

from mysql.connector import DatabaseError


class log(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db_connection = False
        self.attempt = 1
    def db_initiate(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mahi",
                database="offlineai"
            )
            self.mycursor = self.db.cursor()
            self.db_connection = True
        except Exception as e:
            self.db_connection = False
            raise Exception(f'Database Connection Error : {e}')

    def retrieve_conversation(self):
        try:
            if self.attempt<=2 and self.db_connection:
                df = pd.read_sql('SELECT * FROM log_data ORDER BY Date DESC, Time DESC LIMIT 5', self.db)
                if df:
                    self.attempt = 1
                    return df
            raise DatabaseError
        except (DatabaseError) as e:
            self.db_initiate()
            self.attempt += 1
            return self.retrieve_conversation()
    def inject_conversation(self, data):
        try:
            if self.attempt<=2 and self.db_connection:
                sql = (
                    f'INSERT INTO log_data (Date, Time, Method, Model_Name, Input_Type, Role, User_Input, ResponseID, '
                    f'Response, Status_Code, Status_Message, Status_Description)'
                    f' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
                values = (time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.action, self.model_name,
                          self.input_type, self.role, self.user_input, random.randint(1000, 9999), self.response,
                          self.status_code,
                          self.status_message, self.status_description)
                self.mycursor.execute(sql, values)
                self.db.commit()
                return True
            raise DatabaseError
        except (DatabaseError) as e:
            self.db_initiate()
            self.attempt += 1
            return self.inject_conversation(data)
                
    def performance_monitor(self, data):
        self.data = data
        if not self.db_connection:
            self.db_initiate()
        if not self.db_connection:
            raise Exception('Database connection could not be established for performance monitoring.')
        sql_query = (
            f'INSERT INTO performance_monitor (created_at, component, start_time, end_time, duration, status, error_message, conversation_id)'
            f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        )
        values = (
            self.data['created_at'], self.data['component'], self.data['start_time'], self.data['end_time'], self.data['duration'],
            self.data['status'], self.data['error_message'], self.data['conversation_id']
        )
        self.mycursor.execute(sql_query, values)
        self.db.commit()
