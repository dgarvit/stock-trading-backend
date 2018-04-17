pragma solidity ^0.4.18;

contract Trade {
  address public owner;
  mapping (bytes32 => uint) public balance;
  mapping (bytes32 => address) public buyer;
  mapping (bytes32 => address) public seller;
  mapping (bytes32 => bool) private buyerOk;
  mapping (bytes32 => bool) private sellerOk;
  mapping (bytes32 => bool) public done;
  mapping (bytes32 => uint) public start;

  function Trade() public {
    owner = msg.sender;
  }

  modifier restricted() {
    if (msg.sender == owner) _;
  }

  function createNewTrade(bytes32 id, address _buyer, address _seller) public payable {
    balance[id] = msg.value;
    buyer[id] = _buyer;
    seller[id] = _seller;
    start[id] = now;
  }

  function accept(bytes32 id) public {
    require (!done[id]);

    if (msg.sender == buyer[id])
      buyerOk[id] = true;
    else if (msg.sender == seller[id])
      sellerOk[id] = true;

    if (buyerOk[id] && sellerOk[id])
      payBalance(id);
    else if (buyerOk[id] && !sellerOk[id] && now > start[id] + 30 days) {
      buyer[id].transfer(balance[id]);
      balance[id] = 0;
      done[id] = true;
    }
  }

  function payBalance(bytes32 id) private {
    require (!done[id]);

    owner.transfer(balance[id] / 10);
    seller[id].transfer(balance[id] - balance[id] / 10);
    balance[id] = 0;
    done[id] = true;
  }

  function cancel(bytes32 id) public {
    require (!done[id]);

    if (msg.sender == buyer[id])
      buyerOk[id] = false;
    else if (msg.sender == seller[id])
      sellerOk[id] = false;

    if (!buyerOk[id] && !sellerOk[id]) {
      buyer[id].transfer(balance[id]);
      balance[id] = 0;
      done[id] = true;
    }
  }

  function killTxn(bytes32 id) public restricted {
    require (!done[id]);
    buyer[id].transfer(balance[id]);
    balance[id] = 0;
    done[id] = true;
  }
}
