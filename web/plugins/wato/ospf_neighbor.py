#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# License: GNU General Public License v2
#
# Author: thl-cmk[at]outlook[dot]com
# URL   : https://thl-cmk.hopto.org
# Date  : 2020-07-26
#
# wato plugin for ospf_neighbor check
#
#

register_check_parameters(
    subgroup_networking,
    'ospf_neighbor',
    _('OSPF neighbor'),
    Dictionary(
        elements=[
            ('neighborstate',
             Dictionary(
                 title=_('State to report for OSPF neighbor state'),
                 elements=[
                     ('1',
                      MonitoringState(
                          title=_('1 - down'),
                          default_value=2,
                      ),
                      ),
                     ('2',
                      MonitoringState(
                          title=_('2 - attempt'),
                          default_value=1,
                      ),
                      ),
                     ('3',
                      MonitoringState(
                          title=_('3 - init'),
                          default_value=1,
                      ),
                      ),
                     ('4',
                      MonitoringState(
                          title=_('4 - twoWay'),
                          default_value=0,
                      ),
                      ),
                     ('5',
                      MonitoringState(
                          title=_('5 - exchangeStart'),
                          default_value=1,
                      ),
                      ),
                     ('6',
                      MonitoringState(
                          title=_('6 - exchange'),
                          default_value=1,
                      ),
                      ),
                     ('7',
                      MonitoringState(
                          title=_('7 - loading'),
                          default_value=1,
                      ),
                      ),
                     ('8',
                      MonitoringState(
                          title=_('8 - full'),
                          default_value=0,
                      ),
                      ),
                 ]
             )
             ),
            ('peer_list',
             ListOf(
                 Tuple(
                     title=('OSPF Neighbors'),
                     elements=[
                         TextUnicode(
                             title=_('OSPF Neighbor IP address'),
                             help=_('The configured value must match a OSPF Neighbor item reported by the monitored '
                                    'device. For example: "10.10.10.10"'),
                             allow_empty=False,
                         ),
                         TextUnicode(
                             title=_('OSPF Neighbor Alias'),
                             help=_('You can configure an individual alias here for the OSPF Neighbor matching '
                                    'the text configured in the "OSPF Neighbor IP address" field. The alias will '
                                    'be shown in the infotext'),
                             allow_empty=False,
                         ),
                         MonitoringState(
                             default_value=2,
                             title=_('State if not found'),
                             help=_('You can configure an individual state if the OSPF Neighbor matching the text '
                                    'configured in the "OSPF Neighbor IP address" field is not found')
                         )]),
                 add_label=_('Add OSPF Neighbor'),
                 movable=False,
                 title=_('OSPF Neighbor specific configuration'),
             )),
        ],
    ),
    TextAscii(title=_('OSPF Neighbor IP address')),
    match_type='dict',
)