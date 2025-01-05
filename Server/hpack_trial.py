from venv import logger
import hpack
import re

from bitarray import bitarray

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








# huffman_table= {0b000000: ' ', 0b000001: '!', 0b000010: '"', 0b000011: '#',
#             0b000100: '$', 0b000101: '%', 0b000110: '&', 0b000111: "'",
#             0b001000: '(', 0b001001: ')', 0b001010: '*', 0b001011: '+',
#             0b001100: ',', 0b001101: '-', 0b001110: '.', 0b001111: '/',
#             0b010000: '0', 0b010001: '1', 0b010010: '2', 0b010011: '3',
#             0b010100: '4', 0b010101: '5', 0b010110: '6', 0b010111: '7',
#             0b011000: '8', 0b011001: '9', 0b011010: ':', 0b011011: ';',
#             0b011100: '<', 0b011101: '=', 0b011110: '>', 0b011111: '?',
#             0b100000: '@', 0b100001: 'A', 0b100010: 'B', 0b100011: 'C',
#             0b100100: 'D', 0b100101: 'E', 0b100110: 'F', 0b100111: 'G',
#             0b101000: 'H', 0b101001: 'I', 0b101010: 'J', 0b101011: 'K',
#             0b101100: 'L', 0b101101: 'M', 0b101110: 'N', 0b101111: 'O',
#             0b110000: 'P', 0b110001: 'Q', 0b110010: 'R', 0b110011: 'S',
#             0b110100: 'T', 0b110101: 'U', 0b110110: 'V', 0b110111: 'W',
#             0b111000: 'X', 0b111001: 'Y', 0b111010: 'Z', 0b111011: '[',
#             0b111100: '\\', 0b111101: ']', 0b111110: '^', 0b111111: '_',
#         }



huffman_dict = {
    '0':bitarray('00000'),
    '1': bitarray('00001'),
    '2':bitarray('00010'),
    '3': bitarray('011001'),
    '4': bitarray('011010'),
    '5':bitarray('011011'),
    '6':bitarray('011100'),
    '7':bitarray('011101'),
    '8':bitarray('011110'),
    '9':bitarray('011111'),
    ':':bitarray('1011100'),
    '.':bitarray('010111'),
    'A': bitarray('100001'),
    'B': bitarray('1011101'),
    'C': bitarray('1011110'),
    'D': bitarray('1011111'),
    'E': bitarray('1100000'),
    'F': bitarray('1100001'),
    'G': bitarray('1100010'),
    'H': bitarray('1100011'),
    'I': bitarray('1100100'),
    'J': bitarray('1100101'),
    'K': bitarray('1100110'),
    'L': bitarray('1100111'),
    'M': bitarray('1101000'),
    'N': bitarray('1101001'),
    'O': bitarray('1101010'),
    'P': bitarray('1101011'),
    'Q': bitarray('1101100'),
    'R': bitarray('1101101'),
    'S': bitarray('1101110'),
    'T': bitarray('1101111'),
    'U': bitarray('1110000'),
    'V': bitarray('1110001'),
    'W': bitarray('1110010'),
    'X': bitarray('11111100'),
    'Y': bitarray('1110011'),
    'Z': bitarray('11111101'),
    '[': bitarray('11111111') + bitarray('11011'),
    '\\': bitarray('11111111') + bitarray('11111110') + bitarray('000'),
    ']': bitarray('11111111') + bitarray('11100'),
    '^': bitarray('11111111') + bitarray('111100'),
    '_': bitarray('100010'),
    'a': bitarray('00011'),
    'b': bitarray('100011'),
    'c': bitarray('00100'),
    'd': bitarray('100100'),
    'e': bitarray('00101'),
    'f': bitarray('100101'),
    'g': bitarray('100110'),
    'h': bitarray('100111'),
    'i': bitarray('00110'),
    'j': bitarray('1110100'),
    'k': bitarray('1110101'),
    'l': bitarray('101000'),
    'm': bitarray('101001'),
    'n': bitarray('101010'),
    'o': bitarray('00111'),
    'p': bitarray('101011'),
    'q': bitarray('1110110'),
    'r': bitarray('101100'),
    's': bitarray('01000'),
    't': bitarray('01001'),
    'u': bitarray('101101'),
    'v': bitarray('1110111'),
    'w': bitarray('1111000'),
    'x': bitarray('1111001'),
    'y': bitarray('1111010'),
    'z': bitarray('1111011'),
    '-': bitarray('010110'),
    ' ': bitarray('010100'),
    '!': bitarray('11111110') + bitarray('00'),
    '"': bitarray('11111110') + bitarray('01'),
    '#': bitarray('11111111') + bitarray('1010'),
    '$': bitarray('11111111') + bitarray('11001'),
    '%': bitarray('010101'),
    '&': bitarray('11111000'),
    "'": bitarray('11111111') + bitarray('010'),
    '(': bitarray('11111110') + bitarray('10'),
    ')': bitarray('11111110') + bitarray('11'),
    '*': bitarray('11111001'),
    '+': bitarray('11111111') + bitarray('011'),
    ',': bitarray('11111010'),
    '/': bitarray('011000'),
    ';': bitarray('11111011'),
    '<': bitarray('11111111') + bitarray('1111100'),
    '=': bitarray('100000'),
    '>': bitarray('11111111') + bitarray('1011'),
    '?': bitarray('11111111') + bitarray('00'),
    '@': bitarray('11111111') + bitarray('11010')
}


