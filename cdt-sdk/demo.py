"""Demo"""
#  Copyright lqb ownership-labs

import os
from cdt_utils.contract_handler import ContractHandler
from cdt_utils.keeper import Keeper
from cdt_utils.web3_provider import Web3Provider
from cdt_utils.utils import get_account, add_ethereum_prefix_and_hash_msg

from market.ipfs import IPFSProvider
from market.system import SystemProvider
from market.dataset import DataProvider
from market.computation import ComputaProvider
from market.algorithm import AlgorithmProvider

# 生成链下ddo, 发布到ipfs存储，并在链上注册资源标识符(可组合数据通证CDT)
def simulate_ddo(provider, service_type, service_endpoint, child_cdts, values):
    ddo = provider.generate_ddo(service_type, service_endpoint, child_cdts, values)
    provider.publish_ddo(ddo)
    # print(provider.resolve_ddo(ddo.cdt).as_dictionary())
    return ddo

def import_env():
    if os.path.exists('.env'):
        print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            key, value = var[0].strip(), var[1].strip()
            os.environ[key] = value

if __name__ == "__main__":
    # 合约地址、abi路径设置
    import_env()
    artifacts_path = os.getenv('ARTIFACTS_PATH')
    cdt_registry_address = os.getenv('CDT_REGISTRY_ADDRESS')
    task_market_address = os.getenv('TASK_MARKET_ADDRESS')

    Web3Provider.init_web3('http://localhost:8545')
    ContractHandler.set_artifacts_path(os.path.expanduser(artifacts_path))
    ContractHandler.set_contract_address(cdt_registry_address, task_market_address)
    keeper = Keeper.get_instance()

    # 通过环境变量获取三个以太坊账户, ganache-cli的第一个账户为合约部署的系统账户
    account1 = get_account(0)
    account2 = get_account(1)
    account3 = get_account(2)
    system_account = account1

    # 下面以两家企业的联合建模为例，第三方科技公司提供模型并发起任务
    # data_provider1在企业1的私域，将数据秘密共享后传给企业1、2的联邦域computa_provider1、2
    ipfs_client = IPFSProvider()
    system_provider = SystemProvider(keeper, system_account)
    data_provider1 = DataProvider(keeper, ipfs_client, account1)
    data_provider2 = DataProvider(keeper, ipfs_client, account2)
    computa_provider1 = ComputaProvider(keeper, ipfs_client, account1)
    computa_provider2 = ComputaProvider(keeper, ipfs_client, account2)
    algorithm_provider = AlgorithmProvider(keeper, ipfs_client, account3)
    
    # 通过管理员注册机构
    system_provider.register_authority(account1.address, 'bank1')
    system_provider.register_authority(account2.address, 'bank2')
    system_provider.register_authority(account3.address, 'fintech')
    
    # 数据集的元信息
    service_type='dataset'
    service_endpoint='ip:port'
    child_cdts=None
    values={"attributes":{"name":"test_data", "price":10, "tags":"test","description":"test"}}
    
    # 数据集1和数据集2, +'test'是为了确保两个CDT标识符不同
    dataset_ddo1 = simulate_ddo(data_provider1, service_type, service_endpoint, child_cdts, values)
    dataset_ddo2 = simulate_ddo(data_provider2, service_type, service_endpoint+'test', child_cdts, values)
    
    # 计算力的元信息
    service_type='computation'
    service_endpoint='ip:port'
    child_cdts=None
    values={"attributes":{"name":"test_computa", "price":10, "tags":"test","description":"test"}}

    # 算力1和算力2
    computa_ddo1 = simulate_ddo(computa_provider1, service_type, service_endpoint, child_cdts, values)
    computa_ddo2 = simulate_ddo(computa_provider2, service_type, service_endpoint+'test', child_cdts, values)
    
    # 算法的元信息
    # hash1和hash为数据秘密共享操作的代码哈希值，hash3和hash4为在shares上的MPC运算的代码哈希值
    service_type = 'algorithm'
    service_endpoint = 'ip:port'
    child_cdts = {0:dataset_ddo1.cdt, 1: dataset_ddo2.cdt, 2: computa_ddo1.cdt, 3: computa_ddo2.cdt}
    code_proofs = {0:"hash1", 1:"hash2", 2:"hash3", 3:"hash4"}
    values={"attributes":{"name":"algorithm", "description":"test", "code_proofs": code_proofs}}
    
    # 算法
    algorithm_ddo = simulate_ddo(algorithm_provider, service_type, service_endpoint, child_cdts, values)
    print(algorithm_ddo.as_dictionary())
    
    # 各数据方和各算力方对算法进行验证，判断其符合自己的资源使用条款后，对其授权, 以数据源1为例
    data_provider1.check_service_agreements(dataset_ddo1, algorithm_ddo, account3.address)
    data_provider1.grant_permission(dataset_ddo1.cdt, algorithm_ddo.cdt)

    # 任务方/算法方在链上新建task，并将算法CDT添加到未完成的job列表中
    task_name = 'privateAI'
    task_desc = 'federated learnig for bank1 and bank2'
    task_id = algorithm_provider.add_task(task_name, task_desc)
    job_id = algorithm_provider.add_job(task_id, algorithm_ddo.cdt)

    # 任务方/算法方对数据/算力进行远程访问，需要发送自己的签名
    msg = f'{account3.address}{job_id}'
    job_id_hash = add_ethereum_prefix_and_hash_msg(msg)
    signature = keeper.sign_hash(job_id_hash, account3)

    # 数据源方接受远程访问请求，判断计算操作的有效性，验证通过后，执行本地计算
    if data_provider1.verify_remote_access(job_id, dataset_ddo1, algorithm_ddo, account3.address, signature):
        data_provider1.start_remote_compute(dataset_ddo1, algorithm_ddo)
