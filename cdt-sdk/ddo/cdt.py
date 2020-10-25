"""CDT Lib."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import re
import hashlib
import json
from eth_utils import remove_0x_prefix
from web3 import Web3

PREFIX = 'cdt:op:'

class CDT:
    """Class representing an asset CDT."""

    @staticmethod
    def cdt(seed):
        """
        Create a cdt.

        Format of the cdt:
        cdt:op:cb36cf78d87f4ce4a784f17c2a4a694f19f3fbf05b814ac6b0b7197163888865

        :param seed: The list of checksums that is allocated in the proof, dict
        :return: Asset cdt, str.
        """
        return PREFIX + remove_0x_prefix(checksum(seed))

def checksum(seed):
    """Calculate the hash3_256."""
    return hashlib.sha3_256(
        (json.dumps(dict(sorted(seed.items(), reverse=False))).replace(" ", "")).encode(
            'utf-8')).hexdigest()

def cdt_parse(cdt):
    """
    Parse a CDT into it's parts.

    :param cdt: Asset cdt, str.
    :return: Python dictionary with the method and the id.
    """
    if not isinstance(cdt, str):
        raise TypeError(f'Expecting CDT of string type, got {cdt} of {type(cdt)} type')

    match = re.match('^cdt:([a-z0-9]+):([a-zA-Z0-9-.]+)(.*)', cdt)
    if not match:
        raise ValueError(f'CDT {cdt} does not seem to be valid.')

    result = {
        'method': match.group(1),
        'id': match.group(2),
    }

    return result


def id_to_cdt(cdt_id, method='op'):
    """Return an Ocean CDT from given a hex id."""
    if isinstance(cdt_id, bytes):
        cdt_id = Web3.toHex(cdt_id)

    # remove leading '0x' of a hex string
    if isinstance(cdt_id, str):
        cdt_id = remove_0x_prefix(cdt_id)
    else:
        raise TypeError("cdt id must be a hex string or bytes")

    # test for zero address
    if Web3.toBytes(hexstr=cdt_id) == b'':
        cdt_id = '0'
    return f'cdt:{method}:{cdt_id}'


def cdt_to_id(cdt):
    """Return an id extracted from a CDT string."""
    result = cdt_parse(cdt)
    if result and result['id'] is not None:
        return result['id']
    return None


def cdt_to_id_bytes(cdt):
    """
    Return an Ocean CDT to it's correspondng hex id in bytes.

    So cdt:op:<hex>, will return <hex> in byte format
    """
    if isinstance(cdt, str):
        if re.match('^[0x]?[0-9A-Za-z]+$', cdt):
            raise ValueError(f'{cdt} must be a CDT not a hex string')
        else:
            cdt_result = cdt_parse(cdt)
            if not cdt_result:
                raise ValueError(f'{cdt} is not a valid cdt')
            if not cdt_result['id']:
                raise ValueError(f'{cdt} is not a valid ocean cdt')
            id_bytes = Web3.toBytes(hexstr=cdt_result['id'])
    elif isinstance(cdt, bytes):
        id_bytes = cdt
    else:
        raise TypeError(
            f'Unknown cdt format, expected str or bytes, got {cdt} of type {type(cdt)}'
        )
    return id_bytes

