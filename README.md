# GSoC 2020 : TCP Prague in ns-3

Project webpage: [https://deepakkavoor.github.io/gsoc-2020-prague](https://deepakkavoor.github.io/gsoc-2020-prague)


This branch contains results of simulations performed in ns-3 and Linux namespaces comparing the implementations of TCP Prague.

### Contents:
- [Topology](#Topology)
- [Results in Linux namespaces](#Results-in-Linux-namespaces)
- [Results in ns-3](#Results-in-ns-3)
- [Quick comparison between ns-3 and Linux](#Quick-comparison-between-ns-3-and-Linux)

### Topology:

```
server1 -->-- wr -->-- m1 -->-- m2 -->-- m3 -->-- lr -->-- client1
```

This topology and the subsequent parameters we choose in our experiments (bottleneck rate, RTT) are motivated by Pete Heist's [tests](https://github.com/heistp/sce-l4s-bakeoff#scenario-1) comparing SCE and L4S. 
There are seven nodes with one TCP Prague flow from server1 to client1. 

Following mapping depicts the queue disc type installed at each node:

- server1 -- fq_codel
- wr -- fq_codel
- m1 -- pfifo
- m2 -- fq_codel
- m3 -- fq_codel
- lr -- fq_codel
- client1 -- fq_codel

The parameters used for queue discs are:

- fq_codel -- ce_threshold: 1ms , interval: 100ms , target: 5ms
- pfifo -- limit: 5000p 

The link between routers m3 and lr is chosen to be the bottleneck with rate 100Mbps and a configurable delay (5ms, 80ms, 160ms). All other links support a data rate of 1000Mbps and delay 1us. 

### Results in Linux namespaces

The above topology was generated in Linux namespaces using [this](https://github.com/L4STeam/linux/tree/b256daedc7672b2188f19e8b6f71ef5db7afc720) kernel version of TCP Prague.

We use [NeST](https://gitlab.com/nitk-nest/nest) to handle testbed setup, configuration,
collection and visualization of data in Linux namespaces. NeST obtains periodic socket statistics (congestion window, delivery rate, RTT) using ```ss``` tool, queue statistics using ```tc``` and throughput statistics using ```netperf``` to generate subsequent plots.

#### Steps to reproduce these results:

1. Build the [kernel](https://github.com/L4STeam/linux/tree/b256daedc7672b2188f19e8b6f71ef5db7afc720) supporting TCP Prague.

2. Install the Python packages ```numpy``` , ```matplotlib``` , ```packaging```.

3. Execute the following commands.
```bash
# clone NeST
git clone https://gitlab.com/deepakkavoor/nest.git
cd nest/
git checkout results-prague-fq
# create topology and start TCP flow
cd examples/
sudo python3 prague.py
```

The file [prague.py](https://gitlab.com/deepakkavoor/nest/-/blob/results-prague-fq/examples/prague.py) sets up nodes in the topology, installs queue discs and runs a TCP Prague flow between server1 and client1 using namespaces. The last command executes it with root access to create a folder containing results of the simulation.

For convenience, the folders in [linux-namespaces/](linux-namespaces/) contain raw simulation data obtained by following the aforementioned instructions. These contain data for bottleneck rate 100Mbps and RTT 5ms, 80ms and 160ms. Values of these parameters can be manually changed from [prague.py](https://gitlab.com/deepakkavoor/nest/-/blob/results-prague-fq/examples/prague.py).

### Results in ns-3

To simulate this topology in ns-3, we used the [l4s-evaluation](https://gitlab.com/tomhend/modules/l4s-evaluation/-/tree/hackathon/master) suite (more details about setting up nodes, queue discs and TCP flows can be found at the link).

This suite provides readily usable scripts that implement various topologies illustrating performance of L4S components. Values of congestion window, RTT, throughput are traced and stored as raw simulation data along with plots. 

#### Steps to reproduce these results:

Execute the following commands.

```bash
# clone ns-3-dev
git clone https://gitlab.com/deepakkavoor/ns-3-dev.git
cd ns-3-dev
git checkout prague-mr
# clone l4s-evaluation suite in contrib/ directory
cd contrib/
git clone https://gitlab.com/deepakkavoor/l4s-evaluation.git
cd l4s-evaluation/
git checkout results-prague-fq
cd ../../
# build ns-3-dev
./waf configure --enable-examples --enable-tests
./waf build
# simulate topology with one flow
cd contrib/l4s-evaluation/
cd experiments/tsvwg-issue-17-one-flow/
./run-single.sh
```

Executing ```run-single.sh``` creates a new directory in ```l4s-evaluation/experiments/tsvwg-issue-17-one-flow/results/``` containing raw data and plots for congestion window, RTT, throughput and queue statistics.

As before the folders in [ns-3/](ns-3/) contain raw simulation data for bottleneck rate 100Mbps and RTT 5ms, 80ms and 160ms. Values of these parameters can be manually changed from [run-single.sh](https://gitlab.com/deepakkavoor/l4s-evaluation/-/blob/results-prague-fq/experiments/tsvwg-issue-17-one-flow/run-single.sh).

### Quick comparison between ns-3 and Linux

For a quick comparison of behaviour of TCP Prague between ns-3 and Linux, selected files from directories [linux-namespaces/](linux-namespaces/) and [ns-3/](ns-3/) are cumulated in [comparison/](comparison/). These give a quick and direct summary about alignment of congestion window plots when the above topology is simulated in ns-3 and Linux namespaces.