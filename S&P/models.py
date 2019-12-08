# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:52:15 2019

@author: Nischal
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class Investor:

    data_snp = pd.read_excel("blog.xlsx")  # Read file
    # Get percentage changes
    data_snp["Percentage_Change"] = data_snp["Price_SnP"].pct_change() * 100
    data_snp.fillna(value=0, inplace=True)  # Fill nan values with 0
    total_points = len(data_snp)  # Total Data points
    years = sorted(data_snp["Date"].apply(lambda x: x.year).unique().tolist())
    n_years = len(years)  # Total number of years

    def __init__(self):

        self.stocks_owned = 0  # Total stocks owned by an investor
        self.available_cash = 0  # Cash remaining after purchasing
        self.total_investment = 0  # Total money invested till date
        self.data = Investor.data_snp.copy()  # Make a copy of the S&P data

    def GetReturnRatio(self):

        num_el = len(self.data)  # Number of elements in the dataset
        # Return on investment ratio
        roi_ratio = self.data.loc[num_el - 1, "Asset_Value"] / \
            self.data.loc[num_el - 1, "Total_Investment"]
        return np.round(roi_ratio, 2)

    def GetAssetValue(self, stock_price):
        # This function is used to update total assets
        asset_value = self.available_cash + stock_price * self.stocks_owned
        return asset_value

    def LogData(self, idx, stock_price, stocks_acquired):
        # This function is used to log data to dataframe on any given day = idx
        self.data.loc[idx, "Asset_Value"] = self.GetAssetValue(stock_price)
        self.data.loc[idx, "Stocks_Owned"] = self.stocks_owned
        self.data.loc[idx, "Stocks_Acquired"] = stocks_acquired
        self.data.loc[idx, "Available_Cash"] = self.available_cash
        self.data.loc[idx, "Total_Investment"] = self.total_investment

    def BuyStocks(self, stock_price):
        '''
        This function is used to update stocks owned and available cash whenever stocks are bought
        and return the amount of stocks bought
        '''

        # Buy stocks in whole number
        stocks_acquired = self.available_cash // stock_price
        # Update stocks owned
        self.stocks_owned += stocks_acquired
        # Update available cash to the amount remaining after buying stocks
        self.available_cash = self.available_cash % stock_price

        return stocks_acquired

    def DepositFunds(self, amount):
        '''
        This function is used to update the total investments and available cash
        when money is deposited in the account
        '''
        # Update total_investment and available_cash
        self.total_investment += amount
        self.available_cash += amount

    def InvestMonthly(self, amount=200, apply_boost=False, boost_perc=1e-12, apply_yearly_increment=False, increment_in_years=None, incr_fac=None):
        """
        In this strategy we invest on a fixed day i.e. 1st of every month.
        Amount is the value invested monthly, default value being 200
        apply_boost parameter is used to control whether we want to increase the amount 
        invested per month if the index goes down. Default is False
        """

        assert amount is not None, "amount cannot be None in monthly investment strategy, please give an amount"

        self.amount = amount

        if apply_yearly_increment:
            assert increment_in_years is not None, "increment in years can't be none, please give a value"
            assert incr_fac is not None, "incr_fac can't be none, please give a value"
            assert increment_in_years < Investor.n_years, " increment in years can't be greater than the total number of years"
            total_years = Investor.years  # Get total number of years
            # Select years when the amount will be doubled. Start from 1 as we won't double the investment from starting year
            incremental_years = total_years[::increment_in_years][1:]
            years_multiplication_factor = {
                year: (k+1)*incr_fac for k, year in enumerate(incremental_years)}

        incr_boost = boost_perc  # Assign boost_incr to incr_boost variable
        # List that will store the years when increment has already been applied
        years_incr_applied = []

        for i in range(Investor.total_points):

            if not apply_boost:
                if apply_yearly_increment:
                    # Get current year
                    current_year = self.data.loc[i, "Date"].year
                    # Check if the year is in the years when the amount is to be doubled
                    if current_year in years_multiplication_factor and current_year not in years_incr_applied:
                        # Get the multiplication factor
                        mult_factor = years_multiplication_factor[current_year]
                        # Now increment the amount
                        self.amount *= mult_factor
                        years_incr_applied.append(current_year)
                # If not applying boosting, keep the deposit amount same
                amount_deposited = self.amount
            else:
                assert 0 < boost_perc <= 0.25, "Boost Percentage should be between 0 and 0.25"
                # Get the percentage change in index
                perc_change = self.data.loc[i, "Percentage_Change"]

                if perc_change >= 0:
                    amount_deposited = self.amount
                elif -5 <= perc_change < 0:
                    # If perc_change is between 0  to -5, increase deposit amount by 1 * incr_boost
                    amount_deposited = (1.0 + 1 * incr_boost) * self.amount
                elif -10 <= perc_change < -5:
                    # If perc_change is between -10 to -20, increase deposit amount by 2 * incr_boost
                    amount_deposited = (1.0 + 2 * incr_boost) * self.amount
                elif -15 <= perc_change < -10:
                    # If perc_change is between 20 to 30, increase deposit amount by 3 * incr_boost
                    amount_deposited = (1.0 + 3 * incr_boost) * self.amount
                elif perc_change < -15:
                    # If perc_change is greater than 15 %, double the deposit
                    amount_deposited = 2 * self.amount

            # Step 1. Add money to account
            self.DepositFunds(amount_deposited)

            # Step 2. Get the stock price
            stock_price = self.data.loc[i, "Price_SnP"]

            """
            If the stock price is more than the remaining cash, 
            then we cannot buy any stock this month. So we donot do any updates
            """
            if self.available_cash < stock_price:
                '''
                Since we didn't buy new stocks therefore 
                new stocks acquired = 0, 
                '''
                stocks_acquired = 0

                # Log data to the dataframe
                self.LogData(i, stock_price, stocks_acquired)

            else:
                """
                1. Buy stocks. 
                    Note: Stocks can only be bought in whole numbers
                2. Update available cash to the amount left after buying stocks
                """

                # Buy Stocks
                stocks_acquired = self.BuyStocks(stock_price)

                # Log data to dataframe
                self.LogData(i, stock_price, stocks_acquired)

        return self.data


