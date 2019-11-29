# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:52:15 2019

@author: Nischal
"""

import pandas as pd
import matplotlib.pyplot as plt


class Investor:
    
    data = pd.read_excel("blog.xlsx")
        
    def __init__(self):
        
        self.stocks_owned = 0 # Total stocks owned by an investor
        self.asset_value = 0 # Total value of the investments (= remaining cash + stocks_owned * price)
        self.available_cash = 0 # Cash remaining after purchasing
        self.total_investment = 0 # Total money invested till date
        
    def DepositMoney(self, amount):
        # This function is used to update the money deposited to the account
        
        self.available_cash+=amount
    
    def UpdateTotalInvestment(self, amount, idx):
        # This function updtes total investments made to an account
        self.total_investment+=amount
        Investor.data.loc[idx, "Amount_Invested"] = self.total_investment


    def Compute_S1(self, amount=200):
        """
        In this strategy we invest on a fixed day i.e. 1st of every month. 
        
        Amount is the value invested monthly, default value being 200
        """

        
        data = Investor.data
        
        for i in range(len(data)):
            # Step 1. Add money to account
            self.DepositMoney(amount) 
            # Step 2. Update total investment
            self.UpdateTotalInvestment(amount, i)
            # Get the stock price
            price = data.loc[i, "Price_SnP"]
            
            """
            If the stock price is more than the remaining cash, 
            then we cannot buy any stock this month. So add the amount to 
            the remaining cash.
            """            
            if self.available_cash < price:
                self.available_cash+=amount
                self.asset_value = self.available_cash + price * self.stocks_owned
                
                # Add data to the dataframe
                data.loc[i, "Remaining_Cash"] = self.available_cash
                data.loc[i, "Asset_Value"] = self.asset_value
                # Since we didn't buy new stocks or stocks acquired = 0, they are same as previous month
                data.loc[i, "Stocks_Acquired"] = 0
                if i == 0:                    
                    data.loc[i, "Stocks_Owned"] = 0
                else:                    
                    data.loc[i, "Stocks_Owned"] = data.loc[i-1, "Stocks_Owned"]                
            else:                
                """
                1. Buy stocks. Stocks can only be bought in whole numbers
                2. Add remaining money to the remining cash
                """
                stocks_acquired = self.available_cash // price
                self.stocks_owned+=stocks_acquired
                self.available_cash = self.available_cash % price                
                self.asset_value = self.available_cash + price * self.stocks_owned
                
                # Add data to dataframe
                data.loc[i, "Asset_Value"] = self.asset_value               
                data.loc[i, "Stocks_Owned"] = self.stocks_owned
                data.loc[i, "Stocks_Acquired"] = stocks_acquired            
                data.loc[i, "Available_Cash"] = self.available_cash
                
        return data

p = Investor().Compute_S1()    

plt.subplot(2,2,1)
plt.plot(p["Price_SnP"], '--r', label = "S&P");plt.legend()
plt.ylabel("S&P Index", fontsize = 14); plt.yticks(fontsize = 14)            
plt.subplot(2,2,2)
plt.plot(p["Asset_Value"], '--g', label = "Asset Value"); plt.legend()      
plt.plot(p["Amount_Invested"], '--b', label = "Amount_Invested")
plt.ylabel("Amount in USD", fontsize = 14); plt.yticks(fontsize = 14)            

plt.legend()            
           

                
            
            

