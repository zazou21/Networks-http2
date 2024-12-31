"""Implementing HPACK compression to be able to decode and encode requests and responses"""

"""static_table"""


""""prefixes"""

"""Check for entry in dynamic or static table"""

#1 INDEXED HEADER FIELD


"""This adds a new header to the dynamic table"""


#01 LITERAL HEADER FIELD WITH INDEXING



#0000 LITERAL HEADER FIELD WITHOUT INDEXING




from collections import deque









# HPACK Static Table
hpack_static_table = [
    (":authority", ""),                      # 1
    (":method", "GET"),                      # 2
    (":method", "POST"),                     # 3
    (":path", "/"),                          # 4
    (":path", "/index.html"),                # 5
    (":scheme", "http"),                     # 6
    (":scheme", "https"),                    # 7
    (":status", "200"),                      # 8
    (":status", "204"),                      # 9
    (":status", "206"),                      # 10
    (":status", "304"),                      # 11
    (":status", "400"),                      # 12
    (":status", "404"),                      # 13
    (":status", "500"),                      # 14
    ("accept-charset", ""),                  # 15
    ("accept-encoding", "gzip, deflate"),    # 16
    ("accept-language", ""),                 # 17
    ("accept-ranges", ""),                   # 18
    ("accept", ""),                          # 19
    ("access-control-allow-origin", ""),     # 20
    ("age", ""),                             # 21
    ("allow", ""),                           # 22
    ("authorization", ""),                   # 23
    ("cache-control", ""),                   # 24
    ("content-disposition", ""),             # 25
    ("content-encoding", ""),                # 26
    ("content-language", ""),                # 27
    ("content-length", ""),                  # 28
    ("content-location", ""),                # 29
    ("content-range", ""),                   # 30
    ("content-type", ""),                    # 31
    ("cookie", ""),                          # 32
    ("date", ""),                            # 33
    ("etag", ""),                            # 34
    ("expect", ""),                          # 35
    ("expires", ""),                         # 36
    ("from", ""),                            # 37
    ("host", ""),                            # 38
    ("if-match", ""),                        # 39
    ("if-modified-since", ""),               # 40
    ("if-none-match", ""),                   # 41
    ("if-range", ""),                        # 42
    ("if-unmodified-since", ""),             # 43
    ("last-modified", ""),                   # 44
    ("link", ""),                            # 45
    ("location", ""),                        # 46
    ("max-forwards", ""),                    # 47
    ("proxy-authenticate", ""),              # 48
    ("proxy-authorization", ""),             # 49
    ("range", ""),                           # 50
    ("referer", ""),                         # 51
    ("refresh", ""),                         # 52
    ("retry-after", ""),                     # 53
    ("server", ""),                          # 54
    ("set-cookie", ""),                      # 55
    ("strict-transport-security", ""),       # 56
    ("transfer-encoding", ""),               # 57
    ("user-agent", ""),                      # 58
    ("vary", ""),                            # 59
    ("via", ""),                             # 60
    ("www-authenticate", "")                 # 61
]





class DynamicTable:
    def __init__(self, max_size=4096):
        self.table = deque()  # Using deque for fast appends and pops
        self.max_size = max_size  
    def get_table(self):
        # Return the current entries in the dynamic table
        return list(self.table)

    def add_entry(self, name, value):
        # Create the header tuple
        entry = (name, value)

        
        entry_size = len(name) + len(value) + 32  # 32 bytes for name and value encoding overhead

        
        while entry_size > self.max_size and len(self.table) > 0:
            evicted_entry = self.table.popleft()  
            evicted_size = len(evicted_entry[0]) + len(evicted_entry[1]) + 32
            self.max_size += evicted_size 
        
        # Add the new entry to the table
        self.table.append(entry)





dynamic_table = DynamicTable()


def get_prefix(encoded_block,prefix_size=3):
    mask = (1 << prefix_size) - 1
    first_byte = encoded_block[0]
    prefix = first_byte & mask
    return prefix

