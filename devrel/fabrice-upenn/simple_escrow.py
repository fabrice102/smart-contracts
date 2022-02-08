import os

from pyteal import *


def app():
    is_creator = Txn.sender() == Global.creator_address()

    handle_noop = Seq(
        Assert(Txn.application_args[0] == Bytes("payme")),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: Int(2100000),   # = 0.21 Algos
            TxnField.receiver: Txn.sender()
        }),
        InnerTxnBuilder.Submit(),
        Log(Bytes("sent 0.21 Algos")),
        Approve()
    )

    return Cond(
        [Txn.application_id() == Int(0), Approve()],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )


def write_teal_file():
    path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(path, "simple_escrow.teal"), "w") as f:
        f.write(compileTeal(app(), mode=Mode.Application, version=5))


if __name__ == '__main__':
    write_teal_file()