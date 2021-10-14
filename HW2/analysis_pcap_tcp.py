import dpkt  as dp
import socket as sk
import sys
from collections import Counter

from dpkt.tcp import tcp_flags_to_str

# PART A
def flow_identification(filename):
    f = open(filename, "rb")
    
    tcp_flows = [] # a tuple of 4, that consists of the sport, sip, dport, dip. Only three of them exists for this problem
    for _, buf in dp.pcap.Reader(f):
        eth = dp.ethernet.Ethernet(buf)
        
        ip = eth.data
        tcp = ip.data
        
        # Get the source port, source ip, destination port, destional ip
        sip = sk.inet_ntoa(ip.src)
        dip = sk.inet_ntoa(ip.dst)
        sport = tcp.sport
        dport = tcp.dport
        
        # Check for SYN flag, and only add the unique pairs
        # should only be 3 
        if tcp.flags & dp.tcp.TH_SYN:
            if len(tcp_flows) == 0:
                tcp_flows.append((sport, sip, dport, dip))
            else:
                # check if the same pair already exists
                found = False
                for tcp_flow in tcp_flows:
                    if (sport == tcp_flow[0] or sport == tcp_flow[2]) and (dport == tcp_flow[0] or dport == tcp_flow[2]):
                        found = True
                if not found:
                    tcp_flows.append((sport, sip, dport, dip))
    return tcp_flows


def first_two_transaction(filename, tcp_flows):
    output = [[] for _ in range(len(tcp_flows) * 2)]
    f = open(filename, "rb")

    flow_count = [0 for _ in range(len(tcp_flows))]

    found_shift = False

    for _, buf in dp.pcap.Reader(f):
        eth = dp.ethernet.Ethernet(buf)
        
        ip = eth.data
        tcp = ip.data
        
        # Get the source port, source ip, destination port, destional ip
        sip = sk.inet_ntoa(ip.src)
        dip = sk.inet_ntoa(ip.dst)
        sport = tcp.sport
        dport = tcp.dport
        
        if tcp.flags & dp.tcp.TH_SYN and not found_shift:
            opts = str(tcp.opts).split("\\x")[-1][:-1] # Get the scale without the hypostpey
            scale = int(opts, 16)
            found_shift = True
        
        for i, tcp_flow in enumerate(tcp_flows): 
            if ((tcp_flow[0] == sport and tcp_flow[2] == dport) or (tcp_flow[0] == dport and tcp_flow[2] == sport)) and flow_count[i] < 3:
                flow_count[i] += 1
            else:
                if tcp_flow[0] == sport and tcp_flow[2] == dport:
                    if len(output[2*i]) == 0:
                        output[2*i].append(f"first transaction from ip {sip} to {dip} {sport} to {dport} seq: {tcp.seq:,d} ack: {tcp.ack:,d} window: {tcp.win * (2**scale):,d} from sender")
                    elif len(output[2*i]) == 1:
                        output[2*i].append(f"second transaction from ip {sip} to {dip} {sport} to {dport} seq: {tcp.seq:,d} ack:{tcp.ack:,d} window: {tcp.win * (2**scale):,d} from sender")
                elif tcp_flow[0] == dport and tcp_flow[2] == sport:
                    if len(output[2*i + 1]) == 0:
                        output[2*i+1].append(f"first transaction from ip {sip} to {dip} {sport} to {dport} seq: {tcp.seq:,d} ack: {tcp.ack:,d} window: {tcp.win * (2**scale):,d} from receiver")
                    elif len(output[2*i + 1]) == 1:
                        output[2*i + 1].append(f"second transaction from ip {sip} to {dip} {sport} to {dport} seq: {tcp.seq:,d} ack: {tcp.ack:,d} window: {tcp.win * (2**scale):,d} from receiver")
    
    return output


