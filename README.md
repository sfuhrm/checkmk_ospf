# OSPF neighbors [(Download the MKP package)](/../../../-/raw/master/ospf_neighbor.mkp "Download MKP package")

 **Note: this package is for CheckMK version 2.x. For other versions see the corresponding branch.**

Monitors status of OSPF neighbors.

**NOTE**: This check is originaly from Thomas Wollner (tw[at]wollner-net[dot]de).

I changed *item* from neighbor **ID** to neighbor **IP**, added events as perfdata (incl. metrics file),\
moved part of the output to long output and done a little code cleanup to better match coding guide lines.\
Added WATO for Alias name, map check states to OSPF Neighbor state, state if neighbour not found in SNMP data.

Check Info:

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
* *perfdata*: OSPF neighbor events (count)

Sample output

![sample output](/doc/sample.png?raw=true "sample output")

WATO options

![WATO options](/doc/wato.png?raw=true "WATO options")
