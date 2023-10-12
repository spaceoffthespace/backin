from celery import shared_task
from .models import HotWallet
from web3 import Web3

@shared_task
def rotate_hot_wallet():
    # Deactivate all hot wallets
    HotWallet.objects.update(is_active=False)

    # Create a new hot wallet
    w3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
    account = w3.eth.account.create()
    HotWallet.objects.create(address=account.address, private_key=account.key.hex(), is_active=True)

    # Additional logic to transfer funds to the ledger from the previous hot wallet, if needed
