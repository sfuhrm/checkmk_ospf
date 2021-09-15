#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

###############################################################################
# $Id: ospf_neighbor 288 2012-07-10 11:06:38Z twollner $
# Descr: OSPF Neighbor State check_mk check
# $Author: twollner $
# $Date: 2012-07-10 13:06:38 +0200 (Tue, 10 Jul 2012) $
# $Rev: 288 $
###############################################################################
# Author: Thomas Wollner (tw@wollner-net.de)
###############################################################################
#
# changes by: thl-cmk[at]outlook[dot]com
# url       : https://thl-cmk.hopto.org
#
#  2018-06-15: changed item from neighbor id to neighbor ip
#              added events as perfdata (incl. metrics file)
#              moved part of the output to long output
#              a little code cleanup to better match coding guide lines
#  2019-11-03: moved 'events' from infotext to longoutput
#  2020-07-26: added parse section, alias, wato for alias and state
#  2021-09-15: rewritten for CMK 2.0
#
###############################################################################

# Example Agent Output:
# OSPF-MIB

# 1.3.6.1.2.1.14.10.1.1.172.20.2.214.0 = IpAddress: 172.20.2.214
# 1.3.6.1.2.1.14.10.1.2.172.20.2.214.0 = INTEGER: 0
# 1.3.6.1.2.1.14.10.1.3.172.20.2.214.0 = IpAddress: 192.168.1.2
# 1.3.6.1.2.1.14.10.1.4.172.20.2.214.0 = INTEGER: 2
# 1.3.6.1.2.1.14.10.1.5.172.20.2.214.0 = INTEGER: 1
# 1.3.6.1.2.1.14.10.1.6.172.20.2.214.0 = INTEGER: 8
# 1.3.6.1.2.1.14.10.1.7.172.20.2.214.0 = Counter32: 6
# 1.3.6.1.2.1.14.10.1.8.172.20.2.214.0 = Gauge32: 0
# 1.3.6.1.2.1.14.10.1.9.172.20.2.214.0 = INTEGER: 1
# 1.3.6.1.2.1.14.10.1.10.172.20.2.214.0 = INTEGER: 1
# 1.3.6.1.2.1.14.10.1.11.172.20.2.214.0 = INTEGER: 2
#
# sample parsed
# {
#  '172.17.108.52': {'helperage': '', 'prio': '1', 'permanence': 'dynamic', 'helperstatus': '', 'options': '2',
#                    'state': '8', 'hellosup': 'false', 'helperexitreason': '', 'events': 6, 'rtrid': '10.250.128.130'},
#  '172.17.108.60': {'helperage': '', 'prio': '1', 'permanence': 'dynamic', 'helperstatus': '', 'options': '2',
#                    'state': '8', 'hellosup': 'false', 'helperexitreason': '', 'events': 6, 'rtrid': '10.253.128.101'},
#  '172.17.108.58': {'helperage': '', 'prio': '1', 'permanence': 'dynamic', 'helperstatus': '', 'options': '2',
#                    'state': '8', 'hellosup': 'false', 'helperexitreason': '', 'events': 12, 'rtrid': '172.17.0.2'},
#  '172.17.108.49': {'helperage': '', 'prio': '1', 'permanence': 'dynamic', 'helperstatus': '', 'options': '2',
#                    'state': '8', 'hellosup': 'false', 'helperexitreason': '', 'events': 9, 'rtrid': '172.17.0.2'}
# }
#

from dataclasses import dataclass
from typing import Dict

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Service,
    Result,
    State,
    SNMPTree,
    exists,
    Metric,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
    StringTable,
)


@dataclass
class OspfNeighbor:
    rtrid: str
    options: str
    prio: str
    state: str
    events: int
    permanence: str
    hellosup: str
    helperstatus: str
    helperage: str
    helperexitreason: str


