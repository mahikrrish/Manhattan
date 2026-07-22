"""
Database management component for the Manhattan AI Assistant.

This module provides a centralized database access layer for the
Manhattan project. It manages MySQL connections, conversation
storage, conversation retrieval, and component-level performance
monitoring.

Rather than allowing every project component to communicate directly
with MySQL, Manhattan uses DatabaseManager as an abstraction layer.
This improves modularity, simplifies database maintenance, and keeps
SQL operations isolated from the application's business logic.

Current Architecture:

        Manhattan Components
                │
                ▼
         DatabaseManager
                │
      ┌─────────┴─────────┐
      ▼                   ▼
Conversation History   Performance Monitor
      ▼                   ▼
          MySQL Database

Current responsibilities of this module:

- Establish and maintain MySQL database connectivity.
- Create new conversation records before processing begins.
- Retrieve previous conversations for context generation.
- Update completed conversation records after processing.
- Record component-level performance metrics.
- Provide a single database interface shared across all Manhattan
  components.

Conversation Lifecycle:

Unlike traditional database designs where an entire conversation is
written only after processing completes, Manhattan uses a two-phase
conversation lifecycle.

1. create_conversation()
   - Creates a new conversation_history row before any processing
     begins.
   - Inserts only the input_mode.
   - Returns the generated conversation_id.

2. Component Execution
   - The generated conversation_id is propagated through Speech
     Recognition, Natural Language Processing, Conversation Memory,
     Manhattan, and Performance Monitoring.
   - Each component independently records its execution metrics while
     referencing the same conversation_id.

3. inject_conversation()
   - Executes after the complete pipeline finishes.
   - Updates the existing conversation_history row with:
       • creation timestamp
       • raw user input
       • structured NLP output
       • conversation memory supplied to the LLM
       • AI response
       • execution timings
       • execution status
       • error information

This parent-child design guarantees that every performance_monitor
record can be traced back to a single conversation_history row,
providing complete end-to-end execution visibility while allowing
component-level performance analysis.

Database tables currently managed:

- conversation_history
- performance_monitor

Author:
    Sai Krishna Mahidhar Devulapalli

Project:
    Manhattan - Offline AI Assistant
"""

import mysql
import mysql.connector
import pandas as pd
import threading
import json
import config

class DatabaseManager(threading.Thread):
    """
    Central database management component for the Manhattan AI Assistant.

    This class acts as the single communication layer between Manhattan
    and the MySQL database.

    It provides reusable methods for creating conversations, updating
    conversation history, retrieving previous conversations, and storing
    component-level execution metrics.

    DatabaseManager intentionally separates database operations from
    individual project components. As a result, Speech Recognition,
    Natural Language Processing, Conversation Memory, Manhattan, and the
    User Interface remain independent of SQL implementation details.

    Features:

    - Automatic database connection initialization
    - Conversation lifecycle management
    - Conversation history retrieval
    - Component performance logging
    - Shared reusable MySQL connection
    - Exception propagation for database failures

    Attributes:

        db_connection (bool):
            Indicates whether a valid database connection has been
            established.

        attempt (int):
            Reserved for future database reconnection or retry logic.

        db (mysql.connector.connection_cext.CMySQLConnection):
            Active MySQL database connection.

        mycursor (mysql.connector.cursor.MySQLCursor):
            Cursor object used to execute SQL queries.
    """
    def __init__(self):
        """
        Initialize the DatabaseManager component.

        This constructor initializes the parent Thread class and prepares
        internal variables used for database connection management.

        A database connection is not established during object creation.
        Instead, connections are created lazily when the first database
        operation is requested.

        This approach avoids unnecessary database connections when the
        component is instantiated but not immediately used.
        """
        threading.Thread.__init__(self)
        self.db_connection = False
        self.attempt = 1
    def db_initiate(self):
        """
        Establish a connection to the MySQL database.

        This method creates the project's MySQL connection and initializes
        the cursor object used by all subsequent SQL operations.

        The resulting connection is reused throughout the lifetime of the
        DatabaseManager instance, eliminating repeated connection overhead.

        Workflow:

            1. Connect to MySQL.
            2. Select the Manhattan database.
            3. Create SQL cursor.
            4. Mark connection as active.

        Raises:

            Exception:
                Raised when a database connection cannot be established.

        Side Effects:

            Initializes:

            - self.db
            - self.mycursor
            - self.db_connection
        """
        try:
            self.db = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME
            )
            self.mycursor = self.db.cursor()
            self.db_connection = True
        except Exception as e:
            self.db_connection = False
            raise Exception(f'Database Connection Error : {e}')
    def create_conversation(self, input_mode):
        """
        Create a new conversation record.

        This method creates the initial conversation_history row before any
        processing begins.

        Only the input mode is inserted during this stage. The remaining
        conversation details become available as the pipeline executes and
        are written later through inject_conversation().

        The generated conversation_id becomes the parent identifier shared
        across all project components.

        Workflow:

            1. Verify database connection.
            2. Insert initial conversation row.
            3. Commit transaction.
            4. Retrieve generated conversation_id.
            5. Return conversation_id.

        Args:

            input_mode (str):
                User-selected input mode.

                Examples:

                - Text
                - Voice

        Returns:

            int:
                Auto-generated conversation_id used throughout the current
                conversation lifecycle.

        Raises:

            Exception:
                Raised when the database connection cannot be established.
        """
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
        """
        Retrieve previous conversations.

        This method fetches the most recent conversation_history records from
        MySQL while preserving chronological order.

        Internally, the newest rows are selected first for efficiency before
        being reordered into ascending conversation order. This ensures the
        Conversation Memory component receives messages in the correct
        chronological sequence.

        Args:

            row_limit (int):
                Maximum number of conversation records to retrieve.

        Returns:

            pandas.DataFrame:
                DataFrame containing the retrieved conversation_history rows.

        Raises:

            Exception:
                Raised when the database connection cannot be established.
        """
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
        """
        Update a completed conversation record.

        This method completes the conversation_history row that was created
        at the beginning of the conversation.

        Once Manhattan finishes processing, all generated information is
        written into the corresponding conversation record using the
        conversation_id assigned during create_conversation().

        Stored information includes:

        - Conversation metadata
        - Raw user input
        - Structured NLP output
        - Conversation Memory input
        - AI response
        - Execution timing
        - Execution status
        - Error information

        Workflow:

            1. Verify database connection.
            2. Serialize structured objects.
            3. Update conversation_history row.
            4. Commit transaction.

        Args:

            conv_data (dict):
                Dictionary containing the complete conversation execution
                data.

        Raises:

            Exception:
                Raised when the database connection cannot be established.

        Notes:

            Structured Python objects such as NLP output and Conversation
            Memory messages are serialized into JSON before being stored in
            MySQL.
        """
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
        """
        Store component-level performance information.

        This method inserts a performance record into the
        performance_monitor table.

        Every Manhattan component independently records its execution
        details using this method. Each performance record is linked to its
        parent conversation through conversation_id, allowing complete
        end-to-end execution analysis.

        Metrics recorded include:

        - created_at
        - component
        - start_time
        - end_time
        - duration
        - status
        - error_message
        - conversation_id

        Args:

            perf_data (dict):
                Dictionary containing component execution metadata.

        Raises:

            Exception:
                Raised when the database connection cannot be established.

        Notes:

            Multiple performance_monitor records may reference the same
            conversation_id, allowing individual component timings to be
            correlated with a single conversation_history record.
        """
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