def decode_hpack(payload):
    """Simple HPACK decoder for indexed and literal headers."""
    headers = []
    i = 0
  
    while i < len(payload):
      

        byte = payload[i]
        
        if byte & 0x80:  # Indexed header field (1xxxxxxx)

          

            index = byte & 0x7F  # Clear the high bit
            if 1 <= index <= len(hpack_static_table):
                headers.append(hpack_static_table[index - 1])
            else:
                pass
               #  print(f"Invalid index: {index}")
            i += 1

        elif byte & 0x40:  # Literal header field with incremental indexing
            # Read the length of the header field name (variable length)
            length_field = payload[i + 1]
            try:
                name = payload[i + 2:i + 2 + length_field].decode("utf-8")
            except UnicodeDecodeError as e:
               # print(f"UnicodeDecodeError while decoding name: {e}")
                name = None
            
            try:
                value = payload[i + 2 + length_field:i + 2 + length_field + 1].decode("utf-8")
            except UnicodeDecodeError as e:
                #print(f"UnicodeDecodeError while decoding value: {e}")
                value = None
                
            
            headers.append((name, value))
            #print(f"Literal header with incremental indexing: {name} = {value}")
            i += 2 + length_field + 1

        elif byte & 0x20:  # Literal header field without incremental indexing
            # Read the length of the header field name (variable length)
            length_field = payload[i + 1]
            try:
                name = payload[i + 2:i + 2 + length_field].decode("utf-8")
            except UnicodeDecodeError as e:
             #   print(f"UnicodeDecodeError while decoding name: {e}")
                name = None
            
            try:
                value = payload[i + 2 + length_field:i + 2 + length_field + 1].decode("utf-8")
            except UnicodeDecodeError as e:
              #  print(f"UnicodeDecodeError while decoding value: {e}")
                value = None
            
            headers.append((name, value))
         #   print(f"Literal header without incremental indexing: {name} = {value}")
            i += 2 + length_field + 1
        
        else:
       #     print(f"Unsupported header type: {byte}")
            i += 1

    return headers
# def decode_hpack(payload):
#     """Simple HPACK decoder for indexed and literal headers."""
#     headers = []
#     dynamic_table = deque(maxlen=100)  # Optional: Dynamic table for incremental indexing
#     i = 0

#     while i < len(payload):
#         byte = payload[i]
#         print(f"payload[{i}] = {byte:#04x}")
#         print(f"Processing byte: {byte:#x} at index {i}")

#         if byte & 0x80:  # Indexed header field (1xxxxxxx)
#             index = byte & 0x7F  # Clear the high bit
#             if 1 <= index <= len(hpack_static_table):
#                 headers.append(hpack_static_table[index - 1])
#             else:
#                 print(f"Invalid index: {index}")
#             i += 1

#         elif byte & 0x40:  # Literal header field with incremental indexing
#             # Name length
#             if i + 1 >= len(payload):
#                 print(f"Error: Incomplete payload at index {i}.")
#                 break

#             name_length = payload[i + 1]
#             print(f"Name length: {name_length}")

#             # Name and value boundaries
#             name_end = i + 2 + name_length
#             if name_end >= len(payload):
#                 print(f"Error: Name end exceeds payload length at index {i}.")
#                 break

#             value_length = payload[name_end]
#             value_start = name_end + 1
#             value_end = value_start + value_length

#             if value_end > len(payload):
#                 print(f"Error: Value end exceeds payload length at index {i}.")
#                 break

#             # Decode name and value
#             try:
#                 name = payload[i + 2:name_end].decode("utf-8")
#                 value = payload[value_start:value_end].decode("utf-8")
#                 print(f"Literal header: {name} = {value}")
#             except UnicodeDecodeError as e:
#                 print(f"UnicodeDecodeError while decoding name or value: {e}")
#                 name, value = "<invalid_name>", "<invalid_value>"

#             headers.append((name, value))
#             dynamic_table.append((name, value))  # Optional
#             i = value_end

#         elif byte & 0x20:  # Literal header field without incremental indexing
#             # Same logic as above, but without adding to the dynamic table
#             if i + 1 >= len(payload):
#                 print(f"Error: Incomplete payload at index {i}.")
#                 break

#             name_length = payload[i + 1]
#             name_end = i + 2 + name_length
#             if name_end >= len(payload):
#                 print(f"Error: Name end exceeds payload length at index {i}.")
#                 break

#             value_length = payload[name_end]
#             value_start = name_end + 1
#             value_end = value_start + value_length

#             if value_end > len(payload):
#                 print(f"Error: Value end exceeds payload length at index {i}.")
#                 break

