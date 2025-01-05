



import ssl
from sessions import Session, generate_session_id, get_session_id_from_request,cookie_response,get_session,create_session,sessions
from http_module import *
from Frames import *
from HPACK import *
from HPACK import encode_header,encode_integer,encode_string


HTTP2_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"




# def handle_http1(client_socket, client_address):
#     try:
#         print(f"Handling client {client_address} using http1")

#         client_socket.settimeout(10)  # Optional timeout
#         request_data = client_socket.recv(1024).decode('utf-8', errors='ignore')  
#     except client_socket.timeout:
#         print(f"Client {client_address} timed out")
#     except Exception as e:
#         print(f"Error handling client {client_address}: {e}")
  
#     print(f"Handling HTTP/1.1 request from {client_address} \n")

#     print(f"{request_data} \n")

  
#     # Process other HTTP/1.1 requests (e.g., GET and POST)
# def handle_http1(client_socket, client_address):
#     try:
#         print(f"Handling client {client_address} using HTTP/1")

#         client_socket.settimeout(10)
#         request_data = client_socket.recv(1024).decode('utf-8', errors='ignore')

#         http_request = HttpRequest(request_data)
#         session=None

#         session_id = get_session_id_from_request(request_data)

#         if session_id in sessions:
#             print(f"Valid session found for {client_address}: {session_id}")
#             session = sessions[session_id]
#             print(f"The username saved in session data is {session.username}")

#         else:
#             print(f"No valid session for {client_address}, creating a new one.")
#             session = create_session()
#             cookie_response(client_socket, session.session_id)  # Send session cookie to client


#         if http_request.method == "GET":
#             handle_GET(client_socket, http_request)
#         elif http_request.method == "POST":

#             handle_POST(client_socket, session, http_request)

#     except ssl.SSLError as e:
#         print(f"SSL error with client {client_address}: {e}")
#     except Exception as e:
#         print(f"Error handling client {client_address}: {e}")
#     finally:
#         client_socket.close()


def handle_GET(client_socket, GET_request):
    if GET_request.path == "/":
        with open("files/index.html", "r") as file:
            html_content = file.read()



        # encoded_headers=[]

        # print(len(html_content))

        hex_string = "885f09746578742f68746d6c5c03363534"

        # Convert the hex string to bytes
        encoded_bytes = bytes.fromhex(hex_string)

        # Print the result to verify the conversion
        print("Encoded Bytes:", encoded_bytes)


        
           
        with open("files/index.html", "r") as file:
                html_content = file.read()

            # Convert HTML content to bytes
        data_payload = html_content.encode('utf-8')  # Encode the string to bytes using UTF-8


            # Step 4: Respond with HEADERS and DATA frames
            # Create headers for the response (200 OK)
        response_headers = b'\x88\x85'  # This should be updated with real headers logic

            # Headers frame (200 OK response)
        headers_frame = (
                b'\x00\x00\x02'  # Length: 2 bytes (size of response_headers)
                + b'\x01'        # Type: HEADERS
                + b'\x04'        # Flags: END_HEADERS
                + b'\x00\x00\x00\x01'  # Stream ID: 1
                + response_headers
            )

            # Data frame
        data_frame = (
                len(data_payload).to_bytes(3, byteorder='big')  # Length of payload
                + b'\x00'  # Type: DATA
                + b'\x01'  # Flags: END_STREAM
                + b'\x00\x00\x00\x01'  # Stream ID: 1
                + data_payload

            )

            # Send HEADERS and DATA frames together
        
        client_socket.sendall(headers_frame + data_frame)
        
       
        #x88\xbe\xbf
        # headers = [
        #     (":status", "200"),
        #     ("content-type", "text/html"),
        #     ("content-length",f"{len(html_content)}")
        # ]

        # encoded_headers = []
        # for name, value in headers:
        #     encoded_headers.extend(encode_header(name, value,dynamic_table))

     
        # encoded_headers_bytes = bytes(encoded_headers)

        # print(encoded_headers_bytes)

        # headers_frame = (
        #         get_response_size(encoded_bytes)  # Length: 2 bytes (size of response_headers)
        #         + b'\x01'        # Type: HEADERS
        #         + b'\x04'        # Flags: END_HEADERS
        #         + b'\x00\x00\x00\x01'  # Stream ID: 1
        #         + encoded_bytes)
 
        # data_payload = html_content.encode('utf-8')

        
        #     # Data frame
        # data_frame = (
        #     len(data_payload).to_bytes(3, byteorder='big')  # Length of payload
        #     + b'\x00'  # Type: DATA
        #     + b'\x01'  # Flags: END_STREAM
        #     + b'\x00\x00\x00\x01'  # Stream ID: 1
        #     + data_payload
        #     )


        # client_socket.sendall(headers_frame + data_frame)


        

    else:
        try:
            with open(f"files/{GET_request.path}.html", "r") as file:
                html_content = file.read()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    f"Content-Length: {len(html_content)}\r\n"
                    "\r\n"
                    f"{html_content}"
                )
                client_socket.sendall(response.encode('utf-8'))
        except FileNotFoundError:
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: 29\r\n"
                "\r\n"
                "<h1>404 Not Found</h1>"
            )
            client_socket.sendall(response.encode('utf-8'))


