import mysql
import mysql.connector
import pandas as pd
import threading
import json


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
    def create_conversation(self, input_mode):
        if not self.db_connection:
            self.db_initiate()
        if not self.db_connection:
            raise Exception('Database connection could not be established for creating conversation.')
        sql = (
            f'INSERT INTO conversation_history (input_mode) '
            f'VALUES (%s)'
        )
        values = (input_mode, )
        self.mycursor.execute(sql, values)
        self.db.commit()
        conversation_id = self.mycursor.lastrowid
        return conversation_id

    def retrieve_conversation(self, row_limit):
        if not self.db_connection:
            self.db_initiate()
        if not self.db_connection:
            raise Exception('Database connection could not be established for retrieving conversation.')
        df = pd.read_sql(f'SELECT * FROM ('
                             f'select * '
                             f'from conversation_history '
                             f'ORDER BY conversation_id DESC '
                             f'LIMIT {row_limit} '
                             f') AS subquery_table '
                             f'ORDER BY conversation_id ASC', self.db)
        return df

    def inject_conversation(self, conv_data):
        if not self.db_connection:
            self.db_initiate()
        if not self.db_connection:
            raise Exception('Database connection could not be established for conversation injection.')
        sql = (
            f'UPDATE conversation_history '
            f'SET created_at = %s, '
            f'raw_text = %s, '
            f'processed_text = %s, '
            f'conversationmemory_input = %s, '
            f'ai_response = %s, '
            f'run_start_time = %s, '
            f'run_end_time = %s, '
            f'run_duration = %s, '
            f'status = %s, '
            f'error_message = %s '
            f'WHERE conversation_id = %s'
        )
        values = (conv_data['created_at'], conv_data['raw_text'], json.dumps(conv_data['processed_text']),
                  json.dumps(conv_data['conversationmemory_input']), conv_data['ai_response'], conv_data['run_start_time'],
                  conv_data['run_end_time'], conv_data['run_end_time'] - conv_data['run_start_time'], conv_data['status'],
                  conv_data['error_message'], conv_data['conversation_id']
                  )
        self.mycursor.execute(sql, values)
        self.db.commit()

    def performance_monitor(self, perf_data):
        if not self.db_connection:
            self.db_initiate()
        if not self.db_connection:
            raise Exception('Database connection could not be established for performance monitoring.')
        sql_query = (
            f'INSERT INTO performance_monitor (created_at, component, start_time, end_time, duration, status, error_message, conversation_id) '
            f'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        )
        values = (
            perf_data['created_at'], perf_data['component'], perf_data['start_time'], perf_data['end_time'], perf_data['duration'],
            perf_data['status'], perf_data['error_message'], perf_data['conversation_id']
        )
        self.mycursor.execute(sql_query, values)
        self.db.commit()
