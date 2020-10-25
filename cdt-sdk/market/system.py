
class SystemProvider:

    def __init__(self, keeper, system_account):
        self.keeper = keeper
        self.system_account = system_account

    def register_authority(self, address, name):

        if not self.keeper.cdt_registry.is_authority(address):
            self.keeper.cdt_registry.add_authority(address, name, self.system_account)
            assert self.keeper.cdt_registry.is_authority(address)

        return