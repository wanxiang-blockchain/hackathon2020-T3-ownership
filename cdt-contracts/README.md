# cdt-contracts

## 概览
  本仓库提供了三个合约功能，包括机构注册、CDT链上授权以及计算任务市场。
  
## 部署

```shell
$ git clone https://github.com/ownership-labs/cdt-contracts
$ cd cdt-contracts
$ ganache-cli
$ truffle migrate --network development
```
  ganache-cli输出的第一个账户为合约管理员，此外还需记录下CDTRegistry和TaskMarket的合约地址
