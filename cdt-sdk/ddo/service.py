"""
创建DDO中的service，算法/算力/数据，包含子CDT列表
author: lqb
"""

import copy
import json
import logging

logger = logging.getLogger(__name__)

class Service:
    SERVICE_ENDPOINT = 'serviceEndpoint'
    SERVICE_TYPE = 'type'
    SERVICE_CHILD_CDTS = 'child_cdts'
    SERVICE_ATTRIBUTES = 'attributes'

    def __init__(self, service_type, service_endpoint, child_cdts, attributes):
        self._service_endpoint = service_endpoint
        self._type = service_type or ''
        self._child_cdts = child_cdts
        self._attributes = attributes or {}

    @property
    def type(self):
        return self._type

    @property
    def service_endpoint(self):
        return self._service_endpoint

    @property
    def child_cdts(self):
        return self._child_cdts

    @property
    def attributes(self):
        return self._attributes

    def as_dictionary(self):
        attributes = {}
        for key, value in self._attributes.items():
            if isinstance(value, object) and hasattr(value, 'as_dictionary'):
                value = value.as_dictionary()
            elif isinstance(value, list):
                value = [v.as_dictionary() if hasattr(v, 'as_dictionary') else v for v in value]

            attributes[key] = value

        values = {
            self.SERVICE_TYPE: self._type,
            self.SERVICE_ENDPOINT: self._service_endpoint,
            self.SERVICE_CHILD_CDTS: self._child_cdts,
            self.SERVICE_ATTRIBUTES: attributes
        }

        return values

    @classmethod
    def _parse_json(cls, service_dict):
        sd = copy.deepcopy(service_dict)
        _service_endpoint = sd.pop(cls.SERVICE_ENDPOINT, None)
        _type = sd.pop(cls.SERVICE_TYPE, None)
        _attributes = sd.pop(cls.SERVICE_ATTRIBUTES, None)
        _child_cdts = sd.pop(cls.SERVICE_CHILD_CDTS, None)

        return _type, _service_endpoint, _child_cdts, _attributes

    @classmethod
    def from_json(cls, service_dict):
        _type, _service_endpoint, _child_cdts, _attributes = cls._parse_json(service_dict)
        
        return cls(
            _type,
            _service_endpoint,
            _child_cdts,
            _attributes
        )
