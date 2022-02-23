import base64
import os

from algosdk import *
from algosdk.logic import get_application_address
from algosdk.future.transaction import *
from algosdk.v2client import algod
from algosdk.v2client.models import DryrunRequest, DryrunSource

from sandbox_accounts import get_accounts
import simple_escrow

token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
url = "http://localhost:4001"

client = algod.AlgodClient(token, url)


def demo():
    # List of 3 accounts from sandbox
    # Alice = accounts[0]
    # Bob = accounts[1]
    accounts = get_accounts()

    print(f"Alice's account: {accounts[0].address}")
    print(f"Bob's account:   {accounts[1].address}")
    print()

    # Create application
    print(f"Creating simple escrow app using Alice's account...")
    app_id = create_app(accounts[0].address, accounts[0].private_key)
    app_address = get_application_address(app_id)
    print(f"  App created with id:            {app_id}")
    print(f"  Associated application account: {app_address}")
    print()

    sp = client.suggested_params()

    # Print balances
    print_balance("Application Account", app_address)
    print()

    # Fund the application account
    print(f"Funding the application account from Alice's account")
    unsigned_txn = PaymentTxn(
        sender=accounts[0].address,  # Alice's address
        sp=sp,
        receiver=app_address,
        amt=10000000  # 10 Algos
    )
    signed_txn = unsigned_txn.sign(accounts[0].private_key)
    send_txn(signed_txn)

    print()

    # Print balances
    print_balance("Application Account", app_address)
    print_balance("Bob", accounts[1].address)

    print()

    # Call the application with arguments "payme"
    print(f"Calling the application with arguments \"payme\" from Bob's account")
    unsigned_txn = ApplicationNoOpTxn(
        sender=accounts[1].address,  # Bob's address
        sp=sp,
        index=app_id,
        app_args=["payme"]
    )
    signed_txn = unsigned_txn.sign(accounts[1].private_key)
    # (optional) Simulate transaction and store dryrun for debugging
    # (use simple_escrow_debug.sh to debug)
    write_dryrun([signed_txn], app_id,
                 [accounts[1].address, app_address])
    send_txn(signed_txn, with_logs=True)

    print()

    # Print balances
    print_balance("Application Account", app_address)
    print_balance("Bob", accounts[1].address)

    print()

    # Delete application
    print(f"Delete application...")
    unsigned_txn = ApplicationDeleteTxn(
        sender=accounts[0].address,  # Alice's address
        sp=sp,
        index=app_id
    )
    signed_txn = unsigned_txn.sign(accounts[0].private_key)
    send_txn(signed_txn)


def print_balance(name: str, address: str) -> None:
    """
    Print the balance of an account
    :param name: name of the account to display
    :param address: address of the account
    """
    acct_info = client.account_info(address)
    algos = acct_info["amount"] / 1000000
    print(f"Balance of {name:20s}: {algos:.3f} Algos")


def create_app(address: str, private_key: str) -> int:
    """
    Create an application and returns its ID
    :param address: address of the creator
    :param private_key: private key of the creator
    :return:
    """
    # Get suggested params from network 
    sp = client.suggested_params()

    path = os.path.dirname(os.path.abspath(__file__))

    # Generate simple_escrow.teal from simple_escrow.py PyTeal
    simple_escrow.write_teal_file()

    # Read in approval teal source && compile
    with open(os.path.join(path, 'simple_escrow.teal')) as f:
        approval = f.read()
    app_result = client.compile(approval)
    app_bytes = base64.b64decode(app_result['result'])

    # Read in clear teal source && compile
    with open(os.path.join(path, 'clear.teal')) as f:
        clear = f.read()
    clear_result = client.compile(clear)
    clear_bytes = base64.b64decode(clear_result['result'])

    # We dont need no stinkin storage
    schema = StateSchema(0, 0)

    # Create the transaction
    create_txn = ApplicationCreateTxn(address, sp, 0, app_bytes, clear_bytes, schema, schema)

    # Sign it
    signed_txn = create_txn.sign(private_key)

    # Wait for the result so we can return the app id
    result = send_txn(signed_txn)

    return result['application-index']


def send_txn(signed_txn: SignedTransaction, with_logs=False):
    """
    Send a signed transaction to the blockchain
    and displays when sent and when confirmed
    :param signed_txn: signed transaction to send
    :param with_logs: print logs
    :return: result of waiting for confirmation
    """
    txid = client.send_transaction(signed_txn)
    print("  Sending transaction with txID: {}...".format(txid))

    result = wait_for_confirmation(client, txid, 4)
    print("  Transaction confirmed in round: {}".format(result['confirmed-round']))

    if with_logs:
        print("  Logs: ")
        for log in result['logs']:
            print("    {}".format(base64.b64decode(log).decode('utf-8')))

    return result


def write_dryrun(signed_txns: List[SignedTransaction], app_id: int, addrs: List[str]) -> None:
    """
    Make a dryrun of the transaction signed_txn
    Assumes the source of the approval file is simple_escrow.teal
    :param signed_txns: group of transactions to dryrun
    :param app_id: application ID associated
    :param addrs: account addresses used
    """
    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval teal source
    with open(os.path.join(path, 'simple_escrow.teal')) as f:
        app_src = f.read()

    # Add source
    sources = [
        DryrunSource(
            app_index=app_id,
            field_name="approv",
            source=app_src
        ),
    ]

    # Get account info
    accounts = [client.account_info(a) for a in addrs]
    # Get app info
    app = client.application_info(app_id)

    # Create request
    drr = DryrunRequest(
        txns=signed_txns,
        sources=sources,
        apps=[app],
        accounts=accounts
    )

    file_path = os.path.join(path, "dryrun.msgp")
    data = encoding.msgpack_encode(drr)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(data))

    print("  Created dryrun file at {}".format(file_path))


if __name__ == "__main__":
    demo()
