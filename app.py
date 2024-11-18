# app.py

def app(environ, start_response):
    # The response headers
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    
    # The body of the response (Hello World)
    return [b"Hello, World!"]
