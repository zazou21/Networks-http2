from HPACK import *


class HttpRequest2:
    def __init__(self, method, path, body=None):
        self.method = method
        self.path = path
        self.body = body


def create_response_frame(headers, response_content, current_stream_id, dynamic_table):

    # Encode headers
    encoded_headers = []
    for name, value in headers:
        encoded_headers.extend(encode_header(name, value, dynamic_table))

    encoded_headers_bytes = bytes(encoded_headers)
    print(encoded_headers_bytes)

    # Prepare the headers frame
    headers_frame = (
        get_response_size(encoded_headers_bytes)  # Length of the encoded headers
        + b"\x01"  # Type: HEADERS
        + b"\x04"  # Flags: END_HEADERS
        + current_stream_id.to_bytes(4, byteorder="big")  # request stream ID
        + encoded_headers_bytes
    )

    # Encode the data payload
    if isinstance(response_content, str):
        data_payload = response_content.encode("utf-8")
    else:
        data_payload = response_content  # Already bytes

    # Create the data frame
    data_frame = (
        len(data_payload).to_bytes(3, byteorder="big")  # Length of payload
        + b"\x00"  # Type: DATA
        + b"\x01"  # Flags: END_STREAM
        + current_stream_id.to_bytes(4, byteorder="big")  # request stream ID
        + data_payload
    )

    # Return the combined frames: headers frame followed by data frame
    return headers_frame + data_frame


def get_response_size(encoded_headers):
    # Get the size of the encoded headers
    header_size = len(encoded_headers)

    # Ensure the size is within the 24-bit frame length (max 16,777,215 bytes)
    if header_size > 16777215:
        raise ValueError("Encoded headers size exceeds maximum allowed frame size")

    # Return the size in the 3-byte format required for the frame header
    # This is the length in big-endian byte order
    return header_size.to_bytes(3, "big")
