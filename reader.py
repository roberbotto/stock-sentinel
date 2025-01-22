import pandas as pd


def is_utility_stock(data):
    return data['SECTOR'] == 'Utilities'

def is_timelyten_stock(data):
    return all(
        [
            data['out'] <= 0.75 if is_utility_stock(data) else data['out'] <= 0.5,
            data['Debt'] <= 0.75 if is_utility_stock(data) else data['Debt'] <= 0.5,
            data['ROIC'] >= 0.1,
            data['FCFY'] >= 0.05,
            data['PVR'] <= 1.6,
            data['S&P'] in ('A+', 'A', 'A-'),
            data['P/E'] <= 15
        ]
    )

def is_feasible_stock(data):
    return all(
        [
            data['out'] <= 0.7,
            data['Debt'] <= 1.0,
            data['ROIC'] >= 0.1,
            data['FCFY'] >= 0.05,
            data['Yield'] >= 0.03,
            data.iloc[32] >= 0.05  # crecimiento dividendo los ultimos 5 años
        ]
    )

def is_high_yield_stock(data):
    return all(
        [
            data['out'] <= 0.9,
            data['Debt'] <= 1.0,
            data['ROIC'] >= 0.03,
            data['Yield'] >= 0.06,
        ]
    )

# Cargar el archivo Excel
df = pd.read_excel('data/iqtrends_report.xlsx')

# Eliminar las dos primeras filas
df_sin_filas = df.iloc[2:].reset_index(drop=True)
df_sin_filas.columns = df.iloc[1].values  # type: ignore

# Listas de datos
undervalue_stocks = []
other_stocks = []
feasible_stocks = []
high_yield_stocks = []

# Recorrer el DataFrame filtrado fila por fila
for index, row in df_sin_filas.iterrows():
    
    stock = f"{row['STOCK']} - {row['Tic']}"
    
    if is_timelyten_stock(row):
        if row.iloc[2] == 'U':
            undervalue_stocks.append(stock)
        else:
            other_stocks.append(stock)
    
    if is_feasible_stock(row):
        feasible_stocks.append(stock)
    
    if is_high_yield_stock(row):
        high_yield_stocks.append(stock)

print("TimelyTen (U):")
for i in undervalue_stocks:
    print(f"\t - {i}")

print("TimelyTen (Other):")
for i in other_stocks:
    print(f"\t - {i}")

print("Feasible Stocks:")
for i in feasible_stocks:
    print(f"\t - {i}")

print("Hihg-Yield Stocks:")
for i in high_yield_stocks:
    print(f"\t - {i}")