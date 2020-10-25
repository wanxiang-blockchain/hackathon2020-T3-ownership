
from market.provider import Provider
from ddo.cdt import cdt_to_id, cdt_to_id_bytes
from eth_utils import remove_0x_prefix

class AlgorithmProvider(Provider):

    def __init__(self, keeper, ipfs_client, account):
        
        self.keeper = keeper
        self.ipfs_client = ipfs_client
        self.account = account

        super(AlgorithmProvider, self).__init__(keeper,ipfs_client,account)
        
    def fetch_code(self, leaf_ddo, algorithm_ddo):
        # get remote operation codes
        return

    def add_task(self, name, desc):
        task_id = self.keeper.task_market.add_task(name, desc, self.account)
        return task_id

    def add_job(self, taskid, algorithm_cdt):
        _id = cdt_to_id(algorithm_cdt)
        job_id = self.keeper.task_market.add_job(_id, taskid, self.account)
        assert cdt_to_id_bytes(algorithm_cdt) == self.keeper.task_market.get_job(job_id)[0]
        return job_id
                
