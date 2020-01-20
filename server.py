#  coding: utf-8 
import socketserver
from http import HTTPStatus
import os.path
import fnmatch
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/



# Copyright 2020 Xuechun Hou

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

class MyWebServer(socketserver.BaseRequestHandler):
    
    def setup(self):
        self.base_dir = "./www"
        self.the_only_method = "GET"
        
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # parse request header 
        request_method, request_url, self.http_version = self.parse()
        # verify request method
        if ( not self.is_valid_request_method(request_method)):
            # request method not GET, send 405
            method_not_allowed_status_code = self.http_version + " " + str(HTTPStatus.METHOD_NOT_ALLOWED.value) + " " + HTTPStatus.METHOD_NOT_ALLOWED.phrase
            content_length_header = "Content-Length: 0"
            content_type = "Content-Type: text/plain"
            response_array = [method_not_allowed_status_code, content_type, content_length_header]
            method_not_allowed_response = "\r\n".join(response_array) + "\r\n\r\n"
            
            self.request.sendall(bytearray(method_not_allowed_response,'utf-8'))
            return
            
        # verify if file path valid 
        file_path = self.base_dir + request_url
        if (not self.is_valid_file_path(file_path)):
            # path not valid; either DNE, or exist outside of www directory, send 404
            not_found_status_code = self.http_version + " " + str(HTTPStatus.NOT_FOUND.value) + " " + HTTPStatus.NOT_FOUND.phrase
            content_length_header = "Content-Length: 0"
            content_type = "Content-Type: text/plain"
            response_array = [not_found_status_code, content_type, content_length_header]
            not_found_response = "\r\n".join(response_array) + "\r\n\r\n"
            
            self.request.sendall(bytearray(not_found_response,'utf-8'))
            return

        # if it's requesting a file
        if (os.path.isfile(file_path)):
            self.send_file(file_path)
        # request for a directory 
        else:
            # either send index.html or redirect url 301 
           
            self.handle_directory_request(request_url)
    



    def handle_directory_request(self, directory_path):
        has_end = directory_path[-1] == '/'
        
        if (has_end):
            
            self.send_file(self.base_dir + directory_path + "index.html")
        else:
            # needs a url redirection 
            self.send_redirect_response(directory_path)

    
    
    
    
    def send_redirect_response(self, directory_path):
        
        moved_permanently_status_code = self.http_version + " " + str(HTTPStatus.MOVED_PERMANENTLY.value) + " " + HTTPStatus.MOVED_PERMANENTLY.phrase 
        location = "Location: " + "http://" + self.server.server_address[0] +  ":" + str(self.server.server_address[1]) + directory_path + "/"
        content_length_header = "Content-Length: 0"
        content_type = "Content-Type: text/plain"
        response_array = [moved_permanently_status_code, content_type, content_length_header, location]
        moved_permanently_response = "\r\n".join(response_array) + "\r\n\r\n"
        
        self.request.sendall(bytearray(moved_permanently_response,'utf-8'))

    
    def send_file(self, file_path):
        content_type = ""
        if fnmatch.fnmatch(file_path, "*.html"):
            content_type = "Content-Type: text/html"
        elif fnmatch.fnmatch(file_path, "*.css"):
            content_type = "Content-Type: text/css"
        # read file 
        file_content = open(file_path, "r").read()
        content_length_header = "Content-Length: {}".format(len(file_content))
        ok_response = self.http_version + " " + str(HTTPStatus.OK.value) + " " + HTTPStatus.OK.phrase
        
        # send response 
        response_array = [ok_response, content_type, content_length_header, "Connection: Closed", "", file_content]
        response = "\r\n".join(response_array)
        response += "\r\n"
        
        self.request.sendall(bytearray(response,'utf-8'))
        


    def is_valid_request_method(self, request_method):
        return request_method.upper() == self.the_only_method
    
    def is_valid_file_path(self, file_path):
        if not os.path.exists(file_path): return False
        if os.path.samefile(self.base_dir, file_path): return True
        
        for root, dirs, files in os.walk(self.base_dir, topdown=True):
            for name in files:
                
                if (os.path.samefile(os.path.join(root, name), file_path)): return True
            for name in dirs:
                
                if (os.path.samefile(os.path.join(root, name), file_path)): return True
        return False
        
    def parse(self):
        self.data = self.data.decode("utf-8");

        return self.data.split("\r\n")[0].split(" ")
        




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
