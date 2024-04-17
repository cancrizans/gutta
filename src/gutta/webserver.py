import http.server
import socketserver


def run_webserver():
    PORT = 8069
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(('0.0.0.0', PORT), Handler)
    try:
        
        httpd.serve_forever(poll_interval=0.5)

    except KeyboardInterrupt:
        pass
    return