"""Implementing HPACK compression to be able to decode and encode requests and responses"""

"""static_table"""


""""prefixes"""

"""Check for entry in dynamic or static table"""

# 1 INDEXED HEADER FIELD


"""This adds a new header to the dynamic table"""


# 01 LITERAL HEADER FIELD WITH INDEXING


# 0000 LITERAL HEADER FIELD WITHOUT INDEXING

from bitarray import bitarray

import re

from collections import deque


huffman_dict = {
    "0": bitarray("00000"),
    "1": bitarray("00001"),
    "2": bitarray("00010"),
    "3": bitarray("011001"),
    "4": bitarray("011010"),
    "5": bitarray("011011"),
    "6": bitarray("011100"),
    "7": bitarray("011101"),
    "8": bitarray("011110"),
    "9": bitarray("011111"),
    ":": bitarray("1011100"),
    ".": bitarray("010111"),
    "A": bitarray("100001"),
    "B": bitarray("1011101"),
    "C": bitarray("1011110"),
    "D": bitarray("1011111"),
    "E": bitarray("1100000"),
    "F": bitarray("1100001"),
    "G": bitarray("1100010"),
    "H": bitarray("1100011"),
    "I": bitarray("1100100"),
    "J": bitarray("1100101"),
    "K": bitarray("1100110"),
    "L": bitarray("1100111"),
    "M": bitarray("1101000"),
    "N": bitarray("1101001"),
    "O": bitarray("1101010"),
    "P": bitarray("1101011"),
    "Q": bitarray("1101100"),
    "R": bitarray("1101101"),
    "S": bitarray("1101110"),
    "T": bitarray("1101111"),
    "U": bitarray("1110000"),
    "V": bitarray("1110001"),
    "W": bitarray("1110010"),
    "X": bitarray("11111100"),
    "Y": bitarray("1110011"),
    "Z": bitarray("11111101"),
    "[": bitarray("11111111") + bitarray("11011"),
    "\\": bitarray("11111111") + bitarray("11111110") + bitarray("000"),
    "]": bitarray("11111111") + bitarray("11100"),
    "^": bitarray("11111111") + bitarray("111100"),
    "_": bitarray("100010"),
    "a": bitarray("00011"),
    "b": bitarray("100011"),
    "c": bitarray("00100"),
    "d": bitarray("100100"),
    "e": bitarray("00101"),
    "f": bitarray("100101"),
    "g": bitarray("100110"),
    "h": bitarray("100111"),
    "i": bitarray("00110"),
    "j": bitarray("1110100"),
    "k": bitarray("1110101"),
    "l": bitarray("101000"),
    "m": bitarray("101001"),
    "n": bitarray("101010"),
    "o": bitarray("00111"),
    "p": bitarray("101011"),
    "q": bitarray("1110110"),
    "r": bitarray("101100"),
    "s": bitarray("01000"),
    "t": bitarray("01001"),
    "u": bitarray("101101"),
    "v": bitarray("1110111"),
    "w": bitarray("1111000"),
    "x": bitarray("1111001"),
    "y": bitarray("1111010"),
    "z": bitarray("1111011"),
    "-": bitarray("010110"),
    " ": bitarray("010100"),
    "!": bitarray("11111110") + bitarray("00"),
    '"': bitarray("11111110") + bitarray("01"),
    "#": bitarray("11111111") + bitarray("1010"),
    "$": bitarray("11111111") + bitarray("11001"),
    "%": bitarray("010101"),
    "&": bitarray("11111000"),
    "'": bitarray("11111111") + bitarray("010"),
    "(": bitarray("11111110") + bitarray("10"),
    ")": bitarray("11111110") + bitarray("11"),
    "*": bitarray("11111001"),
    "+": bitarray("11111111") + bitarray("011"),
    ",": bitarray("11111010"),
    "/": bitarray("011000"),
    ";": bitarray("11111011"),
    "<": bitarray("11111111") + bitarray("1111100"),
    "=": bitarray("100000"),
    ">": bitarray("11111111") + bitarray("1011"),
    "?": bitarray("11111111") + bitarray("00"),
    "@": bitarray("11111111") + bitarray("11010"),
}


