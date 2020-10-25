pragma solidity 0.5.6;

import './Library.sol';
/**
 * @title CDT主要功能
 * @author lqb
 */
contract CDTRegistry {
    
    // CDT注册表状态存储
    using CDTLibrary for CDTLibrary.CDTList;    
    // 机构注册表状态存储, 只有机构可以添加CDT
    using AuthorityLibrary for AuthorityLibrary.AuthorityList;

    CDTLibrary.CDTList internal cdtList;
    AuthorityLibrary.AuthorityList internal authorityList;
    
    // CDT->授权CDT->是否具有权限
    mapping(bytes32 => mapping(bytes32 => bool)) CDTPermissions;
    
    // 只有管理员可以增加机构
    mapping(address => bool) private isAdmin;
    
    // _value并不存储在链上，而是记录在事件日志, 例如ddo的ipfs_path
    event CDTAttributeRegistered(
        bytes32 indexed _cdt,
        address indexed _owner,
        bytes32 indexed _checksum,
        string _value,
        address _lastUpdatedBy,
        uint256 _blockNumberUpdated
    );
    
    event CDTPermissionGranted(
        bytes32 indexed _cdt,
        address indexed _owner,
        bytes32 indexed _grantee
    );

    event AuthorityAdded(
        address indexed _member,
        string indexed _name
    );
    
    // 只有管理员可以进行相应的操作
    modifier onlyAdmin()
    {
        require(
            isAdmin[msg.sender] == true
        );
        _;
    }
    
    // 只有注册机构可以进行相应的操作
    modifier onlyAuthority()
    {
        require(
           authorityList.authorities[msg.sender].isAuthority == true
        );
        _;
    }
    
    // 只有CDT拥有者可以进行相应的操作
    modifier onlyCDTOwner(bytes32 _cdt)
    {
        require(
            msg.sender == cdtList.cdts[_cdt].owner
        );
        _;
    }

	constructor() public {
		isAdmin[msg.sender] = true;
	}
    
    // 添加新的机构，只有系统管理员可以进行该操作
    function addAuthority(
        address _member,
        string memory _name
    )
        onlyAdmin()
        public
        returns (uint size)
    {
        require(
            authorityList.authorities[_member].isAuthority == false &&
            _member != address(0)
        );

        uint updatedSize = authorityList.update(_member, _name);

        emit AuthorityAdded(
            _member,
            _name
        );

        return updatedSize;

    }
    
    // 注册/更新CDT
    function registerAttribute(
        bytes32 _cdt,
        bytes32 _checksum,
        string memory _value
    )
        onlyAuthority()
        public
        returns (uint size)
    {
        require(
            cdtList.cdts[_cdt].owner == address(0x0) ||
            cdtList.cdts[_cdt].owner == msg.sender
        );

        uint updatedSize = cdtList.update(_cdt, _checksum);

        emit CDTAttributeRegistered(
            _cdt,
            cdtList.cdts[_cdt].owner,
            _checksum,
            _value,
            msg.sender,
            block.number
        );

        return updatedSize;
    }
    
    // 将cdt授权给另一地址，只有cdt拥有者可以进行该操作
    function grantPermission(
        bytes32 _cdt,
        bytes32 _grantee
    )
        external
        onlyCDTOwner(_cdt)
    {
        CDTPermissions[_cdt][_grantee] = true;
        emit CDTPermissionGranted(
            _cdt,
            msg.sender,
            _grantee
        );
    }
    
    // 判断某地址是否得到该cdt的授权
    function getPermission(
        bytes32 _cdt,
        bytes32 _grantee
    )
        external
        view
        returns(bool)
    {
        return CDTPermissions[_cdt][_grantee];
    }
    
    // 获取某一cdt的结构体记录
    function getCDTRegister(
        bytes32 _cdt
    )
        public
        view
        returns (
            address owner,
            bytes32 lastChecksum,
            address lastUpdatedBy,
            uint256 blockNumberUpdated
        )
    {
        owner = cdtList.cdts[_cdt].owner;
        lastChecksum = cdtList.cdts[_cdt].lastChecksum;
        lastUpdatedBy = cdtList.cdts[_cdt].lastUpdatedBy;
        blockNumberUpdated = cdtList.cdts[_cdt].blockNumberUpdated;
    }
    
    // 获取某一cdt的所有者地址
    function getCDTOwner(bytes32 _cdt)
        public
        view
        returns (address CDTOwner)
    {
        return cdtList.cdts[_cdt].owner;
    }
    
    // 获取某一cdt的注册/更新时间
    function getBlockNumberUpdated(bytes32 _cdt)
        public
        view
        returns (uint256 blockNumberUpdated)
    {
        return cdtList.cdts[_cdt].blockNumberUpdated;
    }

    // 判断是否是权威机构
    function isAuthority(
        address _member
    )
        public
        view
        returns (bool)
    {
        return authorityList.authorities[_member].isAuthority;
    }
    
}