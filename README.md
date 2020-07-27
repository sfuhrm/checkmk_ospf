# OSPF neighbors

Monitors status of OSPF neighbors.

**NOTE**: This check is originaly from Thomas Wollner (tw[at]wollner-net[dot]de).

I changed *item* from neighbor **ID** to neighbor **IP**, added events as perfdata (incl. metrics file),\
moved part of the output to long output and done a little code cleanup to better match coding guide lines.\
Added WATO for Alias name, map check states to OSPF Neighbor state, state if neighbour not found in SNMP data.

Check Info:

* *service*: ithe check creates one service for each OSPF neighnor
* *state*: 
    * **critical** if the neighbor state is *down*
    * **warning** if the neighbor is not in *full* or *2-way* state
    * **unknown** if the agent output is invalid
* *wato*: 
    * configure check state for the different OSPF neighbor states, 
    * configure a alias for each OSPF neighbor
    * configure the check state if the OSPF neighbor not found in the SNMP data (default is UNKNOWN)
* *perfdata*: OSPF neighbor events (count)

Sample output

![sample output](/doc/sample.png?raw=true "sample [SHORT TITLE]")

