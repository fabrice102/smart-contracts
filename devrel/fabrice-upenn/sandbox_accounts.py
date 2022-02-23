from algosdk.kmd import KMDClient

KMD_ADDRESS = "http://localhost:4002"
KMD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

KMD_WALLET_NAME = "unencrypted-default-wallet"
KMD_WALLET_PASSWORD = ""


class Account:
    def __init__(self, private_key: str, address: str):
        self.private_key = private_key
        self.address = address


def get_accounts():
    kmd = KMDClient(KMD_TOKEN, KMD_ADDRESS)
    wallets = kmd.list_wallets()

    wallet_id = None
    for wallet in wallets:
        if wallet["name"] == KMD_WALLET_NAME:
            wallet_id = wallet["id"]
            break

    if wallet_id is None:
        raise Exception("Wallet not found: {}".format(KMD_WALLET_NAME))

    wallet_handle = kmd.init_wallet_handle(wallet_id, KMD_WALLET_PASSWORD)

    try:
        addresses = kmd.list_keys(wallet_handle)
        kmd_accounts = [
            Account(
                private_key=kmd.export_key(wallet_handle, KMD_WALLET_PASSWORD, addr),
                address=addr
            )
            for addr in addresses
        ]
    finally:
        kmd.release_wallet_handle(wallet_handle)

    return kmd_accounts


if __name__ == "__main__":
    # If called directly, print the list of accounts
    accounts = get_accounts()
    for account in accounts:
        print(account.address)