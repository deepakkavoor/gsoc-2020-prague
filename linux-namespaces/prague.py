import sys
import os

sys.path.append('../')
from nest.topology import *
from nest.experiment import *

# Topology
# (10.0.1.1)                                                 (10.0.6.2)
# server1 -->-- wr -->-- m1 -->-- m2 -->-- m3 -->-- lr -->-- client1

# logging.set_log_level(2)

# Change the parameters below to what you want

bottleneck = 100
rtt = 160
startTime = 5
endTime = 200
# by default fq_codel is installed at m3
# if use_dualq is set to True dualq is installed at m3 instead of fq_codel
use_dualq=False

bottleneck = 0.95 * bottleneck
bottleneck = str(bottleneck) + 'mbit'
oneWayDelay=str(int(rtt/2))+'ms'

server1_wr_bandwidth = '1000mbit'
wr_m1_bandwidth = '1000mbit'
m1_m2_bandwidth = '1000mbit'
m2_m3_bandwidth = '1000mbit'
m3_lr_bandwidth = bottleneck
lr_client1_bandwidth = '1000mbit'

server1_wr_latency = oneWayDelay
wr_m1_latency = '1us'
m1_m2_latency = '1us'
m2_m3_latency = '1us'
m3_lr_latency = '1us'
lr_client1_latency = '1us'

dualq_queuedisc = 'dualpi2'
dualq_params = {}

fq_codel_queuedisc = 'fq_codel'
fq_codel_params = {'ce_threshold': '1ms','interval': '100ms', 'target': '5ms'}

pfifo_queue_disc = 'pfifo'
pfifo_params = {'limit': '5000p'}

nFlows = 1
tcpVersion = 'prague'

# Set up topology

server1 = Node('server1')
wr = Node('wr')
m1 = Node('m1')
m2 = Node('m2')
m3 = Node('m3')
lr = Node('lr')
client1 = Node('client1')

# enable accurate ecn
server1.configure_tcp_param('ecn', '3')
wr.configure_tcp_param('ecn', '3')
m1.configure_tcp_param('ecn', '3')
m2.configure_tcp_param('ecn', '3')
m3.configure_tcp_param('ecn', '3')
lr.configure_tcp_param('ecn', '3')
client1.configure_tcp_param('ecn', '3')

wr.enable_ip_forwarding()
m1.enable_ip_forwarding()
m2.enable_ip_forwarding()
m3.enable_ip_forwarding()
lr.enable_ip_forwarding()

(server1_wr, wr_server1) = connect(server1, wr)
(wr_m1, m1_wr) = connect(wr, m1)
(m1_m2, m2_m1) = connect(m1, m2)
(m2_m3, m3_m2) = connect(m2, m3)
(m3_lr, lr_m3) = connect(m3, lr)
(lr_client1, client1_lr) = connect(lr, client1)

server1_wr.set_address('10.0.1.1/24')
wr_server1.set_address('10.0.1.2/24')
wr_m1.set_address('10.0.2.1/24')
m1_wr.set_address('10.0.2.2/24')
m1_m2.set_address('10.0.3.1/24')
m2_m1.set_address('10.0.3.2/24')
m2_m3.set_address('10.0.4.1/24')
m3_m2.set_address('10.0.4.2/24')
m3_lr.set_address('10.0.5.1/24')
lr_m3.set_address('10.0.5.2/24')
lr_client1.set_address('10.0.6.1/24')
client1_lr.set_address('10.0.6.2/24')

server1.add_route('DEFAULT', server1_wr)
wr.add_route(server1_wr.get_address(), wr_server1);
wr.add_route(client1_lr.get_address(), wr_m1);
m1.add_route(server1_wr.get_address(), m1_wr);
m1.add_route(client1_lr.get_address(), m1_m2);
m2.add_route(server1_wr.get_address(), m2_m1);
m2.add_route(client1_lr.get_address(), m2_m3);
m3.add_route(server1_wr.get_address(), m3_m2);
m3.add_route(client1_lr.get_address(), m3_lr);
lr.add_route(server1_wr.get_address(), lr_m3);
lr.add_route(client1_lr.get_address(), lr_client1);
client1.add_route('DEFAULT', client1_lr)

server1_wr.set_attributes(server1_wr_bandwidth, server1_wr_latency,
                     fq_codel_queuedisc, **fq_codel_params)
wr_server1.set_attributes(server1_wr_bandwidth, server1_wr_latency,
                     fq_codel_queuedisc, **fq_codel_params)

wr_m1.set_attributes(wr_m1_bandwidth, wr_m1_latency,
                     fq_codel_queuedisc, **fq_codel_params)
m1_wr.set_attributes(wr_m1_bandwidth, wr_m1_latency,
                     pfifo_queue_disc, **pfifo_params)

m1_m2.set_attributes(m1_m2_bandwidth, m1_m2_latency,
                     pfifo_queue_disc, **pfifo_params)
m2_m1.set_attributes(m1_m2_bandwidth, m1_m2_latency,
                     fq_codel_queuedisc, **fq_codel_params)

m2_m3.set_attributes(m2_m3_bandwidth, m2_m3_latency,
                     fq_codel_queuedisc, **fq_codel_params)
if use_dualq:
    m3_m2.set_attributes(m2_m3_bandwidth, m2_m3_latency,
                     dualq_queuedisc)
else:
    m3_m2.set_attributes(m2_m3_bandwidth, m2_m3_latency,
                     fq_codel_queuedisc, **fq_codel_params)
if use_dualq:
    m3_lr.set_attributes(m3_lr_bandwidth, m3_lr_latency,
                     dualq_queuedisc)
else:
    m3_lr.set_attributes(m3_lr_bandwidth, m3_lr_latency,
                     fq_codel_queuedisc, **fq_codel_params)
                     
lr_m3.set_attributes(m3_lr_bandwidth, m3_lr_latency,
                     fq_codel_queuedisc, **fq_codel_params)

lr_client1.set_attributes(lr_client1_bandwidth, lr_client1_latency,
                     fq_codel_queuedisc, **fq_codel_params)
client1_lr.set_attributes(lr_client1_bandwidth, lr_client1_latency,
                     fq_codel_queuedisc, **fq_codel_params)


flow = Flow(server1, client1, client1_lr.get_address(), startTime, endTime, nFlows)
exp = Experiment('one-flow-control-scenario')
exp.add_tcp_flow(flow, tcpVersion) # 2nd optional arg here is for tcp algo

exp.require_node_stats(server1)
exp.require_qdisc_stats(m3_lr) # Explicitly mention from where you want to collect qdisc stats

exp.run()

os.system ("sudo ip -all netns delete")
