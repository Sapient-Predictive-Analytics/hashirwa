## Milestone-2 Evidence: Video and Screenshots

A video walk-through of how the Chainlink Distributed Oracle Network (DON) is utilized for certification and price data can be found [HERE](https://drive.google.com/file/d/1FGDaunIrSJRqRjV5fBCLCHnPHyVW7QY0/view?usp=sharing)

Screenshots as Milestone evidence for the updated features, UI and on-chain fulfillment can be found in their respective sections below.

### Automated refresh schedule daily/weekly

Periodic oracle feeds are shown directly in the terminal console using Chainlink's cron scheduling when triggered:
![Terminal](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/automation_terminal_log1.jpg)

A refresh log is also written to file and can be inspected or exported as necessary with all historical calls and fulfillments:
![Log](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/scheduled_log.jpg)

### Market data shown on listing pages
Buttons and feed columns have been added to the Listings page to reflect periodic or manual (upon clicking the Refresh button shown) updates to market price and certification status:
![Listings](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/hashi_with_oracle.jpg)

### Public landing page for separate issuer and investor journey
New UI with views for issuers and investors have been added at this milestone (to be integrated with agricultural produce feeds next milestone):

![Investor Dashboard](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/investor.jpg)
*Investor Dashboard*

![Issuer Dashboard](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/dashboard.jpg)
*Issuer Dashboard*

![Issuer Inout Mask](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/issuer2.jpg)
*Isser Input Mask*

### Chainlink Functions Fulfillment

The current Testnet Chainlink Subscription can be found [HERE](https://functions.chain.link/sepolia/6178)

The Chainlink Functions landing page looks like this:
![Chainlink](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/functionsOverview.jpg)

Screenshot of fulfillments from the Demo video:
![CL Dashboard](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/chainlink_fulfillments.jpg)

A successful Callback:
![Callback](https://github.com/Sapient-Predictive-Analytics/hashirwa/blob/tech/m2/docs/milestones/M2_completed/consumer_callback.jpg)

[This](https://sepolia.etherscan.io/tx/0x891d7ac77073cf8ede5711a8ecefc1b1ac9ed9889b0e88d879ffdd3e82857c4c) is the transaction hash for the on-chain oracle verification.




