import socket as sk 
import os 

port = 5505 # Port 5505 for proxy server 
ip = '127.0.0.1' # Localhost

# Create our proxy server socket
proxySocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

# Reuse the port, might not work on Windows
# proxySocket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEPORT, 1)

# Bind our socket to the ip and port 
proxySocket.bind((ip, port))

# Make it into listen mode with backlog queue size of 3
proxySocket.listen(1)

cache_it = True

print("Proxy server is up and running")

if __name__ == "__main__":
    while True:
        connection, addr = proxySocket.accept() # Block until connection is accepted
        print("Connection established")
        
        host = "" # Used for storing the host url that will be used for resolving the IP address
        
        # Receiving the request from the client
        request = connection.recv(1024).decode()
        print(request)
        
        # This boolean is used for to check if the request has a referer
        # which will be the host if it is found
        found_referer = False
        
        # First step figure out who the hell is the host
        splitted = request.split('\r\n') # split by \r\n
        
        for line in splitted:
            if "Referer: " in line:
                # Referer is found in the client request, geti t
                # and then break out of this for loop
                port_index = line.find(f":{port}")
                host = line[port_index + 6:]
                host = host.replace("http://", "")
                
                first_slash = host.find('/')
                
                if first_slash != -1:
                    host = host[:first_slash]
                
                found_referer = True # Set found_referer boolean to be true
                print(host + " is the host")
                break
                
        
        # Parse the request, taking away the first slash, and http or https
        parsed_line = request.split('\r\n')[0]
        parsed_line = parsed_line.split(' ')[1]
        parsed_line = parsed_line[1:]
        parsed_line = parsed_line.replace("https://", "")
        parsed_line = parsed_line.replace("http://", "")
        
        
        try:
            # Open the file to see if it already exists in cache
            # it will only fetch the html since that's the only thing I'm caching
            cached_file = open(f"{os.getcwd()}/cache/{parsed_line.replace('/', '^')}.html", 'rb')
            print("Cache hit if we reached here")
        
            # Read the cached response
            cache_response = cached_file.read()
            
            # Send the response to the client     
            connection.sendall(cache_response)
            print("Sent response to client and ending the server")
            connection.close()
            
            # I have to stop the server after it serves the cached html file
            # or else it will request other files such as favicon which will cause it to crash
            break
        except FileNotFoundError:
            # Here that means the file is not found in cache hence we
            # must retrieve it from the server
            print("File not found in cache hence retrieve from server")
            
            # No referer which means we have to manually find the host from the request
            if not found_referer:
                # find the first slash
                first_slash = parsed_line.find('/')
                if first_slash == -1:
                    first_slash = len(parsed_line)
                
                # Get us the host if there is no referer
                host = parsed_line[:first_slash]
                
                cache_it = True
                
            # Second find the resource to locate
            first_slash = parsed_line.find('/')
            
            
            # If referer is found it means the resource to locate is just parsed line  
            if found_referer:
                resource_to_locate = '/' + parsed_line      
            # no referer then we have to check whether it is requesting a sub directory or root directory
            elif first_slash == -1 and parsed_line == host:
                resource_to_locate = '/'
            else:
                # incldue the slash
                resource_to_locate = parsed_line[first_slash:] 
            
            # Make the socket that connects to the web server
            proxy_server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            proxy_server_socket.settimeout(4)
            
            try:
                # Try the connection
                proxy_server_socket.connect((host, 80))
                
                header = f"GET {resource_to_locate} HTTP/1.1\r\nHost: {host}\r\n\r\n"
                print(header)
                
                # only store the host's html and nothing else!
                if cache_it:
                    # cache the file here, open up a new file if it doesn't exist
                    cache_file = open(f"{os.getcwd()}/cache/{parsed_line.replace('/', '^')}.html", 'wb+')
                
                # Sent the GET response to the web server
                proxy_server_socket.sendall(header.encode())
                
                while True:
                    data = proxy_server_socket.recv(1024)
                    if cache_it:
                        cache_file.write(data)
                    # Sent data to the client
                    connection.sendall(data)
            except UnicodeDecodeError:
                print("Cannot decode some characters")
            except sk.gaierror:
                print(f"Cannot connect to host {host}")
            except sk.timeout:
                print("Timed out/Finished fetching resources")    
                
            # Finished sending we will be closing our connections to the connection
            # to the server socket
            # as well as the cache file if we opened it 
            print("Closing connection")
            if cache_it:
                cache_file.close()
                cache_it = False
            connection.close()
            proxy_server_socket.close()