"""
Author: Siddhant Mahajani
Project: Cohort Customer Retention Analysis
Date: 25th January 2022
"""

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns

import warnings

warnings.filterwarnings('ignore')

transaction_df = pd.read_excel("data/retail.xlsx")
print(transaction_df.head())

print(transaction_df.info())
print(transaction_df.isnull().sum())

transaction_df = transaction_df.dropna(subset=['CustomerID'])
print(transaction_df.duplicated().sum())
transaction_df = transaction_df.drop_duplicates()
print(transaction_df.describe())

transaction_df = transaction_df[(transaction_df['Quantity'] > 0) & (transaction_df['UnitPrice'] > 0)]


def get_month(x): return dt.datetime(x.year, x.month, 1)


transaction_df['InvoiceMonth'] = transaction_df['InvoiceDate'].apply(get_month)
grouping = transaction_df.groupby('CustomerID')['InvoiceMonth']
transaction_df['CohortMonth'] = grouping.transform('min')


def get_month_int(dframe, col):
    year = dframe[col].dt.year
    month = dframe[col].dt.month
    day = dframe[col].dt.day
    return year, month, day


invoice_year, invoice_month, _ = get_month_int(transaction_df, 'InvoiceMonth')
cohort_year, cohort_month, _ = get_month_int(transaction_df, 'CohortMonth')

year_difference = invoice_year - cohort_year
month_difference = invoice_month - cohort_month

transaction_df['CohortIndex'] = year_difference * 12 + month_difference + 1

grouping = transaction_df.groupby(['CohortMonth', 'CohortIndex'])
cohort_data = grouping['CustomerID'].apply(pd.Series.nunique)
cohort_data = cohort_data.reset_index()
cohort_counts = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')

cohort_size = cohort_counts.iloc[:, 0]
retention = cohort_counts.divide(cohort_size, axis=0)
retention.round(3) * 100

plt.figure(figsize=(15, 8))
plt.title('Retention rates')
sns.heatmap(data=retention, annot=True, fmt='.0%', vmin=0.0, vmax=0.5, cmap='BuPu_r')
plt.show()
