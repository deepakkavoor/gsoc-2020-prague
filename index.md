## Implementing TCP Prague in ns-3 

This page summarizes my work done from June 2020 - August 2020 with the [ns-3](https://gitlab.com/nsnam/) Network Simulator as part of [Google Summer of Code](https://summerofcode.withgoogle.com/) 2020.

I am grateful to the developers at ns-3 for accepting my proposal, and to Google for funding me throughout the project.

## Introduction and Motivation

The Low Latency, Low Loss Scalable Throughput (L4S) architecture (todo: ref) is designed to reduce latency for all Internet applications. In order to reduce queuing delay, this approach shifts the focus from optimizing Active Queue Management (AQM) towards introducing newer techniques in the TCP. The core objective is to use a congestion control mechanism that _scales_ with congestion in the network. 

Existing TCP congestion controls such as Reno and Cubic can perform badly in high-speed networks because of their slow response with large congestion windows. These _non-scalable_ congestion controls fail to better utilize networks with high bandwidth-delay products (todo: ref). _Scalable_ TCP offers a robust mechanism to improve this performance using traditional TCP receivers without interacting badly with existing traffic. 

With this in mind, scalable congestion controls such as Data Center TCP (DCTCP) already exist. However, there are several problems if DCTCP was deployed on the Internet: for example, if DCTCP flows and Reno-like flows were to share a common queue, DCTCP increases the rate of ECN marking and Reno-like flows would reduce their throughput by a larger margin leading to unfairness between the two kinds of flows.

Therefore, several new features are added to DCTCP to allow it to be deployed on the internet, in a Reno-friendly way. To state a few, 

- The L4S service traffic needs to be isolated from the queuing delay of the Classic service traffic.
- The host needs to distinguish L4S and Classic packets with an identifier.

All these additional modifications over DCTCP have been drafted into a new protocol called **TCP Prague**, that aims to integrate scalable congestion controls into the Internet by providing many safety mechanisms that allow it to coexist with current Classic protocols. These modifications are highlighted in Figure 1.

![Figure 1: Overview of TCP Prague](Images/prague-overview.png?raw=true)


## Project Overview

At the time of this work, TCP Prague did not have a well defined IETF draft. Therefore, our primary goal was to align the ns-3 implementation of Prague with that of Linux. The L4S Team led by Bob Briscoe already had a Linux implementation of TCP Prague which was being tested separately, and wasn't yet merged into mainline Linux kernel. The ns-3 version followed [this commit](https://github.com/L4STeam/linux/tree/b256daedc7672b2188f19e8b6f71ef5db7afc720) of their Linux implementation.   

On a higher level, this project was divided into three phases each spanning a month. The objectives for each phase are briefly described below:

- Phase 1: Add dynamic pacing rate to ns-3 TCP
- Phase 2: Implement RTT independence in ns-3 DCTCP
- Phase 3: Extend ns-3 Prague from ns-3 DCTCP aligned with Linux Prague

### Phase 1 - Dynamic Pacing Rate

**Link to code:**

**[https://gitlab.com/deepakkavoor/ns-3-dev/-/commits/pacing-mr](https://gitlab.com/deepakkavoor/ns-3-dev/-/commits/pacing-mr)**

It is important for a Prague sender to pace out packets during transmission. This helps to decrease pressure on the bottleneck queue and reduces congestion marks. Before this work, ns-3 already had the pacing feature in TCP. However, one could only configure a fixed pacing rate, which would be followed throughout the simulation. 

In this phase, I worked on adding the feature that allows pacing rate to change dynamically based on the current congestion window and RTT measurement. This feature is present in Linux, and adding it to ns-3 would be a valuable contribution towards aligning ns-3 Prague with Linux.

The pacing rate is updated as follows.

```
pacingRate = factor * cWnd / RTT
```

The value of factor can be manually configured, and can be different depending on whether TCP is in Slow Start or Congestion Avoidance.

During Slow Start, Linux uses a default value of `factor = 2` (which allows TCP to probe for higher speeds) and `factor = 1` during Congestion Avoidance. The same default parameters are used in ns-3.

A test suite was also added that confirms whether packets are being paced out at the correct rate, depending on whether the sender TCP is currently in Slow Start or Congestion Avoidance. 

### Phase 2 - RTT Independence

**Link to code:**

**[https://gitlab.com/deepakkavoor/ns-3-dev/-/commits/prague-mr](https://gitlab.com/deepakkavoor/ns-3-dev/-/commits/prague-mr)**

Prague, being a scalable congestion control, tends to experience low queuing delays due to its responsive nature. This leads to lower RTT, meaning that a Prague sender changes its congestion window more frequently.

 If Prague and a Classic flow such as Reno were to exist simultaneously with a common bottleneck, Prague would thus have a bigger share of the bandwidth and experience more throughput compared to Reno.

Reducing RTT dependence allows us to remove this unfairness and safely deploy Prague over the internet. The idea here is to scale `cWnd` growth **during Congestion Avoidance**, so that both flows now reasonably converge to a common throughput.

First, we set a parameter `targetRTT` (with a default of 15ms) denoting the RTT in which Prague is _expected_ to operate in. This means that `cWnd` is updated in such a way that Prague is fair to a flow operating with an RTT of 15ms.

Suppose the actual RTT that Prague experiences is `curRTT`. Ideally the `cWnd` increment (in segments) for every ACK during Congestion Avoidance would be

```
increment = 1 / cWnd 
```

which would lead to an overall increase of 1 segment per RTT. If we enable RTT independence, the new increment would look like

```
increment = (curRTT / targetRTT) * (curRTT / targetRTT) * 1 / cWnd
```

To explain better, let's take an example: suppose `curRTT` = 5ms, `targetRTT` = 15ms, `cWnd ` = 10 segments. Based on `targetRTT`, we should expect an increase of 1 segment in 15ms to ensure fairness. 

- RTT independence disabled: The actual RTT being 5ms, `cWnd` is increased by 1 segment for every 5ms (based on the original update equation during Congestion Avoidance). This means that `cWnd` is increased by 3 segments in 15ms, leading to unfairness with a Classic flow whose actual RTT is 15ms and `cWnd` increase per RTT is 1 segment.

- RTT independence enabled: 

- - Let's see the significance of the first factor in the modified update equation. In this case, `cWnd` is increased by `(1 / 3) * 1 / cWnd` for every ACK, meaning that `cWnd` is increased by 1 / 3 segments in 5ms and consequently by 1 segment in 15ms. This is the expected increase for a Reno flow with RTT 15ms.

- - The second factor is also equally important. With only the first factor, Prague and Reno (with say `cWnd` = 10 segments for each and RTTs 5ms and 15ms respectively) now update `cWnd` by equal amounts per ACK. However, the update frequency is higher in case of Prague (due to its lower RTT). More concretely, the number of times `cWnd` is incrememted in case of Reno per 15ms is 10, whereas Prague increments `cWnd` 10 times per 5ms and hence 30 times per 15ms. If we assume 

```
Increase in throughput per 15ms = number of times cWnd is updated in 15ms * cWnd increment each time
```

note that the increase in throughput for Reno is 10 * 1 = 10 segments per 15ms, and for Prague is 30 * 1 = 30 segments per 15ms. If we indeed used the second factor, `cWnd` increase per ACK for Prague would be `1 / 9 * 1 / cWnd` (the increase per 15ms would be 1 / 3), and hence the increase in throughput would be 30 * 1 / 3 = 10 segments per 15ms.

There are different types of RTT Scaling heuristics used, and the increment equation mentioned before refer to the "Rate Control" heuristic. For other heuristics like "Scalable" and "Additive", one can refer to the code linked above.

### Phase 3 - Alignment with Linux

#### References



<!-- You can use the [editor on GitHub](https://github.com/deepakkavoor/gsoc-2020-prague/edit/gh-pages/index.md) to maintain and preview the content for your website in Markdown files.

Whenever you commit to this repository, GitHub Pages will run [Jekyll](https://jekyllrb.com/) to rebuild the pages in your site, from the content in your Markdown files.

### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/). -->