P1 = Investor()
p1 = P1.InvestMonthly(amount=300, apply_boost=False)
P2 = Investor()
p2 = P2.InvestMonthly(amount=300, apply_boost=True, boost_perc=0.15)
P3 = Investor()
p3 = P3.InvestMonthly(
    amount=300, apply_yearly_increment=True, increment_in_years=20, incr_fac=2)

plt.close("all")

plt.plot(p1["Asset_Value"], 'r', label="Strategy 1 (Invest Monthly)")
plt.plot(p1["Total_Investment"], '--r', label="Strategy 1: Total Investment")
plt.plot(p2["Asset_Value"], 'b', label="Strategy 2 (Apply Monthly Boosting)")
plt.plot(p2["Total_Investment"], '--b', label="Strategy 2: Total Investment")
plt.plot(p3["Asset_Value"], 'g', label="Strategy 3 (Double Investment)")
plt.plot(p3["Total_Investment"], '--g', label="Strategy 3: Total Investment")


plt.legend(loc="upper center", fontsize=14)
plt.yticks(fontsize=14)
plt.ylabel("Amount in $", fontsize=14)

#%%


pct = p1.loc[:, "Percentage_Change"]

import seaborn as sns 

plt.plot(pct)

plt.figure()

sns.distplot(pct)


# %%

# Get number of data points
n = Investor.total_points - 1

investments = [p1.loc[n, "Total_Investment"],
               p2.loc[n, "Total_Investment"], p3.loc[n, "Total_Investment"]]
inv_ret = pd.DataFrame(data=investments, index=[
                       "S1", "S2", "S3"], columns=["Investments"])

inv_ret["Returns"] = [p1.loc[n, "Asset_Value"],
                      p2.loc[n, "Asset_Value"], p3.loc[n, "Asset_Value"]]

inv_ret.plot(kind="bar")
