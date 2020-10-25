
import logging
from web3 import Web3

from cdt_utils.contract_base import ContractBase

logger = logging.getLogger(__name__)

class TaskMarket(ContractBase):
    """任务市场类"""
    TASK_ADD_EVENT_NAME = 'TaskAdded'
    JOB_ADD_EVENT_NAME = 'JobAdded'
    CONTRACT_NAME = 'TaskMarket'

    def add_task(self, name, desc, account):
        tx_hash = self.send_transaction(
            'addTask',
            (name, desc),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'account_key': account.key}
        )
        
        _filters = dict()
        _filters['_owner'] = Web3.toBytes(hexstr=account.address)
        event = self.subscribe_to_event(self.TASK_ADD_EVENT_NAME, 15, _filters, wait=True)
    
        task_id = 0
        if event is not None:
            task_id = event['args']['_taskId']
        
        return task_id

    def add_job(self, cdt, taskid, account):
        tx_hash = self.send_transaction(
            'addJob',
            (cdt, taskid),
            transact={'from': account.address,
                      'passphrase': account.password,
                      'account_key': account.key}
        )

        _filters = dict()
        _filters['_owner'] = Web3.toBytes(hexstr=account.address)
        event = self.subscribe_to_event(self.JOB_ADD_EVENT_NAME, 15, _filters, wait=True)
    
        job_id = 0
        if event is not None:
            job_id = event['args']['_jobId']
        
        return job_id

    def get_task(self, taskid):
        return self.contract_concise.getTask(taskid)
        
    def get_job(self, jobid):
        return self.contract_concise.getJob(jobid)