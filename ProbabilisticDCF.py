#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 16:21:27 2021

@author: darshan
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

class intrinsicValue():
    def __init__(self,path,path2):
          self.path = path
          self.path2 =path2
          self.meansd = pd.read_csv(self.path2)
          self.year_index = np.arange(0,11).tolist()
          self.base_year = pd.read_csv(self.path)
          self.simulations()
          self.line_item_index_mapping()
          self.terminal_growth_rate = 0.01
          self.diluted_shares_outstanding = 465600000
          self.set_sims()
          self.discount_rate = 0.10
          self.effective_cash_balance = 475
          self.simulated_line_items()
          self.fair_value()
          
          
    def line_item_mapping(self):
        Line_items = self.base_year['Line_items'].tolist()
        Values = self.base_year['Values'].tolist()
        mapping = {}
        
        for key,value in zip(Line_items,Values):
            
            mapping[key] = value
            
        return mapping
    
    
    def line_item_index_mapping(self):
        self.dd = {0: {'Revenue':(self.meansd.iloc[0,2],self.meansd.iloc[0,3])},
              1: {'Expense':(self.meansd.iloc[1,2],self.meansd.iloc[1,3])},
              2: {'InterestExpense':(self.meansd.iloc[4,2],self.meansd.iloc[4,3])},
              3: {'IncomeTax':(self.meansd.iloc[9,2],self.meansd.iloc[9,3])},
              4: {'Capex':(self.meansd.iloc[7,2],self.meansd.iloc[7,3])},
              5: {'Depreciation':(self.meansd.iloc[8,2],self.meansd.iloc[8,3])}}
        

    
    def simulations(self):
        
        self.sims = np.zeros((len(self.base_year.Line_items) - 9,len(self.year_index),100000))
    
    
    
    def generate_simulations(self,mean,sd):
        
        rnd = np.random.RandomState(seed = None)
        simulations= rnd.normal(mean,sd,size = 100000)
        return simulations
    
    
        
    def set_sims(self):
        for i in range(len(self.base_year.Line_items) - 9):
            for j in range(len(self.year_index)):
                if i == 0:
                  mean = self.dd[i]['Revenue'][0]
                  sd =   self.dd[i]['Revenue'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                elif i == 1:
                  mean = self.dd[i]['Expense'][0]
                  sd =   self.dd[i]['Expense'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                  
                elif i == 2:
                  mean = self.dd[i]['InterestExpense'][0]
                  sd =   self.dd[i]['InterestExpense'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                elif i == 3:
                  mean = self.dd[i]['IncomeTax'][0]
                  sd =   self.dd[i]['IncomeTax'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                elif i == 4:
                  mean = self.dd[i]['Capex'][0]
                  sd =   self.dd[i]['Capex'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                  
                else:
                  mean = self.dd[i]['Depreciation'][0]
                  sd =   self.dd[i]['Depreciation'][1]
                  self.sims[i,j,:] = self.generate_simulations(mean,sd)
                  
                  
                  
    def simulated_line_items(self):
        self.revenue = [1] *11
        self.revenue[0] = self.base_year.Values.values.tolist()[0]
        for i in range(10):
            self.revenue[i+1] =  self.revenue[i] * (1 + np.mean(self.sims,axis = 2)[0][i])
            
        for k in range(1,5):  
            if k == 1:
                self.Expenses = np.asarray(self.revenue) * np.mean(self.sims,axis = 2)[k]
                self.EBITDA = self.revenue - self.Expenses
            elif k == 2:
                self.InterestExpense = np.asarray(self.revenue) * np.mean(self.sims,axis = 2)[k]
                
            elif k == 3:
                self.IncomeTax = np.asarray(self.EBITDA) * np.mean(self.sims,axis = 2)[k]
            elif k == 4:
                self.Capex = np.asarray(self.revenue) * np.mean(self.sims,axis = 2)[k]
        self.Dep = np.asarray(self.revenue) * np.mean(self.sims,axis = 2)[5] 
                
        self.NOPAT = self.EBITDA - self.InterestExpense - self.IncomeTax
        self.FCF = self.NOPAT - self.Capex
        
        self.factor = np.ones(11) * self.discount_rate
        self.discount_factor = [(1+x)**-i for x,i in zip(self.factor.tolist(),self.year_index)]
        self.DFCF = self.discount_factor * self.FCF
        
        
        
    def terminal_DCF(self):
        ratio = (1 + self.discount_rate)/(self.discount_rate - self.terminal_growth_rate)
        terminal_dcf = (self.FCF[-1]*ratio-1679.0)*(1+ self.discount_rate)**(-10)
        return terminal_dcf   
        
         
    def fair_value(self):
         self.summed_dfcf= sum(self.DFCF[2:]) + self.terminal_DCF()
         self.projected_equity_value = self.summed_dfcf + self.effective_cash_balance 
         self.intrinsic_val = self.projected_equity_value * 1e7 /self.diluted_shares_outstanding
         return self.intrinsic_val
                  
     
    
                      
    
it = intrinsicValue('BaseYear.csv','meansd.csv')
it.fair_value()



