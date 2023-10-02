# Charity Application README

Welcome to the Charity Application! This application is designed to help you manage and streamline your charitable events on the Algorand blockchain.

## Global State Variables

The Charity Application utilizes several global state variables to track and manage various aspects of your charity event:

1. **TargetFund (`TargetFund`):** This variable represents the target amount of funds needed for your charity event. It is initialized with the value provided as the first argument during application creation.

2. **TotalFund (`TotalFund`):** This variable keeps track of the total funds collected during the charity event. It starts at 0 and will be updated as donations are made.

3. **Receiver (`Receiver`):** The `Receiver` variable stores the Algorand address of the entity or individual who will receive the funds collected during the charity event. It is specified as the second argument during application creation.

4. **StartDate (`StartDate`):** This variable records the timestamp when the charity event started. It is set to the latest timestamp when the application is created.

5. **EndDate (`EndDate`):** The `EndDate` variable represents the timestamp when the charity event will end. It is calculated based on the duration provided as the third argument during application creation.

6. **EventProgress (`EventProgress`):** `EventProgress` is used to indicate the current state of the charity event:
   - `0`: Event Ongoing - The charity event is still active, and donations are being accepted.
   - `1`: Event Ended - The charity event has concluded, and no more donations are accepted.
   - `2`: Fund Claimed - The funds have been claimed by the receiver.

These global state variables ensure transparency and efficient management of your charity event on the Algorand blockchain.

## Getting Started

To create this application, you'll need to execute the following command:

```bash
goal app create --creator $CREATOR --approval-prog Project/approval.teal --clear-prog Project/clear.teal --global-ints 5 --global-byteslices 1 --local-ints 1 --local-byteslices 0 --app-arg 'int:1000000' --app-arg "addr:$RECEIVER" --app-arg 'int:432000'
```

This command sets up your application with the following configurations:

Total of 5 integer global states and 1 global byteslice.
1 integer local state.

## Arguments

The command also takes three arguments, which are crucial for your charity event:

**Target Funds Needed (int:1000000)**: This argument indicates the target amount of funds you aim to raise for your charity event. You can modify this value to match your fundraising goal.

**Receiver Address (addr:$RECEIVER)**: This argument specifies the Algorand address of the entity or individual who will receive the funds collected during the charity event. Make sure to replace $TWO with the actual Algorand address of the receiver.

**Time Period in Seconds (int:432000) (5Day)**: The third argument represents the duration of the charity event in seconds. You can adjust this value according to the length of your fundraising campaign.

## Usage

Once your charity application is created, you can integrate it into your charity platform to facilitate secure and transparent donations. The application will manage the global and local states, ensuring that funds are allocated appropriately to the designated receiver.

**Making a Donation**
To make a donation using the Charity Application, follow these steps:

1. Calling the Application to Donate:

To start a donation event, use the following command:

```bash
goal app call --app-id $APPID -f $CALLER --app-arg 'string:Donation' --app-arg 'int:1000000' --dryrun-dump -o dryrun.msog
```

The first app-arg specifies 'Donation' to initiate the donation event.
The second app-arg indicates the amount you want to donate.

**Claiming Funds**
To claim funds from the Charity Application, use the following command:

```bash
goal app call --app-id $APPID -f $RECEIVER --app-arg 'string:Claim' --dryrun-dump -o dryrun.msog
```

The app-arg should be set to 'Claim' to initiate the funds claiming event.

### Event Progress

The `EventProgress` global state variable plays a pivotal role in managing the charity event. Here's how it operates:

- **Initial State (`EventProgress` set to `0`):** Initially, `EventProgress` is set to `0`, indicating that the charity event is ongoing.

- **Donation and DonationMade:**

  - When someone makes a donation during the event period, the `TotalFund` global state variable is updated to reflect the contributed amount.
  - Additionally, the `DonationMade` local state variable is utilized to record whether an individual has already contributed and, if so, how much they have donated.

- **Target Funds Reached (`EventProgress` set to `1`):**

  - If the `TotalFund` reaches the specified `TargetFunds` (set during application creation), `EventProgress` is updated to `1`, indicating that the event has ended.
  - Once the event has ended (when `EventProgress` is `1`), no further donations will be accepted.

- **Ending the Event (`EventProgress` remains `1`):**

  - If, during the event period, no one makes any donations, the `Receiver` (specified during application creation) has the option to end the event after the `EndDate` (also specified during application creation).
  - The `EventProgress` remains at `1`, indicating that the event has ended.

- **Claiming Funds (`EventProgress` set to `2`):**
  - After the event ends (when `EventProgress` is `1`), the `Receiver` has the authority to claim the funds collected if not 0 funds collected.
  - Upon successful claiming of the funds, `EventProgress` is updated to `2`, indicating that the funds have been claimed.

## Useful Debug Code

```bash
  - goal app call --app-id $APP -f $DONOR --app-arg 'string:Donation' --app-arg 'int:100000' --dryrun-dump -o dryrun.msog
  - goal app call --app-id $APP -f $RECEIVER --app-arg 'string:Claim' --dryrun-dump -o dryrun.msog
  - tealdbg debug -d dryrun.msog --listen 0.0.0.0
```

**Noted that Algorand Minimum trascation is 0.1ALGOs**

## Support and Feedback

...

Thank you for choosing our charity application to make a positive impact in the world!

```

```
