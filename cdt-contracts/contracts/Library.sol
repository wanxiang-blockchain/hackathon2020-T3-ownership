pragma solidity 0.5.6;

/*
CDT库函数，维护storage
*/
library CDTLibrary {

    struct CDT {
        address owner;
        bytes32 lastChecksum;
        address lastUpdatedBy;
        uint256 blockNumberUpdated;
    }

    struct CDTList {
        mapping(bytes32 => CDT) cdts;
        bytes32[] cdtIds;
    }
    
    // 注册或更新某一cdt的结构体记录
    function update(
        CDTList storage _self,
        bytes32 _cdt,
        bytes32 _checksum
    )
        external
        returns (uint size)
    {
        address cdtOwner = _self.cdts[_cdt].owner;

        if (cdtOwner == address(0)) {
            cdtOwner = msg.sender;
            _self.cdtIds.push(_cdt);
        }

        _self.cdts[_cdt] = CDT({
            owner: cdtOwner,
            lastChecksum: _checksum,
            lastUpdatedBy: msg.sender,
            blockNumberUpdated: block.number
        });

        return _self.cdtIds.length;
    }
}

/*
机构库函数，维护storage
*/
library AuthorityLibrary {

    struct Authority {
        address owner;
        string name;
        bool isAuthority;
    }

    struct AuthorityList {
        mapping(address => Authority) authorities;
        address[] members;
    }
    
    // 添加或更新某一组织成员
    function update(
        AuthorityList storage _self,
        address member,
        string calldata name
    )
        external
        returns (uint size)
    {
        if (_self.authorities[member].owner == address(0)) {
            _self.members.push(member);
        }

        _self.authorities[member] = Authority({
            owner: member,
            name: name,
            isAuthority: true
        });

        return _self.members.length;
    }
}
