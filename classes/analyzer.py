from log import logging
import numpy as np
import numpy_financial as npf
import pandas as pd


logger = logging.getLogger('analyzer.py')

class Analyzer:
    def __init__(self):
        pass

    def calculate_irr(self, arr):
        return npf.irr(arr)


    def create_valuation_at_sale(self, property_data):
        annual_cashflow_df = property_data["cashflow"]["annual_cash_flow_df"]
        noi_year_6 = annual_cashflow_df.loc["net_operating_income", 6]
        sale_price = max( noi_year_6 / property_data["assumptions"]["inputs"]["cap_rate"] ,  property_data["assumptions"]["inputs"]["purchase_price"] * 1.10 )
        mortgage_balance_eoy_5 = property_data["amortization_schedule"]["amort_schedule_df"].loc["balance", 5*12]
        net_sales_proceeds = sale_price - mortgage_balance_eoy_5
        return { "noi_year_6": noi_year_6, "sale_price": sale_price, "mortgage_balance_eoy_5": mortgage_balance_eoy_5, "net_sales_proceeds": net_sales_proceeds }
    

    def create_unleveraged_return_analysis_df(self, property_data):
        annual_cashflow_df = property_data["cashflow"]["annual_cash_flow_df"]
        indices = ["purchase", "cash_flow_operations", "cash_flow_sale", "totals"]
        df = pd.DataFrame()
        df = df.set_axis(indices)
        for i in range(6):
            df[i] = np.nan
        for i, r in df.iterrows():
            for col in df:
                v = None
                if col == 0 and i == "purchase":
                    v = -1 * (property_data["assumptions"]["inputs"]["purchase_price"] + (property_data["assumptions"]["inputs"]["closing_costs"] * property_data["assumptions"]["inputs"]["purchase_price"]))
                if col > 0 and i == "cash_flow_operations":
                    v = annual_cashflow_df.loc["net_operating_income", col]
                if col == 5 and i == "cash_flow_sale":
                     v = property_data["analysis"]["valuation_at_sale"]["sale_price"]
                if i == "totals":
                    v = df[col].sum()
                df.loc[i, col] = v
        return df

    
    def create_leveraged_return_analysis_df(self, property_data):
        annual_cashflow_df = property_data["cashflow"]["annual_cash_flow_df"]
        indices = ["purchase", "cash_flow_operations", "cash_flow_sale", "totals"]
        df = pd.DataFrame()
        df = df.set_axis(indices)
        for i in range(6):
            df[i] = np.nan
        for i, r in df.iterrows():
            for col in df:
                v = 0
                if col == 0 and i == "purchase":
                    v = -1 * ((property_data["assumptions"]["inputs"]["purchase_price"] * (1 - property_data["assumptions"]["inputs"]["loan_amount"]) ) + (property_data["assumptions"]["inputs"]["closing_costs"] * property_data["assumptions"]["inputs"]["purchase_price"]))
                if col > 0 and i == "cash_flow_operations":
                    v = annual_cashflow_df.loc["cash_flow_after_debt_service", col]
                if col == 5 and i == "cash_flow_sale":
                     v = property_data["analysis"]["valuation_at_sale"]["net_sales_proceeds"]
                if i == "totals":
                    v = df[col].sum()
                df.loc[i, col] = v
        return df
    

    def create_return_analysis(self, unleveraged_return_analysis_df, leveraged_return_analysis_df):
        return {
            "unleveraged_irr": self.calculate_irr(list(unleveraged_return_analysis_df.loc["totals"])),
            "leveraged_irr": self.calculate_irr(list(leveraged_return_analysis_df.loc["totals"]))
        }