# def decode_huffman(encoded_bits):
#     """Decode a bitstream into the original data based on RFC 7541 Huffman codes."""
#     decoded_string = ''
#     buffer = 0  # This will hold the bits we process
#     buffer_length = 0  # This tracks the number of bits in the buffer
    
#     # Go through the bitstream (encoded_bits should be a list of bits, not bytes)
#     for bit in encoded_bits:
#         buffer = (buffer << 1) | bit
#         buffer_length += 1
            
#         # Check if the current buffer matches any Huffman code
#         if buffer in huffman_table:
#             decoded_string += huffman_table[buffer]
#             buffer = 0  # Reset the buffer
#             buffer_length = 0  # Reset the bit count
#     return decoded_string




def decode_huffman(huffman_encoded):
    """Decode the Huffman-encoded bitarray."""
    decoded_string = ''
    
    # Convert bytes to bitarray
    bitstream = bitarray()
    bitstream.frombytes(huffman_encoded)
    print(f"number of bits {len(bitstream)}")
    position=0
    
    
    # Decode the bitstream using the Huffman dictionary
    try:
        # Extract decoded characters from the iterator and join them into a string
        decoded_string = ''.join(bitstream.decode(huffman_dict))
        
    except ValueError as e:
        print(f"Error decoding bitstream: {e}")
        match = re.search(r'at position (\d+)', str(e))
        if match:
             position = int(match.group(1))  # Extracted bit position
             print(f"Problematic bit position: {position}")
        decoded_string = ''.join(bitstream[:position].decode(huffman_dict))

        
        return decoded_string
    
    return decoded_string

def get_bits_from_bytes(byte_data):
    """Convert bytes into a list of bits."""
    bits = []
    for byte in byte_data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)  # Extract each bit, from MSB to LSB
    return bits


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



def decode_integer_hpack(payload, start_index=0):
    """Decode an integer from the HPACK format (RFC 7541)."""
    # Single byte encoding (7 bits) - when the value fits in a single byte
    byte = payload[start_index]
    if byte & 0x80 == 0:  # 7-bit integer
        value = byte
        length = 1
    else:
        # Multiple byte encoding (8-32 bits)
        value = byte & 0x7F  # First 7 bits of the integer
        length = 1
        while payload[start_index + length] & 0x80 != 0:  # While there are more bytes
            value = (value << 7) | (payload[start_index + length] & 0x7F)
            length += 1
        value = (value << 7) | (payload[start_index + length - 1] & 0x7F)  # Add last byte value

    return value, length

