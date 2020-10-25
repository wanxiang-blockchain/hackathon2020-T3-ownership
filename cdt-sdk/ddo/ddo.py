"""DDO Lib."""

#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0
import copy
import json
from eth_utils import add_0x_prefix

from ddo.cdt import cdt_to_id, PREFIX
from ddo.service import Service
from ddo.public_key_base import PublicKeyBase, PUBLIC_KEY_TYPE_ETHEREUM_ECDSA

class DDO:
    """DDO class to create, import, export, validate DDO objects."""

    def __init__(self, cdt=None, json_text=None, json_filename=None, dictionary=None):
        """Clear the DDO data values."""
        self._cdt = cdt
        self._public_keys = []
        self._authentications = []
        self._services = []
        self._proof = None
        self._other_values = {}

        if not json_text and json_filename:
            with open(json_filename, 'r') as file_handle:
                json_text = file_handle.read()

        if json_text:
            self._read_dict(json.loads(json_text))
        elif dictionary:
            self._read_dict(dictionary)

    @property
    def cdt(self):
        """ Get the CDT."""
        return self._cdt

    @property
    def services(self):
        """Get the list of services."""
        return self._services[:]

    @property
    def child_cdts(self):
        return self._services[0].child_cdts

    @property
    def proof(self):
        """Get the static proof, or None."""
        return self._proof

    def assign_cdt(self, cdt):
        if self._cdt:
            raise AssertionError('"cdt" is already set on this DDO instance.')
        assert cdt and isinstance(cdt, str), \
            f'cdt must be of str type, got {cdt} of type {type(cdt)}'
        assert cdt.startswith(PREFIX), \
            f'"cdt" seems invalid, must start with {PREFIX} prefix.'
        self._cdt = cdt
        return cdt

    def add_service(self, service_type, service_endpoint=None, child_cdts=None, values=None):
        """
        Add a service to the list of services on the DDO.

        :param service_type: Service
        :param service_endpoint: Service endpoint, str
        :param values: Python dict with index, templateId, serviceAgreementContract,
        list of conditions and purchase endpoint.
        """
        values = copy.deepcopy(values) if values else {}
        service = Service(service_type, service_endpoint, child_cdts, values.pop('attributes', None))
        self._services.append(service)

    def add_proof(self, checksums):
        """Add a proof to the DDO, based on the public_key id/index and signed with the private key
        add a static proof to the DDO, based on one of the public keys.

        :param checksums: dict with the checksum of the main attributes of each service, dict
        :param publisher_account: account of the publisher, account
        """
        self._proof = {
            'signatureValue': '',
            'checksum': checksums
        }

    def add_public_key(self, cdt, public_key):
        """
        Add a public key object to the list of public keys.

        :param public_key: Public key, PublicKeyHex
        """
        self._public_keys.append(
            PublicKeyBase(cdt, **{"owner": public_key, "type": PUBLIC_KEY_TYPE_ETHEREUM_ECDSA}))

    def add_authentication(self, public_key, authentication_type):
        """
        Add a authentication public key id and type to the list of authentications.

        :param public_key: Key id, Authentication
        :param authentication_type: Authentication type, str
        """
        authentication = {}
        if public_key:
            authentication = {'type': authentication_type, 'publicKey': public_key}
        self._authentications.append(authentication)

    def get_service(self, service_type=None):
        """Return a service using."""
        for service in self._services:
            if service.type == service_type and service_type:
                return service
        return None

    def as_dictionary(self, is_proof=True):
        """
        Return the DDO as a JSON dict.

        :param if is_proof: if False then do not include the 'proof' element.
        :return: dict
        """

        data = {
            'id': self._cdt,
        }
        if self._services:
            values = []
            for service in self._services:
                values.append(service.as_dictionary())
            data['service'] = values
        if self._proof and is_proof:
            data['proof'] = self._proof

        if self._other_values:
            data.update(self._other_values)

        return data

    def _read_dict(self, dictionary):
        """Import a JSON dict into this DDO."""
        values = copy.deepcopy(dictionary)
        self._cdt = values.pop('id')

        if 'service' in values:
            self._services = []
            for value in values.pop('service'):
                if isinstance(value, str):
                    value = json.loads(value)
                else:
                    service = Service.from_json(value)

                self._services.append(service)
        if 'proof' in values:
            self._proof = values.pop('proof')

        self._other_values = values