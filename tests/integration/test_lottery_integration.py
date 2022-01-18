from brownie import network
import pytest
import time

from scripts.deploy import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
)


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # arrange
    lottery = deploy_lottery()
    account = get_account()
    entrance_fee = lottery.getEntranceFee() + 333_333_333
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": entrance_fee})
    lottery.enter({"from": account, "value": entrance_fee})
    fund_with_link(lottery)

    # act
    lottery.endLottery({"from": account})
    time.sleep(180)

    # assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
