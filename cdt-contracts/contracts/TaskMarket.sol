pragma solidity 0.5.6;

import './Library.sol';
/**
 * @title 任务市场主要功能
 * @author lqb
 */
contract TaskMarket {
    
    using CDTLibrary for CDTLibrary.CDTList;    
    using AuthorityLibrary for AuthorityLibrary.AuthorityList;

    CDTLibrary.CDTList internal cdtList;
    AuthorityLibrary.AuthorityList internal authorityList;

    // 任务结构体
    struct Task {
        address owner;
        string name;
        string desc;
        uint status;
        uint[] jobIds;
    }
    
    // 计算结构体，接收算法CDT
    struct Job {
        address owner;
        bytes32 cdt;
        uint status;
    }

    mapping(uint => Task) taskList;
    mapping(uint => Job) jobList;

    uint public taskNum = 0;
    uint public jobNum = 0;
    
    event TaskAdded(
        uint indexed _taskId,
        address indexed _owner,
        string _name,
        string _desc
    );

    event JobAdded(
        uint _taskId,
        uint indexed _jobId,
        address indexed _owner,
        bytes32 indexed _cdt
    );
    
	constructor() public {}
  
    // 创建新任务
    // 暂时省略对机构的检查
    function addTask(
        string memory _name,
        string memory _desc
    )
        public
        returns (uint taskId)
    {
        taskId = taskNum + 1;
        taskNum++;
        taskList[taskId] = Task({
            owner: msg.sender,
            name: _name,
            desc: _desc,
            status: 1,
            jobIds: new uint[](0)
        });

        emit TaskAdded(
            taskId,
            msg.sender,
            _name,
            _desc
        );

        return taskId;
    }
    
    // 创建新计算, 算法CDT在链上存证
    // 暂时省略对CDT所有者的检查
    function addJob(
        bytes32 _cdt,
        uint _taskId
    )
        public
        returns (uint jobId)
    {
        jobId = jobNum + 1;
        jobNum++;
        jobList[jobId] = Job({
            owner: msg.sender,
            cdt: _cdt,
            status: 1
        });

        taskList[_taskId].jobIds.push(jobId);

        emit JobAdded(
            _taskId,
            jobId,
            msg.sender,
            _cdt
        );

        return jobId;
    }
    
    // 获取计算状态
    function getJob(
        uint _jobId
    )
        public
        view
        returns (
            bytes32 cdt,
            uint status
        )
    {
        cdt = jobList[_jobId].cdt;
        status = jobList[_jobId].status;
    }

    // 获取任务状态
    function getTask(
        uint _taskId
    )
        public
        view
        returns (
            uint[] memory jobIds,
            uint status
        )
    {
        jobIds = taskList[_taskId].jobIds;
        status = taskList[_taskId].status;
    }

}