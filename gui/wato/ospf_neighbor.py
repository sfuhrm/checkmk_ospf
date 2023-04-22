#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2020-07-26
#
# wato plugin for ospf_neighbor check
#
# 2023-04-22: moved to ~/local/lib/check_mk/gui/plugins/wato

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    ListOf,
    Tuple,
    TextUnicode,
    MonitoringState,
)

from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersNetworking,
)


def _parameter_valuespec_ospf_neighbor():
    return Dictionary(
        elements=[
            ('state_not_found',
             MonitoringState(
                 title=_('State to report if neighbor not found'),
                 help=_('Default monitoring state if the neighbor not found in the SNMP data. Default monitoring '
                        'state is "UNKNOWN"'),
                 default_value=3,
             )),
            ('neighborstate',
             Dictionary(
                 title=_('State to report for OSPF neighbor state'),
                 help=_('Map each OSPF state to a CheckMK monitoring state'),
                 elements=[
                     ('1',
                      MonitoringState(
                          title=_('1 - down'),
                          help=_('This is the first OSPF neighbor state. It means that no information (hellos) has '
                                 'been received from this neighbor, but hello packets can still be sent to the '
                                 'neighbor in this state. During the fully adjacent neighbor state, if a router '
                                 'doesn\'t receive hello packet from a neighbor within the RouterDeadInterval time '
                                 '(RouterDeadInterval = 4*HelloInterval by default) or if the manually configured '
                                 'neighbor is being removed from the configuration, then the neighbor state changes '
                                 'from Full to Down. Default monitoring state is "CRIT"'),
                          default_value=2,
                      )),
                     ('2',
                      MonitoringState(
                          title=_('2 - attempt'),
                          help=_('This state is only valid for manually configured neighbors in an NBMA environment. '
                                 'In Attempt state, the router sends unicast hello packets every poll interval to the '
                                 'neighbor, from which hellos have not been received within the dead interval. '
                                 'Default monitoring state is "WARN"'),
                          default_value=1,
                      )),
                     ('3',
                      MonitoringState(
                          title=_('3 - init'),
                          help=_('This state specifies that the router has received a hello packet from its neighbor, '
                                 'but the receiving router\'s ID was not included in the hello packet. When a router '
                                 'receives a hello packet from a neighbor, it should list the sender\'s router ID in '
                                 'its hello packet as an acknowledgment that it received a valid hello packet. '
                                 'Default monitoring state is "WARN"'),
                          default_value=1,
                      )),
                     ('4',
                      MonitoringState(
                          title=_('4 - twoWay'),
                          help=_('This state designates that bi-directional communication has been established between '
                                 'two routers. Bi-directional means that each router has seen the other\'s hello '
                                 'packet. This state is attained when the router receiving the hello packet sees its '
                                 'own Router ID within the received hello packet\'s neighbor field. At this state, a '
                                 'router decides whether to become adjacent with this neighbor. On broadcast media '
                                 'and non-broadcast multiaccess networks, a router becomes full only with the '
                                 'designated router (DR) and the backup designated router (BDR); it stays in the 2-way '
                                 'state with all other neighbors. On Point-to-point and Point-to-multipoint networks, '
                                 'a router becomes full with all connected routers. At the end of this stage, the DR '
                                 'and BDR for broadcast and non-broadcast multiacess networks are elected. For more '
                                 'information on the DR election process, refer to DR Election. Note: Receiving a '
                                 'Database Descriptor (DBD) packet from a neighbor in the init state will also a cause '
                                 'a transition to 2-way state. Default monitoring state is "OK"'),
                          default_value=0,
                      )),
                     ('5',
                      MonitoringState(
                          title=_('5 - exchangeStart'),
                          help=_('Once the DR and BDR are elected, the actual process of exchanging link state '
                                 'information can start between the routers and their DR and BDR. In this state, '
                                 'the routers and their DR and BDR establish a master-slave relationship and choose '
                                 'the initial sequence number for adjacency formation. The router with the higher '
                                 'router ID becomes the master and starts the exchange, and as such, is the only '
                                 'router that can increment the sequence number. Note that one would logically '
                                 'conclude that the DR/BDR with the highest router ID will become the master during '
                                 'this process of master-slave relation. Remember that the DR/BDR election might be '
                                 'purely by virtue of a higher priority configured on the router instead of highest '
                                 'router ID. Thus, it is possible that a DR plays the role of slave. And also note '
                                 'that master/slave election is on a per-neighbor basis. Default monitoring state '
                                 'is "WARN"'),
                          default_value=1,
                      )),
                     ('6',
                      MonitoringState(
                          title=_('6 - exchange'),
                          help=_('In the exchange state, OSPF routers exchange database descriptor (DBD) packets. '
                                 'Database descriptors contain link-state advertisement (LSA) headers only and '
                                 'describe the contents of the entire link-state database. Each DBD packet has a '
                                 'sequence number which can be incremented only by master which is explicitly '
                                 'acknowledged by slave. Routers also send link-state request packets and link-state '
                                 'update packets (which contain the entire LSA) in this state. The contents of the '
                                 'DBD received are compared to the information contained in the routers link-state '
                                 'database to check if new or more current link-state information is available with '
                                 'the neighbor. Default monitoring state is "WARN"'),
                          default_value=1,
                      )),
                     ('7',
                      MonitoringState(
                          title=_('7 - loading'),
                          help=_('In this state, the actual exchange of link state information occurs. Based on the '
                                 'information provided by the DBDs, routers send link-state request packets. The '
                                 'neighbor then provides the requested link-state information in link-state update '
                                 'packets. During the adjacency, if a router receives an outdated or missing LSA, it '
                                 'requests that LSA by sending a link-state request packet. All link-state update '
                                 'packets are acknowledged. Default monitoring state is "WARN"'),
                          default_value=1,
                      )),
                     ('8',
                      MonitoringState(
                          title=_('8 - full'),
                          help=_('In this state, routers are fully adjacent with each other. All the router and '
                                 'network LSAs are exchanged and the routers databases are fully synchronized. Full '
                                 'is the normal state for an OSPF router. If a router is stuck in another state, '
                                 'it\'s an indication that there are problems in forming adjacencies. The only '
                                 'exception to this is the 2-way state, which is normal in a broadcast network. '
                                 'Routers achieve the full state with their DR and BDR only. Neighbors always see '
                                 'each other as 2-way. Default monitoring state is "OK"'),
                          default_value=0,
                      )),
                 ])
             ),
            ('peer_list',
             ListOf(
                 Tuple(
                     title=_('OSPF Neighbors'),
                     elements=[
                         TextUnicode(
                             title=_('OSPF Neighbor IP address'),
                             help=_(
                                 'The configured value must match a OSPF Neighbor item reported by the monitored '
                                 'device. For example: "10.10.10.10"'),
                             allow_empty=False,
                         ),
                         TextUnicode(
                             title=_('OSPF Neighbor Alias'),
                             help=_('You can configure an individual alias here for the OSPF Neighbor matching '
                                    'the text configured in the "OSPF Neighbor IP address" field. The alias will '
                                    'be shown in the check info (i.e. [your alias])'),
                             allow_empty=False,
                         ),
                         MonitoringState(
                             default_value=2,
                             title=_('State if not found'),
                             help=_('You can configure an individual state if the OSPF Neighbor matching the text '
                                    'configured in the "OSPF Neighbor IP address" field is not found. '
                                    'Default monitoring state is "CRIT".')
                         )]),
                 add_label=_('Add OSPF Neighbor'),
                 movable=False,
                 title=_('OSPF Neighbor specific configuration'),
             )),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name='ospf_neighbor',
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextAscii(title=_('OSPF Neighbor IP address'), ),
        match_type='dict',
        parameter_valuespec=_parameter_valuespec_ospf_neighbor,
        title=lambda: _('OSPF neighbor'),
    ))