#             try:
#                 name = payload[i + 2:name_end].decode("utf-8")
#                 value = payload[value_start:value_end].decode("utf-8")
#                 print(f"Literal header: {name} = {value}")
#             except UnicodeDecodeError as e:
#                 print(f"UnicodeDecodeError while decoding name or value: {e}")
#                 name, value = "<invalid_name>", "<invalid_value>"

#             headers.append((name, value))
#             i = value_end

#         else:
#             print(f"Unsupported header type: {byte:#x}")
#             i += 1

#     return headers




# def decode_hpack(payload):
#     """Improved HPACK decoder for indexed and literal headers."""
#     headers = []
#     dynamic_table = deque(maxlen=100)  # You can keep the dynamic table here if needed
#     i = 0
    
#     while i < len(payload):
#         byte = payload[i]
#         print(f"Processing byte: {byte:#x} at index {i}")
        
#         if byte & 0x80:  # Indexed header field (1xxxxxxx)
#             index = byte & 0x7F  # Clear the high bit
#             if 1 <= index <= len(hpack_static_table):
#                 header = hpack_static_table[index - 1]
#                 headers.append(header)
#                 print(f"Indexed header: {header}")
#             else:
#                 print(f"Invalid index: {index}")
#             i += 1

#         elif byte & 0x40:  # Literal header field with incremental indexing (01xxxxxx)
#             i, header = parse_literal_header(payload, i, dynamic_table, incremental=True)
#             if header:
#                 headers.append(header)

#         elif byte & 0x20:  # Dynamic table size update (001xxxxx)
#             print("Dynamic table size update encountered (not implemented).")
#             i += 1  # Move to the next byte (assuming dynamic table size update is ignored)

#         elif byte & 0x10 == 0:  # Literal header field without indexing (0000xxxx)
#             i, header = parse_literal_header(payload, i, dynamic_table, incremental=False)
#             if header:
#                 headers.append(header)

#         else:
#             print(f"Unsupported header type: {byte:#x}")
#             i += 1

#     return headers  # Only return the decoded headers


# def parse_literal_header(payload, start_index, dynamic_table, incremental):
#     """Parse a literal header field."""
#     try:
#         length_field = payload[start_index + 1]
#         name_end = start_index + 2 + length_field
#         value_start = name_end + 1
#         value_length = payload[value_start - 1]

#         name = payload[start_index + 2:name_end].decode("utf-8", errors="replace")
#         value = payload[value_start:value_start + value_length].decode("utf-8", errors="replace")

#         print(f"Literal header parsed: {name} = {value}")
#         if incremental:
#             dynamic_table.append((name, value))  # Optional: Add to dynamic table

#         return value_start + value_length, (name, value)

#     except (IndexError, UnicodeDecodeError) as e:
#         print(f"Error parsing literal header: {e}")
#         return start_index + 2, ("<invalid_name>", "<invalid_value>")





import binascii



# Huffman Codes for a few characters (this is a simplified set, real HPACK uses a full table)
huffman_table = {
    'a': '00000',
    'b': '00001',
    'c': '00010',
    'd': '00011',
    'e': '00100',
    'f': '00101',
    'g': '00110',
    'h': '00111',
    'i': '01000',
    'j': '01001',
    'k': '01010',
    'l': '01011',
    'm': '01100',
    'n': '01101',
    'o': '01110',
    'p': '01111'
}


# def encode_integer(value, prefix_bits=7):
#     if value < (1 << prefix_bits):
#         return [value]
#     else:
#         result = []
#         while value >= (1 << prefix_bits):
#             result.append((value & 0x7F) | 0x80)  # Set MSB for more bytes
#             value >>= 7
#         result.append(value & 0x7F)  # Last byte without MSB
#         return result[::-1]  # Reverse to get the correct order


def encode_integer(value, prefix_bits):
    max_prefix_value = (1 << prefix_bits) - 1
    if value < max_prefix_value:
        return bytes([value])
    else:
        result = [max_prefix_value]
        value -= max_prefix_value
        while value >= 128:
            result.append((value % 128) + 128)
            value //= 128
        result.append(value)
        return bytes(result)

def encode_string(value,flag):
    huffman=0x80 if flag else 0x00
    encoded_string=value.encode("utf-8")
    length=encode_integer(len(encoded_string),7)
    return encoded_string




# Simple Huffman encoding function
def huffman_encode(data):
    encoded = ''.join(huffman_table.get(c, '') for c in data)
    return encoded

