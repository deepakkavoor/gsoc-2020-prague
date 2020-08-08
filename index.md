# Integrating TCP Prague into ns-3 

This page summarizes my work done from May - August 2020 with the [ns-3](https://gitlab.com/nsnam/) Network Simulator as part of [Google Summer of Code](https://summerofcode.withgoogle.com/) 2020.

I am grateful to the developers at ns-3 for accepting my proposal, and to Google for funding me throughout the project.

## Introduction and Motivation

The L4S architecture [1] is designed to reduce latency for all Internet applications, even those that traditionally have required queues such as CoDel and PIE in the network to maintain high throughput and utilization. In order to reduce queuing delay, this approach shifts the focus from optimizing AQMs towards introducing newer techniques in the TCP. The core objective is to use a congestion control mechanism that scales with congestion in the network. 

The existing TCP congestion controls in Reno and Cubic can perform badly in high-speed networks because of their slow response with large congestion windows. These _non-scalable_ congestion controls fail to better utilize networks with high bandwidth-delay products [4]. _Scalable_ TCP offers a robust mechanism to improve this performance using traditional TCP receivers without interacting badly with existing traffic. With this in mind, scalable congestion controls such as DCTCP already exist. However, there are several problems if DCTCP was to be simply deployed on the Internet: for example, if DCTCP flows and Reno-like flows were to share a common queue, and since DCTCP increases the rate of ECN marking, Reno-like flows would reduce their throughput by a larger margin leading to unfairness between the two kinds of flows. 

Therefore, several new features are added to DCTCP to allow it to be deployed on the internet, in a Reno-friendly way: the L4S service traffic needs to be isolated from the queuing delay of the Classic service traffic, a host needs to distinguish L4S and Classic packets with an identifier, etc. All these additional modifications over DCTCP have been drafted into a new protocol called TCP Prague, that aims to integrate scalable congestion control into the Internet by providing many safety mechanisms that allow it to coexist with current Classic protocols.


## Project Overview

### Phase 1

### Phase 2

### Phase 3

#### References



You can use the [editor on GitHub](https://github.com/deepakkavoor/gsoc-2020-prague/edit/gh-pages/index.md) to maintain and preview the content for your website in Markdown files.

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

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/deepakkavoor/gsoc-2020-prague/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://docs.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