def handle_POST(client_socket, request,current_stream_id):
     
                        form_data = request.body.decode('utf-8').split("&")
                        form_data = dict(item.split("=") for item in form_data)
                            
                            # Extract the "name" and "message" fields
                        name = form_data.get("name", "Unknown")
                        message = form_data.get("message", "No message")

                        # session.username=name

                        response_content = f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Submission Response</title>
                        </head>
                        <body>
                            <h1>Form Submitted!</h1>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>Message:</strong> {message}</p>
                            <p><a href="/">Go back</a></p>
                        </body>
                        </html>
                        """
                        headers = [
                                            (":status", "200"),
                                            ("content-type", "text/html"),
                                            ("content-length",f"{len(response_content)}")
                        ]

                        encoded_headers = []
                        for name, value in headers:
                            encoded_headers.extend(encode_header(name, value,dynamic_table))

                        encoded_headers_bytes = bytes(encoded_headers)

                        print(encoded_headers_bytes)

                        headers_frame = (
                                get_response_size(encoded_headers_bytes)  # Length: length of the encoded headers
                                + b'\x01'        # Type: HEADERS
                                + b'\x04'        # Flags: END_HEADERS
                                + current_stream_id.to_bytes(4, byteorder='big')  # request stream id
                                + encoded_headers_bytes)
                
                        data_payload = response_content.encode('utf-8')

                        
                            # Data frame
                        data_frame = (
                            len(data_payload).to_bytes(3, byteorder='big')  # Length of payload
                            + b'\x00'  # Type: DATA
                            + b'\x01'  # Flags: END_STREAM
                            + current_stream_id.to_bytes(4, byteorder='big')  # request stream id
                            + data_payload
                            )
                    

                        client_socket.sendall(headers_frame + data_frame)

                       
                                
    

    #client_socket.sendall(response.encode('utf-8'))



# def handle_http2(client_socket, client_address):
#     """Handles HTTP/2 requests."""
#     try:
#         print(f"Handling HTTP/2 request from {client_address}")
#         #client_socket.settimeout(10)  # Optional timeout

#         # Step 1: Validate the HTTP/2 connection preface
#         raw_data = client_socket.recv(2048)
#         print(raw_data)

#         frames=parse_all_http2_frames(raw_data)

#         for frame in frames:
#             print(frame)

#         print(f"HTTP/2 preface received from {client_address}")

        

#         # Send the SETTINGS ACK now
#         settings_ack = b'\x00\x00\x00'  # Length: 0
#         settings_ack += b'\x04'         # Type: SETTINGS
#         settings_ack += b'\x01'         # Flags: ACK
#         settings_ack += b'\x00\x00\x00\x00'  # Stream ID: 0
#         client_socket.sendall(settings_ack)
#         print(f"SETTINGS ACK sent to {client_address}")
#         encoded_headers = b'\x88\x85'

#       # Step 3: Read the HTML content from a file
#         with open("files/index.html", "r") as file:
#             html_content = file.read()

#         # Convert HTML content to bytes
#         data_payload = html_content.encode('utf-8')  # Encode the string to bytes using UTF-8

#         # Step 4: Respond with HEADERS and DATA frames
#         # Hardcoded HPACK-encoded headers
#         encoded_headers = b'\x88\x85'

#         # Headers frame
#         headers_frame = (
#             b'\x00\x00\x02'  # Length: 2 bytes (size of encoded_headers)
#             + b'\x01'        # Type: HEADERS
#             + b'\x04'        # Flags: END_HEADERS
#             + b'\x00\x00\x00\x01'  # Stream ID: 1
#             + encoded_headers
#         )

#         # Data frame
#         data_frame = (
#             len(data_payload).to_bytes(3, byteorder='big')  # Length of payload
#             + b'\x00'  # Type: DATA
#             + b'\x01'  # Flags: END_STREAM
#             + b'\x00\x00\x00\x01'  # Stream ID: 1
#             + data_payload
#         )

#         # Send HEADERS and DATA frames together
#         client_socket.sendall(headers_frame + data_frame)
#         print(f"Response sent to {client_address}")
#         print(f"Response sent to {client_address}")

#     except ssl.SSLError as e:
#         print(f"SSL error with client {client_address}: {e}")
#     except client_socket.timeout:
#         print(f"Client {client_address} timed out")
#     except Exception as e:
#         print(f"Error handling client {client_address}: {e}")
    

def handle_http2(client_socket, client_address):
    """Handles HTTP/2 requests."""
    try:

        current_stream_id = 1  # Start with stream ID 1 as per HTTP/2 spec

        print(f"Handling HTTP/2 connection from {client_address}")

        settings_frame = b'\x00\x00\x05'  # Length: 5 bytes (size of the payload)
        settings_frame += b'\x04'         # Type: SETTINGS
        settings_frame += b'\x00'         # Flags
        settings_frame += b'\x00\x00\x00\x00'  # Stream ID: 0
        settings_frame += b'\x01'         # SETTINGS_HEADER_TABLE_SIZE
        settings_frame += b'\x00\x00\x00\x00'  # Value: 0 to disable dynamic table
        print("Sent SETTINGS frame")
        while(1):
            print(f"Handling HTTP/2 request from {client_address}")

            #client_socket.settimeout(0.5)  

            raw_data = client_socket.recv(4096)
            print(f"Received raw data: {raw_data}")

            if not raw_data:
                print(f"No data received from {client_address}, closing connection.")
                
                goaway_frame = (
                    b'\x00\x00\x08'  
                    + b'\x07'       
                    + b'\x00'        
                    + b'\x00\x00\x00\x00'  
                    + b'\x00\x00\x00\x00'  
                    + b'\x00'        
                )
                client_socket.sendall(goaway_frame)  # Send GOAWAY frame
                print("Sent GOAWAY frame")
                break  

            frames = parse_all_http2_frames(raw_data)

           
            request=None
            for frame in frames:
                current_stream_id=frame.stream_id
                print(f"Frame received: {frame}")
                if frame.frame_type == 'HEADERS':

                    
                    
                    headers = frame.payload
                    print(f"Headers payload {headers}")
                    # print(f"payload without .hex() {headers}")
                    headers=decode_hpack(headers)
                    filtered_headers = [(name, value) for name, value in headers if name and value]

                    print(filtered_headers)
                    
                    #headers = payload[9:]

                    
                    method=None
                    path=None
                    body=None
                    for name, value in headers:
                        if name == ":method":
                            method = value
                        elif name == ":path":
                            path = value
                        elif name == "content-length":
                            # Body length could be determined by content-length, but for simplicity, we skip it here
                            pass
                    if method=="GET":
                          request=HttpRequest2(method,path if path is not None else '/')
                       #   print(f"request method {request.method} and request path {request.path}")


                elif frame.frame_type == 'DATA' :
                    # Extract the body from DATA frame
                    body_data = frame.payload  # Assuming the payload contains the body
                   # print(f"Received body data: {body_data}")
                    request=None
                    if path and method:
                        request=HttpRequest2(method,path)
                    #    print(f"request method {request.method} and request path {request.path}")
                    # Append the body data to the existing body
                    if request:
                        request.body = body_data
                        print(f"Updated body: {request.body}")

                        print(f"request method {request.method} , request path {request.path} and request body {request.body}")
                
                if request and request.method=="GET":
                     
                  #  print("hereeeeee")
                    with open("files/index.html", "r") as file:
                        html_content = file.read()
        
                    headers = [
                        (":status", "200"),
                        ("content-type", "text/html"),
                        ("content-length",f"{len(html_content)}")
                    ]

                    encoded_headers = []
                    for name, value in headers:
                        encoded_headers.extend(encode_header(name, value,dynamic_table))

                    encoded_headers_bytes = bytes(encoded_headers)

                    print(encoded_headers_bytes)

                    headers_frame = (
                            get_response_size(encoded_headers_bytes)  # Length: (size of encoded_headers)
                            + b'\x01'        # Type: HEADERS
                            + b'\x04'        # Flags: END_HEADERS
                            + current_stream_id.to_bytes(4, byteorder='big')  # Stream ID: 1
                            + encoded_headers_bytes)
            
                    data_payload = html_content.encode('utf-8')

                    
                        # Data frame
                    data_frame = (
                        len(data_payload).to_bytes(3, byteorder='big')  # Length of payload
                        + b'\x00'  # Type: DATA
                        + b'\x01'  # Flags: END_STREAM
                        + current_stream_id.to_bytes(4, byteorder='big')  # Stream ID: 1
                        + data_payload
                        )
                  

                    client_socket.sendall(headers_frame + data_frame)

                    print(f"Response sent to {client_address}")

                if request and request.method=="POST" and request.body is not None:
                     handle_POST(client_socket,request,current_stream_id)
                     print(f"Response sent to {client_address}")

            if(request and request.method=="GET"):
                 pass
               #  handle_GET(client_socket,request)
               
             

          

        

    except ssl.SSLError as e:
            print(f"SSL error with client {client_address}: {e}")
    except client_socket.timeout:
            print(f"Client {client_address} timed out")
    except Exception as e:
            print(f"Error handling client {client_address}: {e}")




def get_response_size(encoded_headers):
    # Get the size of the encoded headers
    header_size = len(encoded_headers)

    # Ensure the size is within the 24-bit frame length (max 16,777,215 bytes)
    if header_size > 16777215:
        raise ValueError("Encoded headers size exceeds maximum allowed frame size")

    # Return the size in the 3-byte format required for the frame header
    # This is the length in big-endian byte order
    return header_size.to_bytes(3, 'big')
     
     

