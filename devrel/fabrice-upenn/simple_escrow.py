import os

from pyteal import *


def app():
    is_creator = Txn.sender() == Global.creator_address()

    handle_payme = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: Int(2100000),  # = 2.1 Algos
            TxnField.receiver: Txn.sender()
        }),
        InnerTxnBuilder.Submit(),
        Log(Bytes("sent 2.1 Algos")),
        Approve()
    )

    return Cond(
        # Allow creation and do nothing
        [Txn.application_id() == Int(0), Approve()],  # Approve() is the same as Return(1)
        # Allow deletion / update only if called by creator
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        # Disallow opt-in / close-out as no local state is used
        [Txn.on_completion() == OnComplete.OptIn, Reject()],  # Reject() is the same as Return(0)
        [Txn.on_completion() == OnComplete.CloseOut, Reject()],
        # Handle the only (noop) method: "payme"
        [Txn.application_args[0] == Bytes("payme"), handle_payme]
    )


def write_teal_file():
    path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path, "simple_escrow.teal"), "w") as f:
        f.write(compileTeal(app(), mode=Mode.Application, version=5))


if __name__ == '__main__':
    write_teal_file()
