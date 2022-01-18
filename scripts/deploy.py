from brownie import config, network
from brownie import Lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    fund_with_link,
)
from web3 import Web3
import time


def deploy_lottery():
    account = get_account()

    print("Deploying Lottery contract ...")
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    print(f"... Done! Contract deployed to {lottery.address}\n")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]

    print("Starting the Lottery ...")
    start_transaction = lottery.startLottery({"from": account})
    start_transaction.wait(1)
    print("... Done! Lottery has started!\n")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 333_333_333

    print(f"Entering the lottery as {account.address} ...")
    enter_transaction = lottery.enter({"from": account, "value": value})
    enter_transaction.wait(1)
    print(f"... Done! {account.address} has entered the Lottery!\n")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    # fund the contract with LINK
    fund_with_link(lottery.address)

    # end the lottery
    print("Ending the lottery ...")
    end_transaction = lottery.endLottery({"from": account})
    end_transaction.wait(1)
    time.sleep(180)
    print("... Done! Lottery has ended.")
    print(f"{lottery.recentWinner()} is the new winner!!!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
