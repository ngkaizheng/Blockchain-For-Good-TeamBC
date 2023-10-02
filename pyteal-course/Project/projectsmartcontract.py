from pyteal import *
from pyteal.ast import txn
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction

def approval_program():
    # Define global state variables
    handle_creation = Seq([
        App.globalPut(Bytes("TargetFund"), Btoi(Txn.application_args[0])),
        App.globalPut(Bytes("TotalFund"), Int(0)),
        App.globalPut(Bytes("Receiver"), Txn.application_args[1]),
        App.globalPut(Bytes("StartDate"), Global.latest_timestamp()),
        App.globalPut(Bytes("EndDate"), Global.latest_timestamp() + Btoi(Txn.application_args[2])),
        App.globalPut(Bytes("EventProgress"), Int(0)),
        # EventProgress 0 = Event Ongoing
        # EventProgress 1 = Event Ended
        # EventProgress 2 = Fund Claimed
        Return(Int(1))
    ])
    
    # Load global state variables into local variables
    TargetFund = App.globalGet(Bytes("TargetFund"))
    TotalFund = App.globalGet(Bytes("TotalFund"))
    StartDate = App.globalGet(Bytes("StartDate"))
    EndDate = App.globalGet(Bytes("EndDate"))
    Creator = App.globalGet(Bytes("Creator"))
    EventProgress = App.globalGet(Bytes("EventProgress"))
    Receiver = App.globalGet(Bytes("Receiver"))

    handle_optin = Return(Int(1))
    handle_closeout = Return(Int(0))
    handle_updateapp = Return(Int(0))
    handle_deleteapp = Return(Int(0))
    scratchCount = ScratchVar(TealType.uint64)
    localCount = ScratchVar(TealType.uint64)

    # Define the logic to end the event and transfer funds when the target is reached
    end_event = Seq([
        Assert(EventProgress == Int(0)),  # Ensure event is ongoing
        scratchCount.store(App.globalGet(Bytes("EventProgress"))),
        App.globalPut(Bytes("EventProgress"), scratchCount.load() + Int(1)),

        Return(Int(1))
    ])

    make_donation = Seq(
        Assert(EventProgress == Int(0)),  # Ensure event is ongoing
        Assert((Global.latest_timestamp() >= StartDate) & (Global.latest_timestamp() <= EndDate)), # Check if the donation is within the event time frame
        scratchCount.store(App.globalGet(Bytes("TotalFund"))),  # Get the current fund
        App.globalPut(Bytes("TotalFund"), scratchCount.load() + Btoi(Txn.application_args[1])),  # Update the current fund in global storage
        localCount.store(App.localGet(Txn.sender(), Bytes("DonationMade"))),
        #Check is new giver or exisitng giver
        If(localCount.load() != Int(0) ).Then(
            App.localPut(Txn.sender(), Bytes("DonationMade"), localCount.load() + Btoi(Txn.application_args[1])),
        ).Else(
            App.localPut(Txn.sender(), Bytes("DonationMade"), Btoi(Txn.application_args[1])),
        ),
        # Check if the target fund has been reached and end the event if true
        If(TotalFund == TargetFund).Then( 
            end_event
        ),  
        Return(Int(1))  # Return success
    )

    claim = Seq(
        # Check if the sender is the receiver
        Assert(Txn.sender() == Receiver),
        # Check if the event has ended or the target fund has been reached
        Assert((Global.latest_timestamp() >= EndDate) | (TotalFund == TargetFund)),
        # Check if the event is in the "Event Ended" state
        Assert(EventProgress == Int(1)),
        scratchCount.store(App.globalGet(Bytes("EventProgress"))),
        App.globalPut(Bytes("EventProgress"), scratchCount.load() + Int(1)),
        scratchCount.store(App.globalGet(Bytes("TotalFund"))),  # Get the current fund
        # Transfer funds to the receiver's account using Inner Transcation
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Receiver,
                # In testnet, TxnFideld.fee are same 1000, There's why - Int(1000)
                TxnField.amount: App.globalGet(Bytes("TargetFund")) - Int(1000), 
                TxnField.close_remainder_to: Receiver,
            }   
        ),
        InnerTxnBuilder.Submit(),
        Return(Int(1))
    )

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        If(And(Global.latest_timestamp() >= EndDate, EventProgress == Int(0))).Then(
            end_event
        ),
        Cond(
            [Txn.application_args[0] == Bytes("Donation"), make_donation],
            [Txn.application_args[0] == Bytes("Claim"), claim],
        )  # Check for donation request
    )


    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],  # Default condition for initialization
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],  # Default condition for opt-in
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],  # Default condition for close-out
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],  # Default condition for update
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],  # Default condition for delete
        [Txn.on_completion() == OnComplete.NoOp, handle_noop] # Default condition for no-op
    )

    return compileTeal(program, Mode.Application, version=5)

def clear_state_program():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

# Write to file
appFile = open('approval.teal', 'w')
appFile.write(approval_program())
appFile.close()

clearFile = open('clear.teal', 'w')
clearFile.write(clear_state_program())
clearFile.close()