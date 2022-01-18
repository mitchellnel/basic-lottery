from operator import length_hint
from brownie import accounts, config, network, Contract, interface
from brownie import MockV3Aggregator, VRFCoordinatorMock, LinkToken
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

# for MockV3Aggregator
DECIMALS = 8
STARTING_PRICE = 2 * (10 ** 8)

CONTRACT_TO_MOCK = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_account(index=None, id=None):
    if index is not None:
        return accounts[index]
    elif id is not None:
        return accounts.load(id)
    elif (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """Returns the contract address from the Brownie config if it is defined.
    Otherwise, it will deploy a mock version of the contract, and return the address of that
        mock contract.

    Keyword arguments:
    contract_name -- the name of the contract we are looking to interact with
    """
    contract_type = CONTRACT_TO_MOCK[contract_name]

    # do we need to deploy a mock?
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        # use address and ABI to create contract object
        contract_address = config["networks"][network.show_active()][
            contract_name + "_address"
        ]

        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks():
    account = get_account()
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks ...")
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": get_account()})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("... Done!\n")


def fund_with_link(contract_address, account=None, link_token=None, amount=1):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")

    amount_as_wei = amount * (10 ** 18)

    print(f"Funding {account.address} with {amount} LINK ...")
    # transaction = link_token.transfer(contract_address, amount_as_wei, {"from": account})
    link_token_contract = interface.LinkTokenInterface(link_token.address)
    transaction = link_token_contract.transfer(
        contract_address, amount_as_wei, {"from": account}
    )
    transaction.wait(1)
    print("... Done!\n")
