
from market.provider import Provider
from ddo.cdt import cdt_to_id, cdt_to_id_bytes

class DataProvider(Provider):

    def __init__(self, keeper, ipfs_client, account):
        
        self.keeper = keeper
        self.ipfs_client = ipfs_client
        self.account = account

        super(DataProvider, self).__init__(keeper,ipfs_client,account)

    def check_service_agreements(self, dataset_ddo, algorithm_ddo, consumer_address):
        if not self.verify_ddo(algorithm_ddo, consumer_address):
            return False
        # check conditions and terms
        return True

    def grant_permission(self, dataset_cdt, consumer_cdt):
        _id = cdt_to_id(dataset_cdt)
        _consumer_id = cdt_to_id(consumer_cdt)
        self.keeper.cdt_registry.grant_permission(_id, _consumer_id, self.account)
        assert self.keeper.cdt_registry.get_permission(_id, _consumer_id)

    def verify_remote_access(self, job_id, leaf_ddo, algorithm_ddo, consumer_address, signature):
    
        # 判断该cdt是算法cdt
        if algorithm_ddo.services[0].type != 'algorithm':
            return False

        # 判断该算法cdt的有效性，涉及服务、证明、资源标识符和拥有者
        if not self.verify_ddo(algorithm_ddo, consumer_address):
            return False
        
        # 判断签名的有效性
        original_msg = f'{consumer_address}{job_id}'
        if not self.verify_signature(consumer_address, signature, original_msg):
            return False

        # 判断该远程计算已在链上存证
        if cdt_to_id_bytes(algorithm_ddo.cdt) != self.keeper.task_market.get_job(job_id)[0]:
            return False

        # 判断该算法cdt使用到了leaf_cdt资源
        if self.get_leaf_index(leaf_ddo.cdt, algorithm_ddo) < 0:
            return False

        # 判断该算法cdt是否具有操作leaf_cdt资源的权限
        _id = cdt_to_id(leaf_ddo.cdt)
        _granted = cdt_to_id(algorithm_ddo.cdt)
        if not self.keeper.cdt_registry.get_permission(_id, _granted):
            return False

        return True

    def start_remote_compute(self, leaf_ddo, algorithm_ddo):
        # 从算法提供方处获取跟leaf_ddo.cdt相关的代码
        service_endpoint = algorithm_ddo.services[0].service_endpoint
        # code = ...

        # 验证代码哈希是否匹配
        index = self.get_leaf_index(leaf_ddo.cdt, algorithm_ddo)
        codeproof = algorithm_ddo.services[0].attributes['code_proofs'][index]

        # 开始执行实际计算
        # if hash(code) == codeproof:
        # ... e.g., federated learning

        print('successful')
        return True