def decode_string_literal_hpack(payload, start_index, length):
    """Decode a string literal (name, value) from the HPACK format (RFC 7541).
    
    Args:
    - payload: The byte sequence containing the header.
    - start_index: The starting index to begin decoding.
    - length: The total length of the header field (including name and value lengths).

    Returns:
    - A tuple with (name, value) and the number of bytes processed.
    """
    # Start index points to the byte after the header's type byte (which is already handled)
    
    # First, extract the name length (this part is already pre-calculated)
    # Assuming 'length' is a tuple of (name_length, value_length)
    name = payload[start_index:start_index +length].decode("utf-8", errors="ignore")
    
    
    return name




    
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
            i += 1

        elif byte & 0x40:  # Literal header field with incremental indexing
            print(f"here {i}")
            index=byte & 0x3F
            if 1 <= index <= len(hpack_static_table):
                name=hpack_static_table[index - 1]

                #value_length=decode_integer_hpack(payload,i+1)
                
                value_length=payload[i+1] & 0x7f

                print(f"value_length {value_length} {i}")

                if payload[i+1] & 0x7f:
                    
                    huffman_encoded=payload[i+2:i+2+value_length]

                    value=decode_huffman(huffman_encoded)

                else:
                      value= decode_string_literal_hpack(payload,i+2,value_length)
              

                headers.append((name,value))

                i+=2+value_length

            else:
               # name_length=decode_integer_hpack(payload,i+1)
                # Name length and Huffman check for name decoding
                name_length = payload[i+1] & 0x7f
                if payload[i+1] & 0x80:  # Check if the name is Huffman encoded
                    huffman_encoded_name = payload[i+2:i+2+name_length]
                    name = decode_huffman(huffman_encoded_name)
                else:
                    name = decode_string_literal_hpack(payload, i+2, name_length)

                i += 2 + name_length

                # Value length and Huffman check for value decoding
                value_length = payload[i] & 0x7f

                print(f"value_length (else) {value_length} {i}")

                if payload[i] & 0x7f:
                    huffman_encoded = payload[i+1:i+1+value_length]
                    value = decode_huffman(huffman_encoded)
                else:
                    value = decode_string_literal_hpack(payload, i+1, value_length)

                i += 1 + value_length

                headers.append((name, value))
                
        

        elif (byte & 0xF0) ==0  or (byte & 0x10):  # Literal header field without incremental indexing
            index=byte & 0x0F
            if 1 <= index <= len(hpack_static_table):
                name=hpack_static_table[index - 1]

                #value_length=decode_integer_hpack(payload,i+1)
                value_length=payload[i+1] & 0x7f

                value= decode_string_literal_hpack(payload,i+2,value_length)

                headers.append((name,value))

                i+=2+value_length

            else:
               # name_length=decode_integer_hpack(payload,i+1)
                name_length=payload[i+1] & 0x7f

                name=decode_string_literal_hpack(payload,i+2,name_length)

                i+=2+name_length

              #  value_length=decode_integer(payload,i)

                value_length=payload[i] & 0x7f

                value=decode_string_literal_hpack(payload,i+1,value_length)

                i+=1+value_length


                headers.append((name,value))
            


    return headers




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






######################################################


import binascii





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
 
# with open("Server/files/index.html", "r") as file:
#             html_content = file.read()

# print(len(html_content))

# encoded_headers=[]

# print(len(html_content))
        
       
#         #x88\xbe\xbf
# headers = [
#             (":status", "200"),
#             ("content-type", "text/html"),
#             ("content-length",f"{len(html_content)}")
#         ]

# encoded_headers = []
# for name, value in headers:
#             encoded_headers.extend(encode_header(name, value,dynamic_table))

     
# encoded_headers_bytes = bytes(encoded_headers)

# print(encoded_headers_bytes.hex())



dump='80000000ff82418a089d5c0b8170dc780f3787845887a47e561cc5801f40874148b1275ad1ffb8fe711cf350552f4f61e92ff3f7de0fe42c87f9fa53f9bd3d87a4d6d3fcfdf783f90b21fe7e94fe749d3142a5db07549fcfdf783f9135fcff408b4148b1275ad1ad49e33505023f30408d4148b1275ad1ad5d034ca7b29f88fe791aa90fe11fcf4092b6b9ac1c8558d520a4b6c2ad617b5a54251f01317ad5d07f66a281b0dae053fae46aa43f8429a77a8102e0fb5391aa71afb53cb8d7f6a435d74179163cc64b0db2eaecb8a7f59b1efd19fe94a0dd4aa62293a9ffb52f4f61e92b01642b81702e05370e51d8661b65d5d97353e5497ca589d34d1f43aeba0c41a4c7a98f33a69a3fdf9a68fa1d75d0620d263d4c79a68fbed00177fe8d48e62b03ee697e8d48e62b1e0b1d7f46a4731581d754df5f2c7cfdf6800bbdf43aeba0c41a4c7a9841a6a8b22c5f249c754c5fbef046cfdf6800bbbf408a4148b4a549275906497f83a8f517408a4148b4a549275a93c85f86a87dcd30d25f408a4148b4a549275ad416cf023f31408a4148b4a549275a42a13f8690e4b692d49f50929bd9abfa5242cb40d25fa523b3e94f684c9f51952d4b62bbf45a96e1bbefb4005dffa2d5f7da002ef74086aec31ec327d785b6007d286f'
# 8a di 1000 1010  ya3ni 10 bytes be huffman mashy
encoded_header=bytes.fromhex(dump)

#decoder=hpack.Decoder()
#decoder.header_table_size=0

headers=decode_hpack(encoded_header[5:])

for header in headers:
    print(header)