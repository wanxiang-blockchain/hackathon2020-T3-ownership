"""Keeper module to call keeper-contracts."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0


from ocean_keeper.contract_base import ContractBase


class GenericContract(ContractBase):
    """Class for instantiating any contract.

    Contract name is set at time of loading the contract.

    """

