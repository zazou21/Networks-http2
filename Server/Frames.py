
HTTP2_PREFACE = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'


FRAME_TYPES = {
    0x0: "DATA",
    0x1: "HEADERS",
    0x2: "PRIORITY",
    0x3: "RST_STREAM",
    0x4: "SETTINGS",
    0x5: "PUSH_PROMISE",
    0x6: "PING",
    0x7: "GOAWAY",
    0x8: "WINDOW_UPDATE",
    0x9: "CONTINUATION"
}

class Frame:
    def __init__(self, frame_type, length, flags, stream_id, payload):
        self.frame_type = frame_type  # Frame type 
        self.length = length  # Length of the payload
        self.flags = flags  # Flags associated with the frame
        self.stream_id = stream_id  # Stream ID
        self.payload = payload 

    def __repr__(self):
        return (f"Frame(type={self.frame_type}, length={self.length}, "
                f"flags={self.flags}, stream_id={self.stream_id}, "
                f"payload={self.payload.hex()})")


def parse_http2_frame(data):


    # HTTP/2 frame header: 3 bytes length, 1 byte type, 1 byte flags, 4 bytes stream_id
    if len(data) < 9:
        return None, data 

    # Frame header
    length = int.from_bytes(data[:3], 'big')  # 3 bytes for length
    frame_type = data[3]  # 1 byte for frame type
    flags = data[4]  # 1 byte for flags
    stream_id = int.from_bytes(data[5:9], 'big')  # 4 bytes for stream ID

    
    payload = data[9:9 + length]

   
    frame = Frame(get_frame_type_name(frame_type), length, flags, stream_id, payload)

    
    return frame, data[9 + length:] 

def parse_all_http2_frames(data):
    if data.startswith(HTTP2_PREFACE):
        print("Skipping HTTP/2 preface...")
        data = data[len(HTTP2_PREFACE):]  
    frames = []
    while data:
        frame, data = parse_http2_frame(data)
        if frame:
            frames.append(frame)
        else:
            break  
    return frames


def get_frame_type_name(frame_type):
    """Returns the name of the frame type."""
    return FRAME_TYPES.get(frame_type, "Unknown")