def parse_ospf_neighbor(string_table: StringTable) -> Dict[str, OspfNeighbor]:
    def ospf_nbr_hellosuppressed(st: str) -> str:
        names = {'1': 'true',
                 '2': 'false'}
        return names.get(st, st)

    def ospf_nbr_permanence(st: str) -> str:
        names = {'1': 'dynamic',
                 '2': 'permanent'}
        return names.get(st, st)

    def ospf_nbr_helperstatus(st: str) -> str:
        names = {'1': 'notHelping',
                 '2': 'helping'}
        return names.get(st, st)

    def ospf_nbr_helperexitreason(st: str) -> str:
        names = {'1': 'none',
                 '2': 'inProgress',
                 '3': 'completed',
                 '4': 'timedOut',
                 '5': 'topologyChanged'}
        return names.get(st, st)

    def ospf_nbr_options(st: str) -> str:
        """
        A bit mask corresponding to the neighbor's options field.
        Bit 0, if set, indicates that the system will operate on Type of Service metrics other than TOS 0.
               If zero, the neighbor will ignore all metrics except the TOS 0 metric.
        Bit 1, if set, indicates that the associated area accepts and operates on external information;
               if zero, it is a stub area.
        Bit 2, if set, indicates that the system is capable of routing IP multicast datagrams, that is that it
               implements the multicast extensions to OSPF.
        Bit 3, if set, indicates that the associated area is an NSSA. These areas are capable of carrying type-7
               external advertisements, which are translated into type-5 external advertisements at NSSA borders.
        """
        try:
            st = ord(st)
        except TypeError:
            return 'unknown'

        options = []
        for key, value in [
            (1, 'non TOS 0 service metrics accepted'),
            (2, 'not a stub area'),
            (4, 'IP multicast routing capable'),
            (8, 'is NSSA'),
        ]:
            if st & key == key:
                options.append(value)

        options = ', '.join(options)
        if options == '':
            return 'unknown'
        else:
            return options

    parsed = {}
    for ip, rtrid, options, prio, state, events, permanence, hellosup, helperstatus, helperage, \
        helperexitreason in string_table:
        parsed[ip] = OspfNeighbor(
            rtrid=rtrid,
            options=ospf_nbr_options(options),
            prio=prio,
            state=state,
            events=int(events),
            permanence=ospf_nbr_permanence(str(permanence)),
            hellosup=ospf_nbr_hellosuppressed(hellosup),
            helperstatus=ospf_nbr_helperstatus(helperstatus),
            helperage=helperage,
            helperexitreason=ospf_nbr_helperexitreason(helperexitreason),
        )
    return parsed


def discovery_ospf_neighbor(section: Dict[str, OspfNeighbor]) -> DiscoveryResult:
    for neighbor in section.keys():
        yield Service(item=neighbor)


def check_ospf_neighbor(item, params, section: Dict[str, OspfNeighbor]) -> CheckResult:
    def ospf_nbr_state(st: str) -> str:
        names = {'1': 'down',
                 '2': 'attempt',
                 '3': 'init',
                 '4': 'twoWay',
                 '5': 'exchangeStart',
                 '6': 'exchange',
                 '7': 'loading',
                 '8': 'full'}
        return names.get(st, 'unknown: %s' % st)

    # default monitoring states for ospfNbrState
    neighborstate = {
        '1': 2,  # down
        '2': 1,  # attempt
        '3': 1,  # init
        '4': 0,  # twoWay
        '5': 1,  # exchangeStart
        '6': 1,  # exchange
        '7': 1,  # loading
        '8': 0,  # full
    }

    not_found_state = params['state_not_found', 3]

    for neighbour, neighbourAlias, neighbourNotFoundState in params.get('peer_list', []):
        if item == neighbour:
            yield Result(state=State.OK, summary=f'[{neighbourAlias}]')
            not_found_state = neighbourNotFoundState

    try:
        neighbor = section[item]
    except KeyError:
        yield Result(state=State(not_found_state), notice='Item not found in SNMP data')
        return

    yield Result(state=State.OK, summary=f'Neighbor ID: {neighbor.rtrid}')

    neighborstate.update(params.get('neighborstate', neighborstate))  # update neighborstatus with params

    yield Result(state=State(neighborstate.get(neighbor.state, 3)), summary=f'Status {ospf_nbr_state(neighbor.state)}')

    yield Metric(value=neighbor.events, name='ospf_neighbor_ospf_events')

    for text, value in [
        ('options', neighbor.options),
        ('priority', neighbor.prio),
        ('permanence', neighbor.permanence),
        ('hello suppressed', neighbor.hellosup),
        ('helper status', neighbor.helperstatus),
        ('helper age', neighbor.helperage),
        ('helper exit reason', neighbor.helperexitreason),
    ]:
        if value != '':
            yield Result(state=State.OK, notice=f'Neighbor {text}: {value}')


register.snmp_section(
    name='ospf_neighbor',
    parse_function=parse_ospf_neighbor,
    fetch=SNMPTree(
        base='.1.3.6.1.2.1.14.10.1',  # OSPF-MIB::ospfNbrEntry
        oids=[
            '1',  # 'ospfNbrIpAddr'
            '3',  # 'ospfNbrRtrId'
            '4',  # 'ospfNbrOptions'
            '5',  # 'ospfNbrPriority'
            '6',  # 'ospfNbrState
            '7',  # 'ospfNbrEvents'
            '10',  # 'ospfNbrPermanence'
            '11',  # 'ospfNbrHelloSuppressed'
            '12',  # 'ospfNbrRestartHelperStatus'
            '13',  # 'ospfNbrRestartHelperAge'
            '14',  # 'ospfNbrRestartHelperExitReason'
        ]
    ),
    detect=exists('.1.3.6.1.2.1.14.10.1.1.*')
)

register.check_plugin(
    name='ospf_neighbor',
    service_name='OSPF neighbor %s',
    discovery_function=discovery_ospf_neighbor,
    check_function=check_ospf_neighbor,
    check_default_parameters={
        'state_not_found': 3,
    },
    check_ruleset_name='ospf_neighbor',
)
