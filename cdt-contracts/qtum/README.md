# Qtum部署

## 概览
  介绍如何将CDT contracts部署到Qtum链上

## 环境
以Qtum docker container环境为例
[参考链接](https://book.qtum.site/zh/part1/qtum-docker.html "参考链接")

## 部署合约
在remix中依次对Library.sol,Migrations.sol,CDTRegistry.sol,TaskMarket.sol进行编译，获得对应的bytecodes，之后在容器中执行部署合约
```shell
qtum-cli  createcontract <bytecodes>
```
执行成功返回类似
{
  "txid": "52b3eef0fe0032f685974256972b340655501fc87adec4cffe2b96cc46446001",
  "sender": "qYcH9wHcd86LaDAAxquKPyfpmSraxAbBop",
  "hash160": "a5161fee8ff92457c0829889854888b45255f961",
  "address": "2d4b6564a012ae1383854ac48574c2248660d897"
}





