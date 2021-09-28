import socket as sk

# def exit_gracefully(sig, stackframe):
#     print("Exited gracefully", end=".")
#     serverSocket.close()
#     sys.exit(0) # exit with grace
    
# signal.signal(signal.SIGINT, exit_gracefully)

port = 5500
ip = '0.0.0.0' # localhost/loopback address

# Create the server socket
serverSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

# Binds the server to localserver port 5500
serverSocket.bind((ip, port))

# Specifies how many TCP connection can be queued until it refuses connection
serverSocket.listen(3)

if __name__ == "__main__":
    # Since this is a server we would want to run it forever until we shut it down
    while(True):
        connection, addr = serverSocket.accept() # blocks until a connection comes
        print("Connection established\n", flush=True)
        
        # Get the request and print it
        request = connection.recv(1024).decode()
        
        splitted = request.split('\r\n')
        
        action_line = splitted[0].split(' ')
        file_requested = action_line[1].strip('/') # Strip away the slash
        
        try:
            # Look for the file in the local directory
            header = "HTTP/1.1 200 Ok\r\n"
            
            with open(file_requested, 'rb') as f:
                response = f.read()
            
            if file_requested.endswith('.css'):
                mime_type = "text/css"
            elif file_requested.endswith('.jpg'):
                mime_type = "image/jpg"
            elif file_requested.endswith('html'):
                mime_type = "text/html"
            elif file_requested.endswith('js'):
                mime_type = "text/jss"
            
            header += f"Content-type: {mime_type} \r\n\r\n"
                
                        
        except:
            print("File not found")
            # File requested doesn't exist sent 404 response
            header = "HTTP/1.1 404 Not Found\r\n\n"            
            
            response = "<html> \
                <head><meta charset='UTF-8'></head> \
                <body><h3>404 File Not Found</h3></body></html>".encode('utf-8')
            
        
        final_response = header.encode('utf-8') + response
        connection.send(final_response)
        
        # Then close off the connection to accept a new one
        print("Closing connection")
        connection.close()