def flow_throughput(filename, tcp_flows):
    payload_send = [0 for _ in range(len(tcp_flows))] # Used to sum the payload length
    first_packet = [-1 for _ in range(len(tcp_flows))] # time for the first packet
    last_packet = [-1 for _ in range(len(tcp_flows))] # time for the last packet

    f = open(filename, "rb")

    for ts, buf in dp.pcap.Reader(f):
        eth = dp.ethernet.Ethernet(buf)
        
        ip = eth.data
        tcp = ip.data
        
        # Get the source port, source ip, destination port, destional ip
        sip = sk.inet_ntoa(ip.src)
        dip = sk.inet_ntoa(ip.dst)
        sport = tcp.sport
        dport = tcp.dport
        
        for i, tcp_flow in enumerate(tcp_flows): 
            if sport == tcp_flow[0] and dport == tcp_flow[2]:
                payload_send[i] +=  ip.len - ip.hl
                
                if first_packet[i] == -1:
                    first_packet[i] = ts
                if tcp.flags & dp.tcp.TH_FIN:
                    last_packet[i] = ts
    
    throughputs = []
    
    for i, payload in enumerate(payload_send):
        throughputs.append((payload / (last_packet[i] - first_packet[i])))
    
    return throughputs


def congestion_window(filename, tcp_flows):
    f = open(filename, "rb")
    
    # Each list stores the sender -> receiver packets for each flow
    tcp_flows_packet = [[] for _ in range(len(tcp_flows))]
    
    # Need to estimate RTT
    # RTT is equal to the time the capturing device get for the first SYN of three way handshake
    # and the last ACK sent by the sender in the three way handshake
    # https://blog.packet-foo.com/wp-content/uploads/2014/07/InitialRTTAnywhere.png
    
    start_time = []
    first_ack = 0
    second_ack = 0
    counter = [0 for _ in range(len(tcp_flows))]
    for ts, buf in dp.pcap.Reader(f):
        eth = dp.ethernet.Ethernet(buf)
        
        ip = eth.data
        tcp = ip.data
        
        for i, tcp_flow in enumerate(tcp_flows):
            # skip the 3 way handshake cuz they don't help 
            if (tcp.sport == tcp_flow[0] and tcp.dport == tcp_flow[2]) or (tcp.sport == tcp_flow[2] and tcp.dport == tcp_flow[0]):
                if counter[i] < 3:
                    counter[i] += 1
                else:
                    # sender to receiver
                    if tcp.sport == tcp_flow[0] and tcp.dport == tcp_flow[2]:
                        tcp_flows_packet[i].append((ts, tcp))
                        if tcp.flags & dp.tcp.TH_ACK and counter[i] == 3:
                            start_time.append(ts) # find the start time of each tcp_flow, this will be used for finding # of packets sent in each RTT interval
                            counter[i] += 1
                            
                        if tcp.flags & dp.tcp.TH_ACK and first_ack == 0:
                            first_ack = ts
                    else:
                        if tcp.flags & dp.tcp.TH_ACK and second_ack == 0:
                            second_ack = ts
        
    # Find rtt
    rtt = second_ack - first_ack
    # We need to find the first three congestion window 
    # and we will be doing it by counting the number of packets that is sent 
    # between each rtt interval
    rtt_interval = [rtt * i for i in range(1, 4)] # 3 intervals because we are only doing 3 congestion window size
    
    cwnds = [[] for _ in range(len(tcp_flows))]
    for i in range(len(tcp_flows_packet)):
        packets = tcp_flows_packet[i]
        
        # The starting time for this tcp flow
        tcp_flow_start_time = start_time[i]
        
        # Go through each of the packets in the current tcp_flow, subtracting start_time from ts, to get the relative time
        time = [ts - tcp_flow_start_time for ts, _ in packets]
        timestamp_counter = 0
        
        for interval in rtt_interval:
            packet_counter = 0 # Keeps track of how many packets we get for each rtt interval
            while time[timestamp_counter] < interval:
                packet_counter += 1
                timestamp_counter += 1
            # Out of loop means rtt interval is done estimating add to result
            cwnds[i].append(packet_counter) 
        
    return cwnds
        

