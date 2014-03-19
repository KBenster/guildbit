"""
murmur.py
All murmur utility functions and logic for interfacing with configured murmur servers.
"""

import requests
from requests.auth import HTTPDigestAuth

from settings import MURMUR_HOSTS

##
## Helper functions to load configs from settings
##


def get_host_by_location(location):
    """
    Searches MURMUR_HOSTS settings and returns tuple of address, uri, and hostname for given location.
    """
    for i in MURMUR_HOSTS:
        for k, v in i.iteritems():
            if v == location:
                return {
                    'address': i['address'],
                    'uri': i['uri'],
                    'hostname': i['hostname'],
                    'http_uri': i['http_uri'],
                    'username': i['username'],
                    'password': i['password']
                }


def get_murmur_hostname(location):
    """
    Shortcut for getting murmur's hostname.
    """
    return get_host_by_location(location)['hostname']


def get_http_uri(location):
    """
    Shortcut for getting murmur's hostname.
    """
    return get_host_by_location(location)['http_uri']


def get_murmur_uri(location):
    """
    Shortcut for getting murmur's uri.
    """
    return get_host_by_location(location)['uri']


def get_murmur_credentials(location):
    """
    Shortcut for getting murmur's credentials for specified location.
    """
    username = get_host_by_location(location)['username']
    password = get_host_by_location(location)['password']
    return {'username': username, 'password': password}


##
## Functions to interface with murmur-rest server
##

def create_server(host, payload):
    """
    Accepts host and POST data payload as parameters and returns the id of the server created at host.
    """
    auth = get_murmur_credentials(host)
    r = requests.post(host + "/api/v1/servers/", data=payload, auth=HTTPDigestAuth(auth['username'], auth['password']))
    server_id = r.json()['id']
    return server_id


def create_server_by_location(location, payload):
    """
    Accepts location and POST data payload as parameters and returns the id of the server created at host.
    """
    host = get_host_by_location(location)['uri']
    auth = get_murmur_credentials(location)
    try:
        r = requests.post(host + "/api/v1/servers/", data=payload, auth=HTTPDigestAuth(auth['username'],
                                                                                       auth['password']))
        if r.status_code == 200:
            server_id = r.json()['id']
            return server_id
    except requests.exceptions.ConnectionError as e:
        import traceback
        traceback.print_exc()
        return None
    return None


def get_server(host, instance_id):
    """
    Accepts host location (sf.guildbit.com), and mumble_instance id and returns dict of server information.
    """
    uri = get_murmur_uri(host)
    auth = get_murmur_credentials(host)
    try:
        r = requests.get("%s/api/v1/servers/%i" % (uri, instance_id), auth=HTTPDigestAuth(auth['username'],
                                                                                          auth['password']))
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError as e:
        return None
    return None


def delete_server(host, instance_id):
    """
    Deletes a server by hostname and instance_id.
    """
    uri = get_murmur_uri(host)
    auth = get_murmur_credentials(host)
    try:
        r = requests.delete("%s/api/v1/servers/%i" % (uri, instance_id), auth=HTTPDigestAuth(auth['username'],
                                                                                             auth['password']))
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.ConnectionError as e:
        return None
    return None


def get_server_stats(host):
    """
    Get server stats for one host.
    """
    uri = get_murmur_uri(host)
    auth = get_murmur_credentials(host)
    try:
        r = requests.get("%s/api/v1/stats/" % uri, auth=HTTPDigestAuth(auth['username'],
                                                                       auth['password']))
        if r.status_code == 200:
            stats = {
                'servers_online': r.json()['booted_servers'],
                'users_online': r.json()['users_online']
            }
            return stats
    except requests.exceptions.ConnectionError as e:
        pass
    stats = {
        'servers_online': 0,
        'users_online': 0
    }
    return stats


def get_all_server_stats():
    """
    Get server stats for all hosts.
    """
    stats = {
        'servers_online': 0,
        'users_online': 0
    }
    for i in MURMUR_HOSTS:
        try:
            s = get_server_stats(i['hostname'])
            stats['servers_online'] += s.get('servers_online', 0)
            stats['users_online'] += s.get('users_online', 0)
        except:
            pass
    return stats


def get_server_logs(host, instance_id):
    """
    Get server logs for specified host and instance.
    """
    uri = get_murmur_uri(host)
    auth = get_murmur_credentials(host)
    try:
        r = requests.get("%s/api/v1/servers/%s/logs" % (uri, instance_id), auth=HTTPDigestAuth(auth['username'],
                                                                                               auth['password']))
        if r.status_code == 200:
            logs = r.json()
            return logs
    except requests.exceptions.ConnectionError as e:
        pass
    logs = []
    return logs
