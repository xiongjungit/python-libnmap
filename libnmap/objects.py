#!/usr/bin/env python
from libnmap.diff import NmapDiff


class NmapHost(object):
    """
        NmapHost is a class representing a host object of NmapReport

        :todo: add tcpsequence
    """
    def __init__(self, starttime='', endtime='', address=None, status=None,
                 hostnames=None, services=None, extras=None):
        """
            NmapHost constructor
            :param starttime: unix timestamp of when the scan against
            that host started
            :type starttime: string
            :param endtime: unix timestamp of when the scan against
            that host ended
            :type endtime: string
            :param address: dict ie :{'addr': '127.0.0.1', 'addrtype': 'ipv4'}
            :param status: dict ie:{'reason': 'localhost-response',
                                    'state': 'up'}
            :return: NmapHost:
        """
        self._starttime = starttime
        self._endtime = endtime
        self._hostnames = hostnames if hostnames is not None else []
        self._status = status if status is not None else {}
        self._address = address if address is not None else {}
        self._services = services if services is not None else []
        self._extras = extras if extras is not None else {}

    def __eq__(self, other):
        """
            Compare eq NmapHost based on :
                - hostnames
                - address
                - if an associated services has changed
            :return boolean:
        """
        rval = False
        if(self.__class__ == other.__class__ and self.id == other.id):
            rval = (self.changed(other) == 0)
        return rval

    def __ne__(self, other):
        """
            Compare ne NmapHost based on :
                - hostnames
                - address
                - if an associated services has changed
            :return: boolean:
        """
        rval = True
        if(self.__class__ == other.__class__ and self.id == other.id):
            rval = (self.changed(other) > 0)
        return rval

    def __repr__(self):
        """
            String representing the object
            :return: string
        """
        return "{0}: [{1} ({2}) - {3}]".format(self.__class__.__name__,
                                               self.address,
                                               " ".join(self._hostnames),
                                               self.status)

    def __hash__(self):
        """
            Hash is needed to be able to use our object in sets
            :return: hash
        """
        return (hash(self.status) ^ hash(self.address) ^
                hash(frozenset(self._services)) ^
                hash(frozenset(" ".join(self._hostnames))))

    def changed(self, other):
        """
            return the number of attribute who have changed
            :param  other: NmapReport
            :return int:
        """
        return len(self.diff(other).changed())

    @property
    def starttime(self):
        return self._starttime

    @property
    def endtime(self):
        return self._endtime

    @property
    def address(self):
        return self._address['addr']

    @address.setter
    def address(self, addrdict):
        self._address = addrdict

    @property
    def status(self):
        return self._status['state']

    @status.setter
    def status(self, statusdict):
        self._status = statusdict

    @property
    def hostnames(self):
        return self._hostnames

    @property
    def services(self):
        return self._services

    def get_ports(self):
        """
            Retrieve a list of the port used by each service of the NmapHost

            :return: list: of tuples (port,'proto') ie:[(22,'tcp'),(25, 'tcp')]
        """
        return [(p.port, p.protocol) for p in self._services]

    def get_open_ports(self):
        """
            Same as get_ports() but only for open ports

            :return: list: of tuples (port,'proto') ie:[(22,'tcp'),(25, 'tcp')]
        """
        return ([(p.port, p.protocol)
                for p in self._services if p.state == 'open'])

    def get_service(self, portno, protocol='tcp'):
        """
            :param portno: int the portnumber
            :param protocol='tcp': string ('tcp','udp')

            :return: NmapService or None
        """
        plist = [p for p in self._services if
                 p.port == portno and p.protocol == protocol]
        if len(plist) > 1:
            raise Exception("Duplicate services found in NmapHost object")
        return plist.pop() if len(plist) else None

    def get_service_byid(self, id):
        """
            :param id: integer
            :return NmapService or None
        """
        service = [s for s in self.services if s.id() == id]
        if len(service) > 1:
            raise Exception("Duplicate services found in NmapHost object")
        return service.pop() if len(service) == 1 else None

    def os_class_probabilities(self):
        rval = []
        try:
            rval = self._extras['osclass']
        except (KeyError, TypeError):
            pass
        return rval

    def os_match_probabilities(self):
        rval = []
        try:
            rval = self._extras['osmatch']
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def os_fingerprint(self):
        rval = ''
        try:
            rval = self._extras['osfingerprint']
        except (KeyError, TypeError):
            pass
        return rval

    def os_ports_used(self):
        rval = []
        try:
            rval = self._extras['ports_used']
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def tcpsequence(self):
        rval = ''
        try:
            rval = self._extras['tcpsequence']['difficulty']
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def ipsequence(self):
        rval = ''
        try:
            rval = self._extras['ipidsequance']['class']
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def uptime(self):
        rval = 0
        try:
            rval = int(self._extras['uptime']['seconds'])
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def lastboot(self):
        rval = ''
        try:
            rval = self._extras['uptime']['lastboot']
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def distance(self):
        rval = 0
        try:
            rval = int(self._extras['distance']['value'])
        except (KeyError, TypeError):
            pass
        return rval

    @property
    def id(self):
        return self.address

    def get_dict(self):
        """
            Return a dict representation of the object
            This is needed by NmapDiff to allow comparaison
            :return dict
        """
        d = dict([("%s.%s" % (s.__class__.__name__,
                   str(s.id)), hash(s)) for s in self.services])
        d.update({'address': self.address, 'status': self.status,
                  'hostnames': " ".join(self._hostnames)})
        return d

    def diff(self, other):
        """
            :param other: NmapHost to diff with
            :return NmapDiff
        """
        return NmapDiff(self, other)


