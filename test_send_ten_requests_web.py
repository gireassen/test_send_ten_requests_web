import http.server
import socketserver
import json
from urllib.parse import urlparse, urlencode
import http.client
import sys

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('''
            <form method="post" action="/send">
                <label for="target_url">Target URL:</label>
                <input type="text" id="target_url" name="target_url" required>
                <button type="submit">Send Requests</button>
            </form>
        ''', 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        if post_data:
            target_url = self.get_query_param('target_url')
            if target_url:
                send_requests(target_url)
                self.send_response(303)
                self.send_header('Location', '/result')
                self.end_headers()
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes('Invalid request.', 'utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Empty request.', 'utf-8'))

    def get_query_param(self, param):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_params = urlparse(post_data.decode())
        query_params = parsed_params.query.split('&')
        for param_pair in query_params:
            key, value = param_pair.split('=')
            if key == param:
                return value
        return None

def send_requests(target_url):
    for i in range(10):
        conn = http.client.HTTPConnection(urlparse(target_url).netloc)
        conn.request('POST', urlparse(target_url).path)
        response = conn.getresponse()
        print(response.read().decode())
        conn.close()

if __name__ == '__main__':
    server = socketserver.TCPServer(('', 8000), WebhookHandler)
    print('Server started. Listening on port 8000...')
    server.serve_forever()  