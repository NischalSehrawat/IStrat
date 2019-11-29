# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:52:15 2019

@author: Nischal
"""

import pandas as pd
import matplotlib.pyplot as plt


class Investor:

    data_snp = pd.read_excel("blog.xlsx")  # Read file
    # Get percentage changes
    data_snp["Percentage_Change"] = data_snp["Price_SnP"].pct_change() * 100
    data_snp.fillna(value=0, inplace=True)  # Fill nan values with 0
    total_months = len(data_snp)  # Total Data points

    def __init__(self):

        self.stocks_owned = 0  # Total stocks owned by an investor
        self.available_cash = 0  # Cash remaining after purchasing
        self.total_investment = 0  # Total money invested till date
        self.data = Investor.data_snp.copy()  # Make a copy of the S&P data

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

    def InvestMonthly(self, amount=200, apply_boost=False, boost_perc = 0.1):
        """
        In this strategy we invest on a fixed day i.e. 1st of every month.
        Amount is the value invested monthly, default value being 200
        apply_boost parameter is used to control whether we want to increase the amount 
        invested per month if the index goes down. Default is False
        """

        for i in range(Investor.total_months):

            if not apply_boost:
                # If not applying boosting, keep the deposit amount same
                amount_deposited = amount
            else:
                # Get the percentage change in index
                perc_change = self.data.loc[i, "Percentage_Change"]
                incr_boost = boost_perc
                
                if perc_change >=0:
                    amount_deposited = amount
                elif -10 <= perc_change < 0 :
                    # If perc_change is between 0  to -10, keep the amount same
                    amount_deposited = (1.0 + 0.5 * incr_boost) * amount
                elif -20 <= perc_change < -10:
                    # If perc_change is between -10 to -20, increase deposit amount by 10%
                    amount_deposited = (1.0 + 1 * incr_boost) * amount
                elif -30 <= perc_change < -20:
                    # If perc_change is between 20 to 30, increase deposit amount by 20%
                    amount_deposited = (1.0 + 2 * incr_boost) * amount
                elif -40 <= perc_change < -30:
                    # If perc_change is between 30 to 40, increase deposit amount by 30%                    
                    amount_deposited = (1.0 + 3 * incr_boost) * amount
                elif -50 < perc_change < -40:
                    # If perc_change is between 40 to 50, increase deposit amount by 40%                    
                    amount_deposited = (1.0 + 4 * incr_boost) * amount
                elif perc_change <=-50:
                    # If perc_change is greater than 50 %, increase deposit amount by 50%                                       
                    amount_deposited = (1.0 + 5 * incr_boost) * amount
                    
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


p1 = Investor().InvestMonthly(amount=200, apply_boost=False)
p2 = Investor().InvestMonthly(amount=200, apply_boost=True, boost_perc = 0.3)

plt.plot(p1["Asset_Value"], label = "Monthly Investment")
plt.plot(p2["Asset_Value"], label = "Monthly Investment WITH Boosting")
plt.legend(loc = "upper center", fontsize = 14)

