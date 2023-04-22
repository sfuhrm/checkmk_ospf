# OSPF neighbors

Monitors status of OSPF neighbors.

### Acknowledgment 
This check is originaly from Thomas Wollner (tw[at]wollner-net[dot]de).

I changed the *item* from neighbor **ID** to neighbor **IP**, added events as perfdata (incl. metrics file),\
moved part of the output to long output and done a little code cleanup to better match coding guide lines.\
Added WATO for Alias name, map check states to OSPF Neighbor state, state if neighbour not found in SNMP data.

---
### Check Info:

* *service*: ithe check creates one service for each OSPF neighbor with the neighbor IP as item
* *state*: 
    * **critical** if the neighbor state is *down*
    * **warning** if the neighbor is not in *full* or *2-way* state
    * **unknown** if the agent output is invalid
* *wato*: 
    * default monitoring state if neighbor not found in SNMP data
    * configure monitoring state for the different OSPF neighbor states
    * configure a alias for each OSPF neighbor
    * configure the monitoring state if the OSPF neighbor is not found in the SNMP data
* *perfdata*:
    * OSPF neighbor events (count)
    * Retransmission queue length (count)

---
### Download
* [ospf_neighbor.mkp](https://thl-cmk.hopto.org/gitlab/checkmk/vendor-independent/ospf_neighbor/-/raw/master/ospf_neighbor.mkp "Download the MKP file")
                        
---
### Installation

You can install the package by uploading it to your CheckMK site and as site user run `mkp install ospf_neighbor.mkp`.


In the Enterprise/Free edition of CheckMK you can use the GUI to install the package (_Setup_ -> _Extension Packages_ -> _Upload package_)

---
### Want to Contribute?
Nice ;-) Have a look at the [contribution guidelines](CONTRIBUTING.md "Contributing")

---

Sample output

![sample output](/doc/sample.png?raw=true "sample output")

WATO options

![WATO options](/doc/wato.png?raw=true "WATO options")
