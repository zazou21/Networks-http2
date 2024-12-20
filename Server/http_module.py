class HttpRequest:
    def __init__(self,request):
        self.method=None
        self.path = None
        self.headers = {}
        self.body = None
        self.parse(request)

    def parse(self,request):
        lines = request.split("\r\n")
        # Parse method and path from request line (e.g., "POST / HTTP/1.1")
        self.method, self.path, _ = lines[0].split(" ")
        
        # Parse headers
        header_lines = lines[1:]
        for line in header_lines:
           if line.strip() == "": 
                break
           if ":" in line:  # Ensure the line contains a colon
                key, value = line.split(":", 1)
                self.headers[key.strip()] = value.strip()

        # Extract body if POST request
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            self.body = lines[-1][:content_length]  # Body follows the headers


class HttpResponse: 
    def __init__(self, status_code, status_message):
        self.status_code = status_code
        self.status_message = status_message
        self.headers = {}
        self.body = ""
 
    def add_header(self, name, value):
        self.headers[name] = value

    def set_body(self, body):
        self.body = body
        self.add_header("Content-Length", str(len(self.body)))

    def format(self):
        
        response_line = f"HTTP/1.1 {self.status_code} {self.status_message}\r\n"
        
       
        headers = "".join(f"{key}: {value}\r\n" for key, value in self.headers.items())
        
       
        return response_line + headers + "\r\n" + self.body
    



        