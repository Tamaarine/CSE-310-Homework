## Note: Please TA if you are running the server please make sure your current working directory is the root folder, i.e. ~/lu-ricky-assignment1 after you have unzipped the zip file and cd into it

## Note: Also please use Google Chrome as I found out that Firefox sent some random request to the web server even if you just start typing 'localhost:5505', but Google Chrome doesn't
## Additionally please use a Guest Profile since it won't have any cache when you are testing for Part A, and another new Guest Profile when you are testing for Part B. This will give you a new browser session with no cache stored whatsoever.
## I have included the jpg called guest.jpg for how you can find Guest Profile

# Thank you so much for your time for reading it!

# Libraries used
The only two library that I have used for this assignment is socket and os,
socket is used for majority of the assignment. os is only used for getting the current working directory for accessing
and storing the cache, that's it

# Instructions on how to run web server (Part A)
1. Open a Guest Profile session
2. On windows do python webserver.py and this will open up the server if you are on linux do python3 webserver.py
3. It should say 'Server is up and running' after you run the code
4. Now you can go ahead and request the local file HelloWorld.html from port 5500 by typing 'localhost:5500/HelloWorld.html' in your browser
5. It should retrieve a webpage that has some default text, 2 images, and some css stylings
6. If you open up developer tools and refresh the page you should be able to observe that the request gives 200 status code
7. If you went ahead to retrieve a file that is not on the local disk, such as 'localhost:5500/DontExist.html' this should give you a 404 error response
8. Press ctrl + c when you are done running the server


# Instructions on how to run web proxy (Part B)
1. On windows do python proxyserver.py and this will open up the server if you are on linux do python3 proxyserver.py
2. It should say 'Proxy server is up and running' after you run the code
3. Now you can go ahead and make a request for the proxy server, for example 'localhost:5505/http://www.cs.toronto.edu/~ylzhang/'
4. Since initially the cache folder is empty, it will attempt to fetch it from the web server and then relay the response 
back to the client
5. To test the cache file, please close the current Guest Profile Session, and start a new one and then revisit 
'localhost:5505/http://www.cs.toronto.edu/~ylzhang/', the message from the program should say, 'Cache hit' and you should 
immediately see the web page in your browser and the server should end. I designed it this way after it sent the html to end the server
immediately or else it will sent other junk requests from the client
6. The reason why you need to close the current Guest Profile Session is because the browser itself will cache the response for you
so if we just use the browser cache it is not really testing the cache that I kept, that's why you need to close the Guest Profile Session
and start a new one so there won't be any browser cache but rather uses the cache that I stored
7. Below are some of the sites that I have tested, please be gentle :(
8. You have to restart the proxy server again if you have fetched a cached response from the server!
9. For some odd reason Chrome on windows will sent make another connection to the server after it has fetch the response
please just ctrl + c it because it is a request with no headers at all. Thank you!
10. I just don't undertand why Windows works so differently, please let me know if you want me to do a demonstration, because
I program it from linux and it works perfectly fine there, but as soon as I come to test on Windows it is completely different

-P.S. I really appreciate your time! Thank you!!!

Sites that works for proxy server (That I have tested)
localhost:5505/
1. http://www.cs.toronto.edu/~ylzhang/
2. http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file1.html
3. http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file2.html
4. http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file3.html
5. http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file4.html
6. www.neverssl.com
7. tamarine.tech (My website, but when revisit using cache it will be 301 permanently moved because my site has HTTPS)
8. www3.cs.stonybrook.edu/~skiena/373/ (Same thing, it will be 301 permanetly moved but might redirect you)
9. www.google.com
10. http://www.google.com