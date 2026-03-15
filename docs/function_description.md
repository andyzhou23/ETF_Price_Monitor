# Full Stack Developer Interview

This is an interview for the **full stack data developer role** at **BMO Capital Markets' Data Cognition Team**.

---

## Requirements

Design a **single page web application** (actually a single page!) that allows traders to view historical prices for a given ETF and its top holdings.

The frontend should be written in a front end framework such as **Angular, React, Vue** or any other framework that you feel comfortable.

The backend can be anything you want. We primarily use **Python** but you're free to pick whatever you like.

Partial solutions are acceptable. It is not necessary to submit a complete solution that implements every requirement.

---

## Quick introduction to ETFs

**ETFs (Exchange Traded Funds)** are traded securities that hold a basket of securities; the securities could be **stocks, bonds, or even other ETFs**.

In general, the price of the ETF at any time can be computed by doing a **weighted sum of the price of each individual constituent**, and we'll be assuming that the **weights are not changing over time** in this challenge.

---

## Data provided

We've provided all the data you need to complete the challenge. You **don't need to contact any public external API**.

### We've provided:

- `ETF1.csv` and `ETF2.csv` containing the **constituents and their weights** in each ETF
- `prices.csv` which contains the **historical price data for all the constituents**
  - Note that this file contains prices for **all constituents**

---

## Functionality

- Upload a `.csv` file containing weights of a given ETF, `ETF1.csv` or `ETF2.csv`
- An **interactive table** similar to the uploaded `ETF[1-2].csv` file on the webpage that displays three columns:
  - The **constituent name**, i.e., `A`
  - The **weight**, i.e., `0.02`
  - The **most recent close price** of the constituent, i.e., `$20.05` for `A`
- A **zoomable time series plot** of the reconstructed price of the ETF
  - The price of the ETF is calculated as the **weighted sum of the individual prices**
- A **bar chart displaying the top 5 biggest holdings** in the ETF as of the latest market close
  - You can compute the holding size of each constituent by multiplying the **weight and the price**

---

## Challenge Scope

- High level description of **design and technologies used**
- **Document all assumptions made**
- Complete solutions aren't required, but **what you do submit needs to run**

---

## What are we looking for? What does this prove?

- **Assumptions** you make given limited requirements
- **Technology and design choices**
- **Identify areas of your strengths**
- This is **not a pass or fail test**, this will serve as a **common ground for discussion** where we can deep dive together into specific issues

---

## Submission Guidelines

- Follow a **clear project structure**
- Include a **README file with summary**
- Submit within **4 days**
- Prepare for an **in-person review**