# # Simple function to encode headers
# def encode_header(name, value,add_to_dynamic_table_flag=True):
#     # Check if the header name exists in the static table
#     for idx, (static_name, static_value) in enumerate(hpack_static_table):
#         if name == static_name and value == static_value:
#             encoded_integer=encode_integer(idx, 7)
#             # Return the index (indexed header)
#             return [encoded_integer[0] | 0x80] +encoded_integer[1:]
        
#     for idx, (static_name,static_value) in enumerate(hpack_static_table):
#         if name==static_name:
#             encoded_name_index = encode_integer(idx, 7)
#             encoded_value = encode_string(value)
#         return encoded_name_index + encoded_value

#     # If not found, encode literally (this part should encode the name and value)
#     # First encode the name length
#     name_length = len(name)
#     value_length = len(value)
#     encoded_name = huffman_encode(name)  # Huffman encode header name
#     name_length_encoding = encode_integer(name_length, 7)
#     value_length_encoding = encode_integer(value_length, 7)

#     # Return the encoded parts: name, value
#     return name_length_encoding + value_length_encoding + list(map(int, encoded_name))

# Example to encode headers
# headers = [
#     (":method", "GET"),
#     (":path", "/"),
#     ("x-custom-header", "value123")
# ]

def encode_header(name, value, dynamic_table, add_to_dynamic_table_flag=True):
    # Case 1: If both name and value exist in the static table
    for idx, (static_name, static_value) in enumerate(hpack_static_table):
        if name == static_name and value == static_value:
            encoded_integer = encode_integer(idx+1, 7)  # Indexed header
            return bytes([encoded_integer[0] | 0x80]) + bytes(encoded_integer[1:])

    # Case 2: If name and value exist in the dynamic table (indexed header)
    for idx, (dynamic_name, dynamic_value) in enumerate(dynamic_table.get_table()):
        if name == dynamic_name and value == dynamic_value:
            encoded_integer = encode_integer(idx + 62, 7)  # Indexed header in dynamic table
            return bytes([encoded_integer[0] | 0x80]) + bytes(encoded_integer[1:])

 # Case 3: If only the name exists in the static table, encode the name and value literally
    for idx, (static_name, static_value) in enumerate(hpack_static_table):
        if name == static_name:
            # Use the flag for indexed name with literal value (0x40)
            encoded_name_index = encode_integer(idx+1, 6)  
            encoded_name_index = bytearray(encoded_name_index)  
            encoded_name_index[0] |= 0x40  

           
            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value, False)  # Encode value literally

            if add_to_dynamic_table_flag:
                dynamic_table.add_entry(name, value)  # Add to dynamic table

            return bytes(encoded_name_index) + bytes(value_length) + bytes(encoded_value)


    # Case 4: If only the name exists in the dynamic table, encode the name using index and value literally
    for idx, (dynamic_name, dynamic_value) in enumerate(dynamic_table.get_table()):
        if name == dynamic_name:
           
            encoded_name_index = encode_integer(idx + 62, 6)  # Indexed name in dynamic table
          
            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value)  
            if add_to_dynamic_table_flag:
                dynamic_table.add_entry(name, value)  # Add to dynamic table
            return bytes(encoded_name_index) + bytes(value_length) + bytes(encoded_value)

    # Case 5: If neither the name nor value exists in the static or dynamic table, encode both literally
    # Encode name and value literally
    encoded_name = encode_string(name)
    encoded_value = encode_string(value)
    name_length_encoding = encode_integer(len(name), 7)  # Length of name
    value_length_encoding = encode_integer(len(value), 7)  # Length of value

    if add_to_dynamic_table_flag:
        dynamic_table.add_entry(name, value)  # Add to dynamic table

    return bytes(name_length_encoding) + bytes(value_length_encoding) + bytes(encoded_name) + bytes(encoded_value)
# with open("Server/files/index.html", "r") as file:
#             html_content = file.read()

# print(len(html_content))

# headers = [
#             (":status", "200"),
#             ("content-type", "text/html"),
#             ("content-length",f"{len(html_content)}")
#         ]

# encoded_headers = []
# for name, value in headers:
#     encoded_headers.extend(encode_header(name, value,dynamic_table))

# print("Encoded Headers (hex):", encoded_headers)

# encoded_headers_bytes = bytes(encoded_headers)

# # Print the result as a hex string for verification
# print("Encoded Headers (hex):", encoded_headers_bytes.hex())