# HPACK Static Table
hpack_static_table = [
    (":authority", ""),  # 1
    (":method", "GET"),  # 2
    (":method", "POST"),  # 3
    (":path", "/"),  # 4
    (":path", "/index.html"),  # 5
    (":scheme", "http"),  # 6
    (":scheme", "https"),  # 7
    (":status", "200"),  # 8
    (":status", "204"),  # 9
    (":status", "206"),  # 10
    (":status", "304"),  # 11
    (":status", "400"),  # 12
    (":status", "404"),  # 13
    (":status", "500"),  # 14
    ("accept-charset", ""),  # 15
    ("accept-encoding", "gzip, deflate"),  # 16
    ("accept-language", ""),  # 17
    ("accept-ranges", ""),  # 18
    ("accept", ""),  # 19
    ("access-control-allow-origin", ""),  # 20
    ("age", ""),  # 21
    ("allow", ""),  # 22
    ("authorization", ""),  # 23
    ("cache-control", ""),  # 24
    ("content-disposition", ""),  # 25
    ("content-encoding", ""),  # 26
    ("content-language", ""),  # 27
    ("content-length", ""),  # 28
    ("content-location", ""),  # 29
    ("content-range", ""),  # 30
    ("content-type", ""),  # 31
    ("cookie", ""),  # 32
    ("date", ""),  # 33
    ("etag", ""),  # 34
    ("expect", ""),  # 35
    ("expires", ""),  # 36
    ("from", ""),  # 37
    ("host", ""),  # 38
    ("if-match", ""),  # 39
    ("if-modified-since", ""),  # 40
    ("if-none-match", ""),  # 41
    ("if-range", ""),  # 42
    ("if-unmodified-since", ""),  # 43
    ("last-modified", ""),  # 44
    ("link", ""),  # 45
    ("location", ""),  # 46
    ("max-forwards", ""),  # 47
    ("proxy-authenticate", ""),  # 48
    ("proxy-authorization", ""),  # 49
    ("range", ""),  # 50
    ("referer", ""),  # 51
    ("refresh", ""),  # 52
    ("retry-after", ""),  # 53
    ("server", ""),  # 54
    ("set-cookie", ""),  # 55
    ("strict-transport-security", ""),  # 56
    ("transfer-encoding", ""),  # 57
    ("user-agent", ""),  # 58
    ("vary", ""),  # 59
    ("via", ""),  # 60
    ("www-authenticate", ""),  # 61
]


class DynamicTable:
    def __init__(self, max_size=4096):
        self.table = deque()  # Using deque for fast appends and pops
        self.max_size = max_size

    def get_table(self):

        return list(self.table)

    def add_entry(self, name, value):

        entry = (name, value)

        entry_size = len(name) + len(value) + 32

        while entry_size > self.max_size and len(self.table) > 0:
            evicted_entry = self.table.popleft()
            evicted_size = len(evicted_entry[0]) + len(evicted_entry[1]) + 32
            self.max_size += evicted_size

        self.table.append(entry)


def decode_huffman(huffman_encoded):

    decoded_string = ""

    # Convert bytes to bitarray
    bitstream = bitarray()
    bitstream.frombytes(huffman_encoded)
    print(f"number of bits {len(bitstream)}")
    position = 0

    try:

        decoded_string = "".join(bitstream.decode(huffman_dict))

    except ValueError as e:
        match = re.search(r"at position (\d+)", str(e))
        if match:
            position = int(match.group(1))
        decoded_string = "".join(bitstream[:position].decode(huffman_dict))

        return decoded_string

    return decoded_string


def get_bits_from_bytes(byte_data):
    """Convert bytes into a list of bits."""
    bits = []
    for byte in byte_data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)  # Extract each bit, from MSB to LSB
    return bits


def get_prefix(encoded_block, prefix_size=3):
    mask = (1 << prefix_size) - 1
    first_byte = encoded_block[0]
    prefix = first_byte & mask
    return prefix


def decode_integer_hpack(payload, start_index=0):
    """Decode an integer from the HPACK format (RFC 7541)."""

    byte = payload[start_index]
    if byte & 0x80 == 0:
        value = byte
        length = 1
    else:

        value = byte & 0x7F
        length = 1
        while payload[start_index + length] & 0x80 != 0:
            value = (value << 7) | (payload[start_index + length] & 0x7F)
            length += 1
        value = (value << 7) | (payload[start_index + length - 1] & 0x7F)

    return value, length


def decode_string_literal_hpack(payload, start_index, length):

    name = payload[start_index : start_index + length].decode("utf-8", errors="ignore")

    return name


