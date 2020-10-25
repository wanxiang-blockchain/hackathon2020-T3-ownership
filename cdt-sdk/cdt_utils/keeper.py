"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import os

from eth_utils import big_endian_to_int

from contracts.cdtregistry import CDTRegistry
from contracts.taskmarket import TaskMarket

from cdt_utils.generic_contract import GenericContract
from cdt_utils.utils import (add_ethereum_prefix_and_hash_msg, generate_multi_value_hash,
                                split_signature)
from cdt_utils.wallet import Wallet
from cdt_utils.web3.signature import SignatureFix
from cdt_utils.web3_provider import Web3Provider


class Keeper(object):
    """The Keeper class aggregates all contracts in the Ocean Protocol node."""

    DEFAULT_NETWORK_NAME = 'development'
    _network_name_map = {
        1: 'Main',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan'
    }

    def __init__(self, contract_names=None):
        self.network_name = Keeper.get_network_name(Keeper.get_network_id())
        self.accounts = Web3Provider.get_web3().eth.accounts
        self._contract_name_to_instance = {}
        if contract_names:
            for name in contract_names:
                try:
                    contract = GenericContract(name)
                    self._contract_name_to_instance[name] = contract
                    setattr(self, name, contract)
                except (KeyError, Exception):
                    pass

        self.cdt_registry = CDTRegistry.get_instance()
        self.task_market = TaskMarket.get_instance()
        contracts = [
            self.cdt_registry,
            self.task_market
        ]

        self._contract_name_to_instance.update({contract.name: contract
                                                for contract in contracts if contract})

    @staticmethod
    def get_instance(contract_names=None):
        """Return the Keeper instance (singleton)."""
        return Keeper(contract_names)

    @staticmethod
    def get_network_name(network_id):
        """
        Return the keeper network name based on the current ethereum network id.
        Return `development` for every network id that is not mapped.

        :param network_id: Network id, int
        :return: Network name, str
        """
        if os.environ.get('KEEPER_NETWORK_NAME'):
            logging.debug('keeper network name overridden by an environment variable: {}'.format(
                os.environ.get('KEEPER_NETWORK_NAME')))
            return os.environ.get('KEEPER_NETWORK_NAME')

        return Keeper._network_name_map.get(network_id, Keeper.DEFAULT_NETWORK_NAME)

    @staticmethod
    def get_network_id():
        """
        Return the ethereum network id calling the `web3.version.network` method.

        :return: Network id, int
        """
        return int(Web3Provider.get_web3().version.network)

    @staticmethod
    def sign_hash(msg_hash, account):
        """
        This method use `personal_sign`for signing a message. This will always prepend the
        `\x19Ethereum Signed Message:\n32` prefix before signing.

        :param msg_hash:
        :param account: Account
        :return: signature
        """
        wallet = Wallet(Web3Provider.get_web3(), account.key, account.password,
                        account.address)
        s = wallet.sign(msg_hash)
        return s.signature.hex()

    @staticmethod
    def ec_recover(message, signed_message):
        """
        This method does not prepend the message with the prefix `\x19Ethereum Signed Message:\n32`.
        The caller should add the prefix to the msg/hash before calling this if the signature was
        produced for an ethereum-prefixed message.

        :param message:
        :param signed_message:
        :return:
        """
        w3 = Web3Provider.get_web3()
        v, r, s = split_signature(w3, w3.toBytes(hexstr=signed_message))
        signature_object = SignatureFix(vrs=(v, big_endian_to_int(r), big_endian_to_int(s)))
        return w3.eth.account.recoverHash(message, signature=signature_object.to_hex_v_hacked())

    @staticmethod
    def personal_ec_recover(message, signed_message):
        prefixed_hash = add_ethereum_prefix_and_hash_msg(message)
        return Keeper.ec_recover(prefixed_hash, signed_message)

    @staticmethod
    def unlock_account(account):
        """
        Unlock the account.

        :param account: Account
        :return:
        """
        return Web3Provider.get_web3().personal.unlockAccount(account.address, account.password)

    @staticmethod
    def get_ether_balance(address):
        """
        Get balance of an ethereum address.

        :param address: address, bytes32
        :return: balance, int
        """
        return Web3Provider.get_web3().eth.getBalance(address, block_identifier='latest')

    @property
    def contract_name_to_instance(self):
        return self._contract_name_to_instance

    @property
    def contract_names(self):
        return self._contract_name_to_instance.keys()

    def get_contract(self, contract_name):
        contract = self.contract_name_to_instance.get(contract_name)
        if contract:
            return contract

        try:
            return GenericContract(contract_name)
        except Exception as e:
            logging.error(f'Cannot load contract {contract_name}: {e}')
            return None

    def get_contract_by_address(self, contract_address):
        for contract in self._contract_name_to_instance.values():
            if contract.address == contract_address:
                return contract

        return None

    @staticmethod
    def generate_multi_value_hash(types, values):
        return generate_multi_value_hash(types, values)

