import pandas as pd
from ollama import chat
import time, datetime, os
from pandas import *
from openpyxl import *

http_status_codes = {
    # 1xx – Informational
    100: {"Message": "Continue", "Description": "The server has received the request headers and the client should proceed to send the request body"},
    101: {"Message": "Switching Protocols", "Description": "The requester has asked the server to switch protocols"},
    102: {"Message": "Processing", "Description": "The server has received and is processing the request, but no response is available yet"},
    103: {"Message": "Early Hints", "Description": "Allows the user agent to start preloading resources while the server is preparing a response"},

    # 2xx – Success
    200: {"Message": "OK", "Description": "The request succeeded"},
    201: {"Message": "Created", "Description": "The request succeeded and a new resource was created"},
    202: {"Message": "Accepted", "Description": "The request has been accepted for processing, but the processing is not complete"},
    203: {"Message": "Non-Authoritative Information", "Description": "The request was successful but the returned metadata may come from a local or third-party copy"},
    204: {"Message": "No Content", "Description": "The server successfully processed the request, but is not returning any content"},
    205: {"Message": "Reset Content", "Description": "Tells the user agent to reset the document which sent the request"},
    206: {"Message": "Partial Content", "Description": "The server is delivering only part of the resource due to a range header sent by the client"},
    207: {"Message": "Multi-Status", "Description": "Provides status for multiple independent operations (WebDAV)"},
    208: {"Message": "Already Reported", "Description": "Members of a DAV binding have already been enumerated in a previous reply (WebDAV)"},
    226: {"Message": "IM Used", "Description": "The server has fulfilled a GET request and the response represents the result of one or more instance-manipulations applied to the current instance"},

    # 3xx – Redirection
    300: {"Message": "Multiple Choices", "Description": "Indicates multiple options for the resource from which the client may choose"},
    301: {"Message": "Moved Permanently", "Description": "The resource has been moved permanently to a new URL"},
    302: {"Message": "Found", "Description": "The resource resides temporarily under a different URL"},
    303: {"Message": "See Other", "Description": "The response can be found under a different URI and should be retrieved using a GET method"},
    304: {"Message": "Not Modified", "Description": "Indicates that the resource has not been modified since the last request"},
    305: {"Message": "Use Proxy", "Description": "The requested resource is only available through a proxy (deprecated)"},
    306: {"Message": "Unused", "Description": "This code used to mean 'Switch Proxy' but is no longer used"},
    307: {"Message": "Temporary Redirect", "Description": "The request should be repeated with another URI using the same method"},
    308: {"Message": "Permanent Redirect", "Description": "The request and future requests should be repeated using another URI"},

    # 4xx – Client Error
    400: {"Message": "Bad Request", "Description": "The server could not understand the request due to invalid syntax"},
    401: {"Message": "Unauthorized", "Description": "Authentication is required to access the resource"},
    402: {"Message": "Payment Required", "Description": "Reserved for future use"},
    403: {"Message": "Forbidden", "Description": "The client does not have access rights to the content"},
    404: {"Message": "Not Found", "Description": "The server can not find the requested resource"},
    405: {"Message": "Method Not Allowed", "Description": "The request method is known but has been disabled and cannot be used"},
    406: {"Message": "Not Acceptable", "Description": "The resource is not capable of generating acceptable content according to the Accept headers"},
    407: {"Message": "Proxy Authentication Required", "Description": "The client must first authenticate itself with the proxy"},
    408: {"Message": "Request Timeout", "Description": "The server timed out waiting for the request"},
    409: {"Message": "Conflict", "Description": "The request conflicts with the current state of the server"},
    410: {"Message": "Gone", "Description": "The resource requested is no longer available and will not be available again"},
    411: {"Message": "Length Required", "Description": "The request did not specify the length of its content"},
    412: {"Message": "Precondition Failed", "Description": "The server does not meet one of the preconditions in the request headers"},
    413: {"Message": "Payload Too Large", "Description": "The request entity is larger than limits defined by the server"},
    414: {"Message": "URI Too Long", "Description": "The URI requested by the client is longer than the server is willing to interpret"},
    415: {"Message": "Unsupported Media Type", "Description": "The media format of the requested data is not supported by the server"},
    416: {"Message": "Range Not Satisfiable", "Description": "The range specified by the Range header field in the request cannot be fulfilled"},
    417: {"Message": "Expectation Failed", "Description": "The expectation given in the request's Expect header could not be met"},
    418: {"Message": "I'm a teapot", "Description": "Defined as an April Fools' joke; the server refuses to brew coffee in a teapot"},
    421: {"Message": "Misdirected Request", "Description": "The request was directed at a server that is not able to produce a response"},
    422: {"Message": "Unprocessable Content", "Description": "The request was well-formed but was unable to be followed due to semantic errors (WebDAV)"},
    423: {"Message": "Locked", "Description": "The resource being accessed is locked (WebDAV)"},
    424: {"Message": "Failed Dependency", "Description": "The request failed due to failure of a previous request (WebDAV)"},
    425: {"Message": "Too Early", "Description": "Indicates that the server is unwilling to risk processing a request that might be replayed"},
    426: {"Message": "Upgrade Required", "Description": "The client should switch to a different protocol"},
    428: {"Message": "Precondition Required", "Description": "The origin server requires the request to be conditional"},
    429: {"Message": "Too Many Requests", "Description": "The user has sent too many requests in a given amount of time"},
    431: {"Message": "Request Header Fields Too Large", "Description": "The server is unwilling to process the request because its header fields are too large"},
    451: {"Message": "Unavailable For Legal Reasons", "Description": "The user-agent requested a resource that cannot legally be provided"},

    # 5xx – Server Error
    500: {"Message": "Internal Server Error", "Description": "The server encountered an unexpected condition that prevented it from fulfilling the request"},
    501: {"Message": "Not Implemented", "Description": "The server does not support the functionality required to fulfill the request"},
    502: {"Message": "Bad Gateway", "Description": "The server received an invalid response from an inbound server it accessed while attempting to fulfill the request"},
    503: {"Message": "Service Unavailable", "Description": "The server is not ready to handle the request"},
    504: {"Message": "Gateway Timeout", "Description": "The server did not receive a timely response from an upstream server"},
    505: {"Message": "HTTP Version Not Supported", "Description": "The HTTP version used in the request is not supported by the server"},
    506: {"Message": "Variant Also Negotiates", "Description": "Transparent content negotiation for the request results in a circular reference"},
    507: {"Message": "Insufficient Storage", "Description": "The server is unable to store the representation needed to complete the request (WebDAV)"},
    508: {"Message": "Loop Detected", "Description": "The server detected an infinite loop while processing a request (WebDAV)"},
    510: {"Message": "Not Extended", "Description": "Further extensions to the request are required for the server to fulfill it"},
    511: {"Message": "Network Authentication Required", "Description": "The client must authenticate to gain network access"}
}