class NmapService(object):
    def __init__(self, portid, protocol='tcp', state=None,
                 service=None, service_extras=None):
        try:
            self._portid = int(portid or -1)
        except (ValueError, TypeError):
            raise
        if self._portid < 0 or self._portid > 65535:
            raise ValueError

        self._protocol = protocol
        self._state = state if state is not None else {}
        self._service = service if service is not None else {}
        self._service_extras = []
        if service_extras is not None:
            self._service_extras = service_extras

    def __eq__(self, other):
        rval = False
        if(self.__class__ == other.__class__ and self.id == other.id):
            rval = (self.changed(other) == 0)
        return rval

    def __ne__(self, other):
        rval = True
        if(self.__class__ == other.__class__ and self.id == other.id):
            rval = (self.changed(other) > 0)
        return rval

    def __repr__(self):
        return "{0}: [{1} {2}/{3} {4} ({5})]".format(self.__class__.__name__,
                                                     self.state,
                                                     str(self.port),
                                                     self.protocol,
                                                     self.service,
                                                     self.banner)

    def __hash__(self):
        return (hash(self.port) ^ hash(self.protocol) ^ hash(self.state) ^
                hash(self.service) ^ hash(self.banner))

    def changed(self, other):
        return len(self.diff(other).changed())

    @property
    def port(self):
        return self._portid

    @property
    def protocol(self):
        return self._protocol

    @property
    def state(self):
        return self._state['state'] if 'state' in self._state else None

    def add_state(self, state={}):
        self._state = state

    @property
    def service(self):
        return self._service['name'] if 'name' in self._service else None

    def open(self):
        return (True
                if 'state' in self._state and self._state['state'] == 'open'
                else False)

    @property
    def banner(self):
        notrelevant = ['name', 'method', 'conf']
        b = ''
        if 'method' in self._service and self._service['method'] == "probed":
            b = " ".join([k + ": " + self._service[k]
                          for k in self._service.keys()
                              if k not in notrelevant])
        return b

    def scripts_results(self):
        scripts_dict = None
        try:
            scripts_dict = dict([(bdct['id'], bdct['output'])
                                 for bdct in self._service_extras])
        except (KeyError, TypeError):
            pass
        return scripts_dict

    @property
    def id(self):
        return (self.protocol, self.port)

    def get_dict(self):
        return ({'id': str(self.id), 'port': str(self.port),
                 'protocol': self.protocol, 'banner': self.banner,
                 'service': self.service, 'state': self.state})

    def diff(self, other):
        return NmapDiff(self, other)


class NmapReport(object):
    """
        :todo:
                - remove get_raw_data makes no sens
    """
    def __init__(self, raw_data=None):
        self._nmaprun = {}
        self._scaninfo = {}
        self._hosts = []
        self._runstats = {}
        if raw_data is not None:
            self.__set_raw_data(raw_data)

    def save(self, backend):
        """this fct get an NmapBackendPlugin representing the backend
        """
        if backend is not None:
            #do stuff
            id = backend.insert(self)
        else:
            raise RuntimeError
        return id

    def diff(self, other):
        if self.__is_consistent() and other.__is_consistent():
            r = NmapDiff(self, other)
        else:
            r = set()
        return r

    @property
    def started(self):
        return self._nmaprun['start']

    @property
    def commandline(self):
        return self._nmaprun['args']

    @property
    def version(self):
        return self._nmaprun['version']

    @property
    def scan_type(self):
        return self._scaninfo['type']

    @property
    def hosts(self):
        return self._hosts

    @property
    def endtime(self):
        return self._runstats['finished']['time']

    @property
    def summary(self):
        return self._runstats['finished']['summary']

    @property
    def elapsed(self):
        return self._runstats['finished']['elapsed']

    @property
    def hosts_up(self):
        return (self._runstats['hosts']['up']
                if 'hosts' in self._runstats
                else '')

    @property
    def hosts_down(self):
        return (self._runstats['hosts']['down']
                if 'hosts' in self._runstats
                else '')

    @property
    def hosts_total(self):
        return (self._runstats['hosts']['total']
                if 'hosts' in self._runstats
                else '')

    def get_raw_data(self):
        raw_data = {'_nmaprun': self._nmaprun,
                    '_scaninfo': self._scaninfo,
                    '_hosts': self._hosts,
                    '_runstats': self._runstats}
        return raw_data

    def __set_raw_data(self, raw_data):
        self._nmaprun = raw_data['_nmaprun']
        self._scaninfo = raw_data['_scaninfo']
        self._hosts = raw_data['_hosts']
        self._runstats = raw_data['_runstats']

    def __is_consistent(self):
        r = False
        rd = self.get_raw_data()
        _consistent_keys = ['_nmaprun', '_scaninfo', '_hosts', '_runstats']
        if (set(_consistent_keys) == set(rd.keys()) and
                len([k for k in rd.keys() if rd[k] is not None]) == 4):
                r = True
        return r

    def get_dict(self):
        d = dict([("%s.%s" % (h.__class__.__name__, str(h.id)), hash(h))
                 for h in self.hosts])
        d.update({'hosts_up': self.hosts_up, 'hosts_down': self.hosts_down,
                  'hosts_total': self.hosts_total})
        return d

    @property
    def id(self):
        return hash(1)

    def __repr__(self):
        return "{0} {1} hosts: {2} {3}".format(self._nmaprun, self._scaninfo,
                                               len(self._hosts),
                                               self._runstats)
