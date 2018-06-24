pragma solidity ^0.4.24;

contract MarriageContract {

    address public creator;
    mapping(address => bool) public members;

    share_medical_records_type public share_medical_records = share_medical_records_val;
    sexual_fidelity_type public sexual_fidelity  = sexual_fidelity_val;
    relationship_duration_months_type public relationship_duration_months = relationship_duration_months_val;
    support_each_other_type public support_each_other = support_each_other_val;

    constructor() public {
        creator = msg.sender;
    }

    modifier onlyCreator() {
        require(msg.sender == creator);
        _;
    }

    modifier onlySpouse() {
        require(members[msg.sender]);
        _;
    }

    function addSpouse(address _toAdd) onlyCreator public {
        require(_toAdd != 0);
        members[_toAdd] = true;
    }

}