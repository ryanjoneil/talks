import csv
import pandas

raw_data = [row for row in csv.reader(open('2017-03-09-FRB_H10.csv'))]

# Transpose header metadata and turn it into a data frame.
head_data = [[] for _ in range(len(raw_data[0]))]
for row in raw_data[:6]:
    for j, val in enumerate(row):
        head_data[j].append(val)
    
metadata = pandas.DataFrame.from_records(data=head_data[1:], columns=head_data[0])

# Filter out NA currencies.
metadata = metadata[metadata['Currency:'] != 'NA']

# This will have the same indices as the rest of the metadata.
countries = []
for c in metadata['Series Description']:
    c = c.upper()
    c = c.split(' -- ')[0]
    c = c.split(' - ')[0]
    countries.append(c)
countries[1] = 'EURO AREA'
countries

# Compute exchange rates.
exchange_rates = pandas.DataFrame.from_records(data=raw_data[6:], columns=raw_data[5])
exchange_rates = exchange_rates[['Time Period'] + list(metadata['Time Period'])]

# Convert the exchange rate data frame into percentage returns.
rows = []
for i in range(len(exchange_rates)-1):
    row = {}
    for tp, cur in zip(metadata['Time Period'], metadata['Currency:']):
        x1 = float(exchange_rates[tp][i])
        x2 = float(exchange_rates[tp][i+1])
    
        if cur == 'USD':
            x1 = 1.0 / x1
            x2 = 1.0 / x2
        
        # Returns are in units of %.
        row[tp] = 100 * (x1 - x2) / x2
    rows.append(row)

returns = pandas.DataFrame(data=rows, columns=list(metadata['Time Period']))

# Means are the expected returns for each currency.
exp_returns = pandas.concat({'mean': returns.mean(), 'variance': returns.var()}, axis=1)

# Get the covariance matrix for our returns. This is normalized by N-1.
returns_cov = returns.cov()

exp_returns.to_csv('currency-returns.csv')
returns_cov.to_csv('currency-covariance.csv')
