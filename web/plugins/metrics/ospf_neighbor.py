#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# OSPF neighbor metrics plugin
#
# Author: Th.L.
# Date  : 2018-06-15
#
from cmk.gui.i18n import _

from cmk.gui.plugins.metrics import (
    metric_info,
    graph_info,
    perfometer_info
)

#####################################################################################################################
#
# define metrics for OSPF neighbor perfdata
#
#####################################################################################################################

metric_info['ospf_neighbor_ospf_events'] = {
    'title': _('Events'),
    'unit': 'count',
    'color': '16/a',
}

metric_info['ospf_neighbor_ospf_retransmission_queue_length'] = {
    'title': _('Retransmission queue length'),
    'unit': 'count',
    'color': '36/a',
}


######################################################################################################################
#
# how to graph perdata for OSPF neighbor
#
######################################################################################################################

graph_info['ospf_neighbor_ospf_events'] = {
    'title': _('OSPF neighbor events'),
    'metrics': [
        ('ospf_neighbor_ospf_events', 'area'),
    ],
}

graph_info['ospf_neighbor_ospf_retransmission_queue_length'] = {
    'title': _('OSPF neighbor Retransmission queue length'),
    'metrics': [
        ('ospf_neighbor_ospf_retransmission_queue_length', 'area'),
    ],
}
######################################################################################################################
#
# define perf-o-meter for OSPF neighbor events
#
######################################################################################################################

perfometer_info.append({
    'type': 'linear',
    'segments': ['ospf_neighbor_ospf_events'],
    # 'total': 100,
})
