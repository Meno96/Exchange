<h1 align="center">
    BTC Exchange Project
</h1>

<br/>

This project is a BTC Exchange where you can simulate trades with BTC (no real BTC are used).

The main purpose of this project is to show how to combine Django and MongoDB to make a powerful platform that manage all the orders.

<hr/>

## 🗎&nbsp; Requirements

* The platform must have an endpoint to manage user registration and access.

* Automatically assign 1 to 10 bitcoins to each user.
* Each user can post one or more sales or purchase orders of a certain amount.
* At the time of publication, if the purchase price of the order is equal to or greater than the selling price of any other user, match the transaction and mark both orders as filled.
* Provide an endpoint to get all active buy and sell orders.
* Provide an endpoint to calculate the total profit or loss from each user's trades.
* Assume that the platform in question is totally free for users and does not retain any type of commission on operations.


## 🚀&nbsp; How it's suppose to work?

When a user registers, a wallet associated with the user is automatically generated, containing a random value between 1 and 10 bitcoins and between 50k and 150k $.

This wallet can be used to simulate BTC trades.

<p align="center">
    <img width="80%" src="./assets/GitHubImg/screen3.png" alt="Register page">
</p>

<p align="center">
    <img width="80%" src="./assets/GitHubImg/screen1.png" alt="Register view">
</p>

<p align="center">
    <img width="80%" src="./assets/GitHubImg/screen2.png" alt="Wallet Object">
</p>
