from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import time

from nectar import Steem

from nectarengine.wallet import Wallet

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    stm = Steem()
    stm.wallet.unlock(pwd="wallet_pass")
    wallet = Wallet("nectarbot", steem_instance=stm)
    dragon_token = wallet.get_token("DRAGON")
    if dragon_token is not None and float(dragon_token["balance"]) >= 0.01:
        print("balance %.2f" % float(dragon_token["balance"]))
        print(wallet.transfer("thecrazygm", 0.01, "DRAGON", "test"))
    else:
        print("Could not sent")
    time.sleep(15)
    wallet.refresh()
    dragon_token = wallet.get_token("DRAGON")
    print("new balance %.2f" % float(dragon_token["balance"]))