def log(file, user_input, response, status_code = 'N/A', input_type = 'N/A'):
    log_data = {'Date': time.strftime('%m-%d-%Y'),
                'Time': time.strftime('%H:%M:%S'),
                'Input_Type': input_type,
                'User_Input': user_input,
                'Response': response,
                'Status_Code': status_code,
                'Status_Message': 'N/A' if status_code == 'N/A' or status_code not in http_status_codes else http_status_codes[status_code]['Message'],
                'Status_Description': 'N/A' if status_code == 'N/A' or status_code not in http_status_codes else http_status_codes[status_code]['Description'],
    }
    df = pd.DataFrame([log_data])
    # with pd.ExcelWriter(file, engine='openpyxl', mode='a' if os.path.exists(file) else 'w') as writer:
    #     df.to_excel(file, index=False, header = not os.path.exists(file))
    df_file = pd.read_excel(file)
    last_index_value = df_file.shape[0]
    del df_file
    # result = pd.concat([df_file, df_file], axis=0, ignore_index=False)
    # df_file.to_excel(file, index=False, startrow=last_index_value)
    # pd.ExcelWriter(file)
    with pd.ExcelWriter(file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=last_index_value)




def AI_response(user_input, status_code = 'N/A'):
    """"
    Connects to the local Ollama instance and summarizes the text.
    """
    model_name = 'llama3.2:1b'
    messages = [
        {
            'role': 'user',
            'content': f'Below is a request from a user. Please identify the task and execute it accurately using the provided context. {user_input}'
        },
        {
            'role': 'system',
            'content': "You are a high-precision text processing engine. "
                       "Constraint: Use professional, objective language. "
                       "Constraint: Format all lists as bullet points. "
                       "Constraint: Do not include introductory or concluding remarks."
        }
    ]
    try:
        response = chat(model=model_name, messages=messages,
                        options={'temperature': 0.1, 'num_ctx': 8192, 'keep_alive': '10m'},
                        stream=False
                        )
        # print('AI response: ', end='', flush=True)
        # response['message']['content'] = response['message']['content'].replace('<|start_header_id|>assistant<|end_header_id|>', ''.strip())
        # for message in response:
        #     print(message['message']['content'], end='', flush=True)
        return response['message']['content']
    except Exception as e:
        return f'Error connecting to Ollama : {str(e)}'