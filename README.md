# GSoC 2020 : TCP Prague in ns-3

Project webpage: [https://deepakkavoor.github.io/gsoc-2020-prague](https://deepakkavoor.github.io/gsoc-2020-prague)


This branch contains results and steps to reproduce simulations performed in ns-3 and Linux namespaces.

### Topology:

server1 -->-- wr -->-- m1 -->-- m2 -->-- m3 -->-- lr -->-- client1

There are seven nodes with one TCP Prague flow from server1 to client1. 

Following mapping depicts the queue disc type installed at each node in the namespace:

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

The link between routers m3 and lr is chosen to be the bottleneck with rate 95 Mbps and a configurable delay. All other links support a data rate of 1000Mbps and delay 1us. 

### Results for Linux Namespaces

The above topology was generated in Linux namespaces using [this](https://github.com/L4STeam/linux/tree/b256daedc7672b2188f19e8b6f71ef5db7afc720) kernel version of TCP Prague.

The folders in [linux-namespaces/](linux-namespaces/) contain raw simulation data obtained for bottleneck rate 100Mbps and RTT 5ms, 80ms and 160ms.

#### Steps to reproduce these results:

-- Install [kernel](https://github.com/L4STeam/linux/tree/b256daedc7672b2188f19e8b6f71ef5db7afc720) supporting TCP Prague.

-- Make sure that following Python packages are available: numpy , matplotlib , packaging.

-- Execute the following commands.
```bash
git clone https://gitlab.com/deepakkavoor/nest.git
cd nest/
git checkout results-prague-fq
cd examples/
sudo python3 prague.py
```

The file ```prague.py``` contains required setup for aforementioned topology. Running it with root access creates a folder containing results of the simulation.