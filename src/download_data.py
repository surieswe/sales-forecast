# src/download_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create synthetic sales data
def generate_sales_data():
    # Generate dates for 3 years
    start_date = datetime(2021, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(1095)]
    
    # Generate sales with trend and seasonality
    trend = np.linspace(1000, 3000, len(dates))
    seasonality = 500 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    noise = np.random.normal(0, 200, len(dates))
    
    sales = trend + seasonality + noise
    sales = np.maximum(sales, 0)  # No negative sales
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales.round(2)
    })
    
    # Save to CSV
    df.to_csv('data/sales_data.csv', index=False)
    print("✅ Sample data created!")
    return df

if __name__ == "__main__":
    generate_sales_data()