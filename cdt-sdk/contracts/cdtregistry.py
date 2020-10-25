
import logging
from urllib.parse import urlparse

from web3 import Web3

from cdt_utils.contract_base import ContractBase
from cdt_utils.event_filter import EventFilter

logger = logging.getLogger(__name__)

class CDTRegistry(ContractBase):
    """CDT注册类"""
    CDT_REGISTRY_EVENT_NAME = 'CDTAttributeRegistered'
    CONTRACT_NAME = 'CDTRegistry'

    def add_authority(self, address, name, account):
        tx_hash = self.send_transaction(
            'addAuthority',
            (address, name),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'account_key': account.key}
        )
        return self.is_tx_successful(tx_hash)

    def is_authority(self, address):
        return self.contract_concise.isAuthority(address)

    def register(self, cdt, checksum, url, account):
        transaction = self._register_attribute(
            cdt, checksum, url, account)

        receipt = self.get_tx_receipt(transaction)
        if receipt:
            return receipt.status == 1

        _filters = dict()
        _filters['_cdt'] = Web3.toBytes(hexstr=cdt)
        _filters['_owner'] = Web3.toBytes(hexstr=account.address)
        event = self.subscribe_to_event(self.CDT_REGISTRY_EVENT_NAME, 15, _filters, wait=True)
        return event is not None

    def _register_attribute(self, cdt, checksum, value, account):
        return self.send_transaction(
            'registerAttribute',
            (cdt,
             checksum,
             value),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'account_key': account.key}
        )

    def grant_permission(self, cdt, cdt_to_grant, account):
        tx_hash = self.send_transaction(
            'grantPermission',
            (cdt, cdt_to_grant),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'account_key': account.key}
        )
        return self.is_tx_successful(tx_hash)

    def get_permission(self, cdt, cdt_granted):
        return self.contract_concise.getPermission(cdt, cdt_granted)

    def get_cdt_owner(self, cdt):
        return self.contract_concise.getCDTOwner(cdt)

    def get_owner_asset_ids(self, address):
        block_filter = self._get_event_filter(owner=address)
        log_items = block_filter.get_all_entries(max_tries=5)
        cdt_list = []
        for log_i in log_items:
            cdt_list.append(log_i.args['_cdt'])

        return cdt_list

    def get_block_number_updated(self, cdt):
        return self.contract_concise.getBlockNumberUpdated(cdt)

    def get_registered_attribute(self, cdt_bytes):
        result = None
        cdt = Web3.toHex(cdt_bytes)
        
        block_number = self.get_block_number_updated(cdt_bytes)
        logger.debug(f'got blockNumber {block_number} for cdt {cdt}')
        if block_number == 0:
            logger.warning(f'cdt {cdt} is not found on-chain')
            return result

        block_filter = self._get_event_filter(cdt=cdt, from_block=block_number - 1,
                                                  to_block=block_number + 1)
        log_items = block_filter.get_all_entries(max_tries=5)

        if log_items:
            log_item = log_items[-1].args
            value = log_item['_value']
            block_number = log_item['_blockNumberUpdated']
            result = {
                'checksum': log_item['_checksum'],
                'value': value,
                'block_number': block_number,
                'cdt_bytes': log_item['_cdt'],
                'owner': Web3.toChecksumAddress(log_item['_owner']),
            }
        else:
            logger.warning(f'Could not find {CDTRegistry.CDT_REGISTRY_EVENT_NAME} event logs for '
                           f'cdt {cdt} at blockNumber {block_number}')
        return result

    def _get_event_filter(self, cdt=None, owner=None, from_block=0, to_block='latest'):
        _filters = {}
        if cdt is not None:
            _filters['_cdt'] = Web3.toBytes(hexstr=cdt)
        if owner is not None:
            _filters['_owner'] = Web3.toBytes(hexstr=owner)

        block_filter = EventFilter(
            CDTRegistry.CDT_REGISTRY_EVENT_NAME,
            getattr(self.events, CDTRegistry.CDT_REGISTRY_EVENT_NAME),
            from_block=from_block,
            to_block=to_block,
            argument_filters=_filters
        )
        return block_filter

