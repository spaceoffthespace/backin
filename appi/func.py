from django.core.management.base import BaseCommand
from web3 import Web3
from appi.models import HotWallet

class Command(BaseCommand):
    help = 'Transfer funds from the latest active hot wallet to Ledger'

    def handle(self, *args, **kwargs):
        w3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
        
        try:
            wallet = HotWallet.objects.filter(is_active=True).latest('created_at')
        except HotWallet.DoesNotExist:
            self.stdout.write(self.style.ERROR('No active wallet found!'))
            return

        hot_wallet_private_key = wallet.private_key
        hot_wallet_address = wallet.address
        ledger_address = '0xa7dD382c1144D4BC85d5d543f66d802210c1DB72'

        balance = w3.eth.getBalance(hot_wallet_address)
        
        gas_price = w3.toWei('20', 'gwei')
        gas_limit = 21000

        if balance - (gas_price * gas_limit) > w3.toWei('0.01', 'ether'):
            transaction = {
                'to': ledger_address,
                'value': balance - (gas_price * gas_limit),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': w3.eth.getTransactionCount(hot_wallet_address)
            }

            signed_txn = w3.eth.account.signTransaction(transaction, hot_wallet_private_key)
            w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            self.stdout.write(self.style.SUCCESS('Successfully sent funds to Ledger!'))
        else:
            self.stdout.write(self.style.WARNING('Not enough balance to send funds.'))
