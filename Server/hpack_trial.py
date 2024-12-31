from venv import logger
import hpack

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















max_table_size = 100



class DynamicTable:
    def __init__(self, max_size=4096):
        self.table = deque()  # Using deque for fast appends and pops
        self.max_size = max_size  # Maximum size of the dynamic table in bytes

    def get_table(self):
        # Return the current entries in the dynamic table
        return list(self.table)

    def add_entry(self, name, value):
        # Create the header tuple
        entry = (name, value)

        # Calculate the size of the new entry
        entry_size = len(name) + len(value) + 32  # 32 bytes for name and value encoding overhead

        # Evict entries if adding the new entry exceeds the max size
        while entry_size > self.max_size and len(self.table) > 0:
            evicted_entry = self.table.popleft()  # Evict the oldest entry
            evicted_size = len(evicted_entry[0]) + len(evicted_entry[1]) + 32
            self.max_size += evicted_size  # Recalculate the max size after eviction
        
        # Add the new entry to the table
        self.table.append(entry)





dynamic_table = DynamicTable()

dump='80000000db82cb8704896251f7310f52e621ffc8c6cac953b1352398ac0fb9a5fa352398ac782c75fd1a91cc56075d537d1a91cc5611de6ff7e69a3e8d48e62b1f3f5f2c7cfdf6800bbd7f068840e92ac7b0d31aaf7f0685a8eb10f6237f0584352398bf73919d29ad1718602275702e05c371e03cdb1fc5c47f0485b600fd286f'

encoded_header=bytes.fromhex(dump)




def decode_integer(data, prefix_bits):
    """
    Decodes an integer from the HPACK variable-length encoding.
    """
    mask = (1 << prefix_bits) - 1 
    value = data[0] & mask  
    if value < mask:  
        return value, 1

    value = mask
    shift = 0
    i = 1
    while True:
        B = data[i] 
        value += (B & 0x7F) << shift  
        shift += 7
        if not (B & 0x80):
            break
        i += 1

    return value, i + 1


def decode_string(data):
    """
    Decodes a string from HPACK format.
    """
    huffman = data[0] & 0x80
    # if huffman:
    #     length, consumed = decode_integer(data, 7)
    #     string = ht.decode_huffman(data[consumed:consumed + length])
    #     return string, consumed + length
    length, consumed = decode_integer(data, 7)
    string = data[consumed:consumed + length].decode("utf-8")
    return string, consumed + length

def decode(dynamic_table, data):
    try:
        headers = []
        i = 0
        while i < len(data):
            byte = data[i]
            if byte & 0x80: # Index Representation
                index, consumed = decode_integer(data[i:], 7)
                i += consumed
                if index < 62:
                    name, value = hpack_static_table[index]
                else:
                    name, value = dynamic_table.get_entry(index)
                headers.append((name, value))

            elif byte & 0x40:
                index, consumed = decode_integer(data[i:], 6)
                if index == 0: # New Name Incremental Indexing
                    i += consumed
                    name, consumed = decode_string(data[i:])
                    i += consumed
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    dynamic_table.add_entry(name, value)
                    headers.append((name, value))
                elif index: # Indexed Name Incremental Indexing
                    i += consumed
                    if index < 62:
                        name, _ = hpack_static_table[index]
                    else:
                        name, _ = dynamic_table.get_entry(index)
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    dynamic_table.add_entry(name, value)
                    headers.append((name, value))
                else:
                    return headers

            elif byte & 0x10:
                index, consumed = decode_integer(data[i:], 4)
                if index == 0: #New Name Never Incremental Indexing
                    i += consumed
                    name, consumed = decode_string(data[i:])
                    i += consumed
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    headers.append((name, value))
                elif index: #Indexed Name Never Incremental Indexing
                    i += consumed
                    if index < 62:
                        name, _ = hpack_static_table[index]
                    else:
                        name, _ = dynamic_table.get_entry(index)
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    headers.append((name, value))
                else:
                    return headers
            elif byte & 0x20: #Update Dynamic Table Max Size
                index, consumed = decode_integer(data[i:], 5)
                i += consumed
                dynamic_table.update_max_size(index)

            else:
                index, consumed = decode_integer(data[i:], 4)
                if index == 0: #New Name without Incremental Indexing
                    i += consumed
                    name, consumed = decode_string(data[i:])
                    i += consumed
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    headers.append((name, value))
                elif index: #Indexed Name without Incremental Indexing
                    i += consumed
                    if index < 62:
                        name, _ = hpack_static_table[index]
                    else:
                        name, _ = dynamic_table.get_entry(index)
                    value, consumed = decode_string(data[i:])
                    i += consumed
                    headers.append((name, value))
                else:
                    return headers

        return headers
    except Exception as e:
        logger.info(f"Error in decoding: {e}")
        return []






######################################################


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
            encoded_name_index = encode_integer(idx+1, 6)  # Use 6 bits for the index
            encoded_name_index = bytearray(encoded_name_index)  # Convert to bytearray for modification
            encoded_name_index[0] |= 0x40  # Set the flag for "indexed name + literal value

            # Encode value length (should come before the value)
            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value, False)  # Encode value literally

            if add_to_dynamic_table_flag:
                dynamic_table.add_entry(name, value)  # Add to dynamic table

            return bytes(encoded_name_index) + bytes(value_length) + bytes(encoded_value)


    # Case 4: If only the name exists in the dynamic table, encode the name using index and value literally
    for idx, (dynamic_name, dynamic_value) in enumerate(dynamic_table.get_table()):
        if name == dynamic_name:
            # Index the name, encode the value literally
            encoded_name_index = encode_integer(idx + 62, 6)  # Indexed name in dynamic table
            # Encode value length (should come before the value)
            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value)  # Encode value literally
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

# headers = [
#     (":status", "200"),
#     ("content-type", "text/html")
# ]
 
with open("Server/files/index.html", "r") as file:
            html_content = file.read()

print(len(html_content))

encoded_headers=[]

print(len(html_content))
        
       
        #x88\xbe\xbf
headers = [
            (":status", "200"),
            ("content-type", "text/html"),
            ("content-length",f"{len(html_content)}")
        ]

encoded_headers = []
for name, value in headers:
            encoded_headers.extend(encode_header(name, value,dynamic_table))

     
encoded_headers_bytes = bytes(encoded_headers)

print(encoded_headers_bytes.hex())
