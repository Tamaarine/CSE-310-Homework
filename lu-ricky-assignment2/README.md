# Library used
1. dpkt, need to be installed
2. socket
3. sys
4. collections


# Running the program
```
For Linux
python3 analysis_pcap_tcp.py assignment2.pcap > output.txt

For Window
python analysis_pcap_tcp.py assignment2.pcap > output.txt
```
This will run the analysis and store the output into a text file called output.txt

Please make sure that you are in the root folder and running it, because I use command line arguments.


# Part A
a. This basically required me to find the 3 unique tuple that goes from the sender, which has 3 ports numbers (43498, 43500, 43502) to the receiver which is always 80, because it is the web server port number. I just iterate through each of the packets in the pcap file and just find the 3 unique 4-tuple that goes from sender to receiver, only add it to my list if I haven't collected it yet.

b. In order to find the first two transaction of each TCP flow, I had to skip the 3 way handshake for each of them. I did it through a list of 3 counters, each for the TCP flow to skip 3 packets which represents the 3 way handshake. After the 3 way handshake I can collect the first 2 back and forth packet from sender -> receiver and receiver -> sender, because those two together make up **ONE** transaction. I also had to find the window scale which can be found in the TCP options, and raise 2 to the scale number in order to find the correct window size, which should be 49,152 for all 6 transactions.

c. For the throughput, I had to collect the total payload length that was sent for each TCP flow and also the period of the communication. The period can be simply calculated as the difference in time between the first packet was sent by the sender after the 3 way handshake, and the last packet that was sent by the receiver, which is flagged with the FIN flag in the TCP flags. Then the payload length can be summed for each TCP flow by summing up the length of the TCP packet. Lastly, a simple subtraction and division will yield the throughput by dividing the total payload length by the period.

# Part B
1. In order to estimate the congestion window we must find the round trip time, RTT, first. RTT can be found by subtracting the time of the first ACK sent by the sender by the time of the first ACK sent by the receiver. We will be using this RTT for all of the TCP flow. To find the first three congestion window we can just find the number of packets that were sent in each RTT interval. For example, the first congestion window is the number of packets sent between [0, RTT), second congestion window is [RTT, 2 * RTT), and the third congestion window is [2 * RTT, 3 * RTT). 
2. To get the total retransmission count we have to distinguish between either a fast-retransmission (retransmission due to triple duplicate ACK) or just due to timeout. For triple duplicate ACK I went through all of the packets that were sent from the receiver to the sender for each TCP flow and took a count of the ACK number. This will allow me to find any triple duplicate ACK just by checking which ACK number was sent from the receiver more than 3 times, which indicates a triple duplicate ACK. I then also went through all of the SEQ number that was sent from the sender to check which packet was sent multiple times. By taking a intersection of the triple duplicate ACK list and the retransmitted packets from sender it will tell us which sequence packet was sent using a triple duplicate ACK. Now we have a list of packets that was retransmitted due to triple duplicate ACK. However, the list may also contain packet that was retransmitted due to out of order, so to tell the difference of whether or not the packet was retransmitted due to being out of order or triple duplicate ACK, I labeled each packet from each TCP flow in an incremental manner, i.e. 1, 2, 3, ... and so on. This will allow me to determine whether or not a packet is before or after another rather than looking at the timestamp which can be bothersome. To find the out of order packet, I find the labeled time where we have the first duplicate ACK then I just have to search through the packets that was sent by the sender to see if it had a retransmitted packet whose time is before the the duplicate ACK. If it is before then we know that the packet is sent out of order, if it is after then it is retransmitted due to triple duplicate ACK. In the end, by taking away packets that were sent by out of order in the intersection we will have packets that were retransmitted due to triple duplicate ACK. To find timeout retranmission we just have to take away the number of fast-retranmission from the total number of retransmission. 