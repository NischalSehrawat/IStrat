# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:52:15 2019

@author: Nischal
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class Investor:

    def __init__(self):

        self.stocks_owned = 0  # Total stocks owned by an investor
        self.available_cash = 0  # Cash remaining after purchasing
        self.total_investment = 0  # Total money invested till date
        self.data = None  # Initialise data holding variable

    @classmethod
    def PrepareData(cls, index_name):
        '''
        This class method is used for preparing the respective dataset
        '''

        data = pd.read_excel(index_name + ".xlsx")  # Read file

        if index_name == "snp":
            data["Date"] = pd.to_datetime(
                data["Date"].apply(lambda x: x.strftime("%d-%m-%Y")))
        else:
            data["Date"] = pd.to_datetime(data["Date"])
        # Get percentage changes
        data["Percentage_Change"] = data["Price"].pct_change() * 100
        data.fillna(value=0, inplace=True)  # Fill nan values with 0

        cls.data = data
        cls.total_points = len(data)  # Total Data points
        cls.years = sorted(data["Date"].apply(
            lambda x: x.year).unique().tolist())
        cls.n_years = len(cls.years)  # Total number of years

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
        There are 3 strategies implemented in the monthly investment plan
        1. The first strategy is to just keep on investing a fixed sum each month, irrespective of 
            the market conditions.
        2. The second strategy is to adjust the first strategy as per market. Invest more when the market drops
            and keep the amount same when market recovers
        3. The last strategy is to increase the amount invested each month after every "Y" ears by "X" percent. 
            This is done to account for the fact that with time, salaries also increase and we can invest more

        The following are the parameters of the function
        
        amount: The value invested monthly, default value being 200
        apply_boost:  Parameter is used to control whether we want to increase the amount in 2nd strategy
        boost_perc:  Parameter is used to control the increased the amount in 2nd strategy. It can have a max value of 0.25
        apply_yearly_increment: Parameter to apply Strategy #3
        increment_in_years: Parameter to specify the numbey of years after which you want to increase the monthly investment
        incr_fac: Parameter to specify the factor that must be multiplied by the last EMI to amplify it
        
        The function returns the dataframe with logged values

        """
        self.data = Investor.data.copy()  # Make a copy of the dataset

        assert amount is not None, "amount cannot be None in monthly investment strategy, please give an amount"

        if apply_yearly_increment:
            assert increment_in_years is not None, "increment in years can't be none, please give a value"
            assert incr_fac is not None, "incr_fac can't be none, please give a value"
            assert increment_in_years < Investor.n_years, " increment in years can't be greater than the total number of years"
            total_years = Investor.years  # Get total number of years
            # Select years when the amount will be doubled. Start from 1 as we won't double the investment from starting year
            incremental_years = total_years[::increment_in_years]
            years_multiplication_factor = {
                year: incr_fac**(k) for k, year in enumerate(incremental_years)}

        incr_boost = boost_perc  # Assign boost_incr to incr_boost variable
        # List that will store the years when increment has already been applied
        years_incr_applied = []

        self.amount = amount

        for i in range(Investor.total_points):
            # If we are doing only normal monthly investment
            if not apply_boost:
                # If we are increasing the amount as years go by along with systematic monthly investments
                if apply_yearly_increment:
                    # Get current year
                    current_year = self.data.loc[i, "Date"].year
                    # Check if the year is in the years when the amount is to be doubled
                    if current_year in years_multiplication_factor and current_year not in years_incr_applied:
                        # Get the multiplication factor
                        mult_factor = years_multiplication_factor[current_year]
                        # Now increment the amount
                        self.amount = mult_factor * amount
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
            stock_price = self.data.loc[i, "Price"]

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
    
    def GetCagr(self):
        
        Asset_Value = self.data.iloc[-1]["Asset_Value"] 
        Total_Investment = self.data.iloc[-1]["Total_Investment"] 
        
        return 100*((Asset_Value/Total_Investment)**(1/Investor.n_years) - 1)


        


# %%


# ================== Adjust parameters here =====================
index_name = "nifty"
amnt = 15000  #EmI
inc_every = 10 # Years in whcih you wish to increase your emi
inc_perc = 5 # Percentage increase in EMI after every inc_every time period
# ========================================= =====================

# Initialise the dataset as per index name
Investor().PrepareData(index_name)

P1 = Investor();
P2 = Investor()
P3 = Investor()


p1 = P1.InvestMonthly(amount=amnt)
p2 = P2.InvestMonthly(amount=amnt, apply_boost=True, boost_perc=0.20)
p3 = P3.InvestMonthly(
    amount=amnt, apply_yearly_increment=True, increment_in_years=inc_every, incr_fac=1 + 0.01*inc_perc)

plt.close("all")

if index_name != 'snp':
    scale_fac = 1e5 # Scaling factor for Y axis, for Indian context, set it to 1 lakh
    plt.plot(p1["Date"], p1["Asset_Value"] / scale_fac, 'r',
         label=f"Strategy 1 (Invest ₹ {amnt} Monthly, CAGR = {format(P1.GetCagr(),'.2f')} %)")
    plt.ylabel("Amount in Lakhs ₹", fontsize=14)
else:
    scale_fac = 1e6 # Scaling factor for Y axis for American 1 million
    plt.plot(p1["Date"], p1["Asset_Value"] / scale_fac, 'r',
         label=f"Strategy 1 (Invest $ {amnt} Monthly)")
    plt.ylabel("Amount in Million $", fontsize=14)


plt.plot(p1["Date"], p1["Total_Investment"] / scale_fac,
         '--r', label="Strategy 1: Total Investment")
plt.plot(p2["Date"], p2["Asset_Value"] / scale_fac, 'b',
         label=f"Strategy 2 (Apply Monthly Boosting, CAGR = {format(P2.GetCagr(),'.2f')} %)")
plt.plot(p2["Date"], p2["Total_Investment"] / scale_fac,
         '--b', label="Strategy 2: Total Investment")
plt.plot(p3["Date"], p3["Asset_Value"] / scale_fac, 'g',
         label=f"Strategy 3 ({inc_perc}% increase Investment every {inc_every} year, CAGR = {format(P3.GetCagr(),'.2f')} %)")
plt.plot(p3["Date"], p3["Total_Investment"] / scale_fac,
         '--g', label="Strategy 3: Total Investment")


plt.legend(loc="upper center", fontsize=14)
plt.yticks(fontsize=14)
plt.xticks(fontsize=14)
plt.xlabel("Years", fontsize=14)

for investor in  [P1, P2, P3]:
    
    print(investor.GetCagr())
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
