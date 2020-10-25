const Registry = artifacts.require("CDTRegistry");
const TaskMarket = artifacts.require("TaskMarket");
const CDTLibrary = artifacts.require("CDTLibrary");
const AuthorityLibrary = artifacts.require("AuthorityLibrary");

module.exports = function(deployer) {
  deployer.deploy(CDTLibrary)
  deployer.deploy(AuthorityLibrary)
  deployer.link(CDTLibrary, Registry);
  deployer.link(AuthorityLibrary, Registry);
  deployer.link(CDTLibrary, TaskMarket);
  deployer.link(AuthorityLibrary, TaskMarket);
  deployer.deploy(Registry);
  deployer.deploy(TaskMarket);
};