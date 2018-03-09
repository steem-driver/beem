"""graphennewsrpc."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import time
import json
import logging


log = logging.getLogger(__name__)


class UnauthorizedError(Exception):
    """UnauthorizedError Exception."""

    pass


class RPCConnection(Exception):
    """RPCConnection Exception."""

    pass


class RPCError(Exception):
    """RPCError Exception."""

    pass


class NumRetriesReached(Exception):
    """NumRetriesReached Exception."""

    pass


def is_network_appbase_ready(props):
    """Checks if the network is appbase ready"""
    network_version = '0.0.0'
    if "STEEMIT_BLOCKCHAIN_VERSION" in props:
        network_version = props['STEEMIT_BLOCKCHAIN_VERSION']
    elif "STEEM_BLOCKCHAIN_VERSION" in props:
        network_version = props['STEEM_BLOCKCHAIN_VERSION']
    return network_version >= '0.19.4'


def get_query(appbase, request_id, api_name, name, args):
    if not appbase:
        query = {"method": "call",
                 "params": [api_name, name, list(args)],
                 "jsonrpc": "2.0",
                 "id": request_id}
    else:
        args = json.loads(json.dumps(args))
        # print(args)
        if len(args) == 1 and isinstance(args[0], dict):
            query = {"method": api_name + "." + name,
                     "params": args[0],
                     "jsonrpc": "2.0",
                     "id": request_id}
        elif args:
            query = {"method": "call",
                     "params": [api_name, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": request_id}
        elif api_name == "condenser_api":
            query = {"method": api_name + "." + name,
                     "jsonrpc": "2.0",
                     "params": [],
                     "id": request_id}
        else:
            query = {"method": api_name + "." + name,
                     "jsonrpc": "2.0",
                     "params": {},
                     "id": request_id}
    return query


def get_api_name(appbase, *args, **kwargs):
    if not appbase:
        # Sepcify the api to talk to
        if "api_id" not in kwargs:
            if ("api" in kwargs) and len(kwargs["api"]) > 0:
                api_name = kwargs["api"].replace("_api", "") + "_api"
            else:
                api_id = 0
                api_name = None
        else:
            api_id = kwargs["api_id"]
            api_name = api_id
    else:
        # Sepcify the api to talk to
        if "api_id" not in kwargs:
            if ("api" in kwargs) and len(kwargs["api"]) > 0:
                if kwargs["api"] != "jsonrpc":
                    api_name = kwargs["api"].replace("_api", "") + "_api"
                else:
                    api_name = kwargs["api"]
            else:
                api_name = "condenser_api"
        else:
            api_name = "condenser_api"
    return api_name


def sleep_and_check_retries(num_retries, cnt, url):
    """Sleep and check if num_retries is reached"""
    if (num_retries >= 0 and cnt > num_retries):
        raise NumRetriesReached()

    if cnt < 1:
        sleeptime = 0
    elif cnt < 10:
        sleeptime = (cnt - 1) * 2
    else:
        sleeptime = 10
    if sleeptime:
        log.warning("Lost connection to node during wsconnect(): %s (%d/%d) "
                    % (url, cnt, num_retries) +
                    "Retrying in %d seconds" % sleeptime
                    )
        time.sleep(sleeptime)