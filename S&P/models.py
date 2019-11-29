# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 20:52:15 2019

@author: Nischal
"""

import pandas as pd
import matplotlib.pyplot as plt


class Investor:
    
    data_snp = pd.read_excel("blog.xlsx")
    total_points = len(data_snp) # Total Data points 
        
    def __init__(self):
        
        self.stocks_owned = 0 # Total stocks owned by an investor
        self.available_cash = 0 # Cash remaining after purchasing
        self.total_investment = 0 # Total money invested till date
        self.data = Investor.data_snp # Make a copy of the S&P data
        
        
    def GetAssetValue(self, stock_price):
        # This function is used to update total assets
        asset_value = self.available_cash + stock_price * self.stocks_owned
        return asset_value
    
    def LogData(self, idx, stock_price, stocks_acquired):
        # This function is used to log data to dataframe on any given day = idx
        
        # Add data to dataframe
        self.data.loc[idx, "Asset_Value"] = self.GetAssetValue(stock_price)               
        self.data.loc[idx, "Stocks_Owned"] = self.stocks_owned
        self.data.loc[idx, "Stocks_Acquired"] = stocks_acquired            
        self.data.loc[idx, "Available_Cash"] = self.available_cash 
        self.data.loc[idx, "Total_Investment"] = self.total_investment



    def Compute_S1(self, amount=200):
        """
        In this strategy we invest on a fixed day i.e. 1st of every month. 
        
        Amount is the value invested monthly, default value being 200
        """

        for i in range(Investor.total_points):
            # Step 1. Add money to account
            # Update total_investment and available_cash
            self.total_investment+=amount
            self.available_cash+=amount

            # Step 2. Get the stock price
            stock_price = self.data.loc[i, "Price_SnP"]
            
            """
            If the stock price is more than the remaining cash, 
            then we cannot buy any stock this month. 
            """            
            if self.available_cash < stock_price:
                '''
                Since we didn't buy new stocks therefore 
                new stocks acquired = 0, 
                and total stocks owned are same as previous month
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
                # Buy stocks in whole number
                stocks_acquired = self.available_cash // stock_price
                # Update stocks owned
                self.stocks_owned+=stocks_acquired
                # Update available cash to the amount remaining after buying stocks
                self.available_cash = self.available_cash % stock_price

                # Log data to dataframe
                self.LogData(i, stock_price, stocks_acquired)

                
        return self.data

p = Investor().Compute_S1()    

plt.close("all")
plt.subplot(2,2,1)
plt.plot(p["Price_SnP"], '--r', label = "S&P");plt.legend()
plt.ylabel("S&P Index", fontsize = 14); plt.yticks(fontsize = 14)            
plt.subplot(2,2,2)
plt.plot(p["Asset_Value"], '--g', label = "Asset Value"); plt.legend()      
plt.plot(p["Total_Investment"], '--b', label = "Total_Investment")
plt.ylabel("Amount in USD", fontsize = 14); plt.yticks(fontsize = 14)            

plt.legend()            
           

                
            
            

