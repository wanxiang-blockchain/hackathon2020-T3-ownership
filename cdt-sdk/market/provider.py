
from ddo.cdt import CDT, cdt_to_id, checksum, cdt_to_id_bytes
from ddo.ddo import DDO
from ddo.service import Service
from ddo.public_key_base import PUBLIC_KEY_TYPE_RSA
from cdt_utils.utils import add_ethereum_prefix_and_hash_msg

from eth_utils import add_0x_prefix
from web3 import Web3

class Provider(object):
    def __init__(self, keeper, ipfs_client, account):
        self.keeper = keeper
        self.ipfs_client = ipfs_client
        self.account = account
    
    def generate_ddo(self, service_type, service_endpoint=None, child_cdts=None, values=None):
        ddo = DDO()
        ddo.add_service(service_type, service_endpoint, child_cdts, values)
        
        service_dict=ddo.services[0].as_dictionary()
        checksums = dict()
        checksums[str(0)] = checksum(service_dict)
        
        ddo.add_proof(checksums)
        cdt = ddo.assign_cdt(CDT.cdt(ddo.proof['checksum']))

        msg = f'{cdt_to_id_bytes(cdt)}'
        id_hash = add_ethereum_prefix_and_hash_msg(msg)
        ddo.proof['signatureValue'] = self.keeper.sign_hash(id_hash, self.account)
        ddo.add_public_key(cdt, self.account.address)
        ddo.add_authentication(cdt, PUBLIC_KEY_TYPE_RSA)

        return ddo

    def publish_ddo(self, ddo):
        ipfs_path = self.ipfs_client.add(ddo.as_dictionary())

        _id = cdt_to_id(ddo.cdt)
        # 还需调整链上的checksum        
        w3 = Web3
        checksum_test = w3.sha3(text='checksum')
        
        self.keeper.cdt_registry.register(_id, checksum_test, ipfs_path, self.account)

        assert self.keeper.cdt_registry.get_cdt_owner(add_0x_prefix(_id)) == self.account.address
        
        return

    def resolve_ddo(self, cdt):
        cdt_bytes = cdt_to_id_bytes(cdt)
        data = self.keeper.cdt_registry.get_registered_attribute(cdt_bytes)
        if not (data and data.get('value')):
            return None
        ddo_url = data['value']
        ddo_json = self.ipfs_client.get(ddo_url)
        ddo = DDO()
        ddo._read_dict(ddo_json)
        return ddo
    
    def verify_ddo(self, ddo, owner_address):
        service_dict=ddo.services[0].as_dictionary()
        checksums = dict()
        checksums[str(0)] = checksum(service_dict)
        if (checksums != ddo.proof['checksum']) and (CDT.cdt(checksums) != ddo.cdt):
            return False
            
        original_msg = f'{cdt_to_id_bytes(ddo.cdt)}'            
        signature = ddo.proof['signatureValue']
        if not self.verify_signature(owner_address, signature, original_msg):
            return False

        if self.keeper.cdt_registry.get_cdt_owner(cdt_to_id(ddo.cdt)) != owner_address:
            return False

        return True
    
    def verify_signature(self, signer_address, signature, original_msg):
        address = self.keeper.personal_ec_recover(original_msg, signature)
        if address.lower() == signer_address.lower():
            return True
        else:
            return False
    
    def get_leaf_index(self, leaf_cdt, algorithm_ddo):
        index = -1
        for ix, cdt in algorithm_ddo.child_cdts.items():
            if cdt == leaf_cdt:
                index = ix
        return index

