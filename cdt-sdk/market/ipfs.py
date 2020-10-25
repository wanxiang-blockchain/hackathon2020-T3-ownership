
from urllib.parse import urljoin
from rfc3986 import urlparse
import ipfsapi

class IPFSProvider:

    def __init__(self):
        ipfs_rpc_endpoint = "https://ipfs.singularitynet.io:80"
        ipfs_rpc_endpoint = urlparse(ipfs_rpc_endpoint)
        ipfs_scheme = ipfs_rpc_endpoint.scheme if ipfs_rpc_endpoint.scheme else "http"
        ipfs_port = ipfs_rpc_endpoint.port if ipfs_rpc_endpoint.port else 5001
        
        self.ipfs_client = ipfsapi.connect(urljoin(ipfs_scheme, ipfs_rpc_endpoint.hostname), ipfs_port, session=True)

    def add(self, json):
        hash = self.ipfs_client.add_json(json)
        return hash

    def get(self, hash):
        return self.ipfs_client.get_json(hash)
        
    def close(self):
        self.ipfs_client.close()