def retransmission_count(packets, sender_receiver, receiver_sender):
    # Use counter class to count
    sender_receiver_count = Counter([packet[1] for packet in sender_receiver]) # counts the number of sequence packet we sent, if there are duplicate that means retransmission
    receiver_sender_count = Counter([packet[2] for packet in receiver_sender]) # count the number of duplicate ACK for a packet
    
    triple_dup_ack = [ack for ack, count in receiver_sender_count.items() if count > 3] # more than 3 ack then we will count that as triple dup
    duplicate_seq = [seq for seq, count in sender_receiver_count.items() if count > 1] # more than 1 means that the same sequence block is sent more than once
    
    # We find the intersection of these two lists, which tells us which seq block is sent using triple dup ack
    intersection = set(triple_dup_ack).intersection(duplicate_seq)

    out_of_order = 0
    
    for x in intersection:
        # The number for the first dup
        first_dup_ack = 0
        count = 0
        
        for packet in receiver_sender:
            # look at receiver to sender
            if packet[2] == x:
                count += 1
            if count == 2:
                first_dup_ack = packet[0]
                break
        count = 0
        for packet in sender_receiver:
            if packet[1] == x:
                count += 1
            if count == 2:
                if first_dup_ack > packet[0]:
                    out_of_order += 1
                break
                        
    fast_retransmission = len(intersection) - out_of_order
    retransmission = len(duplicate_seq) - fast_retransmission
    
    return fast_retransmission, retransmission


def get_all_retransmission(filename, tcp_flows):
    output = []
    packets = []
    
    f = open(filename, "rb")
    for ts, buf in dp.pcap.Reader(f):
        eth = dp.ethernet.Ethernet(buf)
        
        ip = eth.data
        tcp = ip.data
        
        packets.append(tcp)
        
    for tcp_flow in tcp_flows:
        sender_receiver = []
        receiver_sender = []
        skip = 0 # Skip the 3 way handshake
        counter = 0
        for packet in packets:
            # skip the three way handshake
            if skip < 3 and ((packet.sport == tcp_flow[0] and packet.dport == tcp_flow[2]) or (packet.sport == tcp_flow[2] and packet.dport == tcp_flow[0])):
                skip += 1
                continue
            
            # append each packet to its correct list
            if packet.sport == tcp_flow[0] and packet.dport == tcp_flow[2]:
                sender_receiver.append((counter, packet.seq, packet.ack))
                counter += 1
            elif packet.sport == tcp_flow[2] and packet.dport == tcp_flow[0]:
                receiver_sender.append((counter, packet.seq, packet.ack))
                counter += 1
        # get the retransmission count
        output.append(retransmission_count(packets, sender_receiver, receiver_sender))
    
    return output


if __name__ == "__main__":
    filename = sys.argv[1]
    tcp_flows = flow_identification(filename)
    transactions = first_two_transaction(filename, tcp_flows)
    bpss = flow_throughput(filename, tcp_flows)
    cwnds = congestion_window(filename, tcp_flows)
    retransmissions = get_all_retransmission(filename, tcp_flows)
    
    for index, tcp_flow in enumerate(tcp_flows, start=1):
        print(f"Flow {index}")
        print("Part A")
        print("a.")
        print(f"\t{tcp_flow}", end="\n\n")
        print("b.")
        for i in range(2):
            print(f"\t{transactions[(2*(index - 1))][i]}") # transaction from sender to receiver 
            print(f"\t{transactions[(2*(index - 1)) + 1][i]}\n") # transaction from receiver to sender
        print()
        print(f"c.\n\tSender {tcp_flows[index - 1][0]} to receiver {tcp_flows[index - 1][2]}'s throughput is {bpss[index - 1]:,f} bytes per second\n")
        print("Part B")
        print(f"1.\tFirst 3 Congestion Window Size: {cwnds[index - 1]}")
        print(f"2.\tRetransmission due to triple ACK: {retransmissions[index - 1][0]}\n\tRetransmission due to timeout: {retransmissions[index - 1][1]}\n")
        print("--" * 50)