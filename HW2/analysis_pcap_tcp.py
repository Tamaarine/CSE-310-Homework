import dpkt  as dp
import socket as sk

f = open("assignment2.pcap", "rb")

pcap = dp.pcap.Reader(f)

tcp_flows = [] # a tuple of 4, that consists of the sport, sip, dport, dip. Only three of them exists for this problem

# PART A
for ts, buf in pcap:
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

# Print the pairs, for Part A, a
for tcp_flow in tcp_flows:
    print(tcp_flow[0], tcp_flow[1], tcp_flow[2], tcp_flow[3]) 
    

# PART B
output = [[] for _ in range(len(tcp_flows) * 2)]


f = open("assignment2.pcap", "rb")

flow_count = [0 for _ in range(len(tcp_flows))]

pcap = dp.pcap.Reader(f)

for ts, buf in pcap:
    eth = dp.ethernet.Ethernet(buf)
    
    ip = eth.data
    tcp = ip.data
    
    # Get the source port, source ip, destination port, destional ip
    sip = sk.inet_ntoa(ip.src)
    dip = sk.inet_ntoa(ip.dst)
    sport = tcp.sport
    dport = tcp.dport
    
    
    # filter away the PUSH request
    if not tcp.flags & dp.tcp.TH_PUSH:
        for i, tcp_flow in enumerate(tcp_flows): 
            if ((tcp_flow[0] == sport and tcp_flow[2] == dport) or (tcp_flow[0] == dport and tcp_flow[2] == sport)) and flow_count[i] < 3:
                flow_count[i] += 1
            else:
                if tcp_flow[0] == sport and tcp_flow[2] == dport:
                    if len(output[2*i]) == 0:
                        output[2*i].append(f"first transaction from ip {sip} to {dip} {sport} to {dport} seq:{tcp.seq} ack:{tcp.ack} window:{tcp.win} from sender")
                    elif len(output[2*i]) == 1:
                        output[2*i].append(f"second transaction from ip {sip} to {dip} {sport} to {dport} seq:{tcp.seq} ack:{tcp.ack} window:{tcp.win} from sender")
                elif tcp_flow[0] == dport and tcp_flow[2] == sport:
                    if len(output[2*i + 1]) == 0:
                        output[2*i+1].append(f"first transaction from ip {sip} to {dip} {sport} to {dport} seq:{tcp.seq} ack:{tcp.ack} window:{tcp.win} from receiver")
                    elif len(output[2*i + 1]) == 1:
                        output[2*i + 1].append(f"second transaction from ip {sip} to {dip} {sport} to {dport} seq:{tcp.seq} ack:{tcp.ack} window:{tcp.win} from receiver")
                    
# 2 transactions each              
for message in output:
    for transaction in message:
        print(transaction)