def decode_hpack(payload):
    """Simple HPACK decoder for indexed and literal headers."""
    headers = []
    i = 0
    try:
        while i < len(payload):
            byte = payload[i]

            if byte & 0x80:  # Indexed header field (1xxxxxxx)
                index = byte & 0x7F
                if 1 <= index <= len(hpack_static_table):
                    headers.append(hpack_static_table[index - 1])
                else:
                    pass
                i += 1

            elif byte & 0x40:  # Literal header field with incremental indexing
                # 01xxxxxx
                index = byte & 0x3F
                if 1 <= index <= len(hpack_static_table):
                    name = hpack_static_table[index - 1][0]

                    # value_length=decode_integer_hpack(payload,i+1)

                    value_length = payload[i + 1] & 0x7F

                    if payload[i + 1] & 0x7F:

                        huffman_encoded = payload[i + 2 : i + 2 + value_length]

                        value = decode_huffman(huffman_encoded)

                    else:
                        value = decode_string_literal_hpack(
                            payload, i + 2, value_length
                        )

                    headers.append((name, value))

                    i += 2 + value_length

                else:

                    name_length = payload[i + 1] & 0x7F
                    if payload[i + 1] & 0x80:  # Check if the name is Huffman encoded
                        huffman_encoded_name = payload[i + 2 : i + 2 + name_length]
                        name = decode_huffman(huffman_encoded_name)
                    else:
                        name = decode_string_literal_hpack(payload, i + 2, name_length)

                    i += 2 + name_length

                    # Value length and Huffman check for value decoding
                    value_length = payload[i] & 0x7F

                    if payload[i] & 0x7F:
                        huffman_encoded = payload[i + 1 : i + 1 + value_length]
                        value = decode_huffman(huffman_encoded)
                    else:
                        value = decode_string_literal_hpack(
                            payload, i + 1, value_length
                        )

                    i += 1 + value_length

                    headers.append((name, value))

            elif (byte & 0xF0) == 0 or (
                byte & 0x10
            ):  # Literal header field without incremental indexing
                index = byte & 0x0F
                if 1 <= index <= len(hpack_static_table):
                    name = hpack_static_table[index - 1][0]

                    # value_length=decode_integer_hpack(payload,i+1)
                    value_length = payload[i + 1] & 0x7F

                    if payload[i + 1] & 0x80:
                        huffman_encoded = payload[i + 2 : i + 2 + value_length]
                        value = decode_huffman(huffman_encoded)
                    else:
                        value = decode_string_literal_hpack(
                            payload, i + 2, value_length
                        )

                    name = name[0] if name is isinstance(name, tuple) else name

                    headers.append((name, value))

                    i += 2 + value_length

                else:
                    # name_length=decode_integer_hpack(payload,i+1)
                    name_length = payload[i + 1] & 0x7F

                    if payload[i] & 0x7F:
                        huffman_encoded = payload[i + 2 : i + 2 + name_length]
                        name = decode_huffman(huffman_encoded)
                    else:
                        name = decode_string_literal_hpack(payload, i + 2, value_length)

                    i += 2 + name_length

                    value_length = payload[i] & 0x7F

                    if payload[i] & 0x80:
                        huffman_encoded = payload[i + 1 : i + 1 + value_length]
                        value = decode_huffman(huffman_encoded)
                    else:
                        value = decode_string_literal_hpack(
                            payload, i + 1, value_length
                        )

                    i += 1 + value_length

                    headers.append((name, value))

        return headers
    except:
        return headers


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


def encode_string(value, flag):
    huffman = 0x80 if flag else 0x00
    encoded_string = value.encode("utf-8")
    length = encode_integer(len(encoded_string), 7)
    return encoded_string


def encode_header(name, value, dynamic_table, add_to_dynamic_table_flag=True):
    # Case 1: If both name and value exist in the static table
    for idx, (static_name, static_value) in enumerate(hpack_static_table):
        if name == static_name and value == static_value:
            encoded_integer = encode_integer(idx + 1, 7)  # Indexed header
            return bytes([encoded_integer[0] | 0x80]) + bytes(encoded_integer[1:])

    # Case 2: If name and value exist in the dynamic table (indexed header)
    for idx, (dynamic_name, dynamic_value) in enumerate(dynamic_table.get_table()):
        if name == dynamic_name and value == dynamic_value:
            encoded_integer = encode_integer(
                idx + 62, 7
            )  # Indexed header in dynamic table
            return bytes([encoded_integer[0] | 0x80]) + bytes(encoded_integer[1:])

    # Case 3: If only the name exists in the static table, encode the name and value literally
    for idx, (static_name, static_value) in enumerate(hpack_static_table):
        if name == static_name:

            encoded_name_index = encode_integer(idx + 1, 6)
            encoded_name_index = bytearray(encoded_name_index)
            encoded_name_index[0] |= 0x40

            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value, False)  # Encode value literally

            if add_to_dynamic_table_flag:
                dynamic_table.add_entry(name, value)  # Add to dynamic table

            return (
                bytes(encoded_name_index) + bytes(value_length) + bytes(encoded_value)
            )

    # Case 4: If only the name exists in the dynamic table, encode the name using index and value literally
    for idx, (dynamic_name, dynamic_value) in enumerate(dynamic_table.get_table()):
        if name == dynamic_name:

            encoded_name_index = encode_integer(
                idx + 62, 6
            )  # Indexed name in dynamic table

            value_length = encode_integer(len(value), 7)
            encoded_value = encode_string(value)
            if add_to_dynamic_table_flag:
                dynamic_table.add_entry(name, value)  # Add to dynamic table
            return (
                bytes(encoded_name_index) + bytes(value_length) + bytes(encoded_value)
            )

    # Case 5: If neither the name nor value exists in the static or dynamic table, encode both literally
    # Encode name and value literally
    encoded_name = encode_string(name)
    encoded_value = encode_string(value)
    name_length_encoding = encode_integer(len(name), 7)  # Length of name
    value_length_encoding = encode_integer(len(value), 7)  # Length of value

    if add_to_dynamic_table_flag:
        dynamic_table.add_entry(name, value)  # Add to dynamic table

    return (
        bytes(name_length_encoding)
        + bytes(value_length_encoding)
        + bytes(encoded_name)
        + bytes(encoded_value)
    )
