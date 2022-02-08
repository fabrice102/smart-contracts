# This example is provided for informational purposes only and has not been audited for security.

from pyteal import *


@Subroutine(TealType.uint64)
def isEvenSubRoutine(i):
    return i % Int(2) == Int(0)


def isEvenPyFunc(i):
    return i % Int(2) == Int(0)


progs = {
    "tx-type": Gtxn[0].type_enum() == TxnType.Payment,
    "update-appl": Txn.on_completion() == OnComplete.NoOp,
    "after-feb-2022": Global.latest_timestamp() >= Int(1643691600),
    "atomic-payment": Seq([
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].amount() == Int(2000000)),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        Int(1)
    ]),
    "inner": Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: Int(1420000),
            TxnField.receiver: Txn.sender(),
        }),
        InnerTxnBuilder.Submit(),
        Int(1)
    ]),
    "subroutine": Seq([
        Assert(isEvenSubRoutine(Gtxn[0].amount())),
        Assert(isEvenSubRoutine(Gtxn[1].amount())),
        Int(1)
    ]),
    "pyfunc": Seq([
        Assert(isEvenPyFunc(Gtxn[0].amount())),
        Assert(isEvenPyFunc(Gtxn[1].amount())),
        Int(1)
    ]),
    "appargs": Txn.application_args[2] == Bytes("")
}

if __name__ == "__main__":
    for p in progs:
        print()
        print(f"{p}:")
        print(compileTeal(progs[p], Mode.Application, version=5))
