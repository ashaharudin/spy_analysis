import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy as np

def analyze_spy():
    #Starting capital
    cash = 10000
    #Target Premium
    PREMIUM = 1000
    #Target sell %
    #If target is 1%, SPY is at 500, aim to sell a put at 495
    SELL_PERCENT = 0.015
    #Spread size in dollars
    SPREAD = 5
    #Number of spreads
    SPREAD_COUNT = 20

    # Calculate date range (last 3 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1460)

    # Download SPY data
    spy = yf.Ticker("SPY")
    df = spy.history(start=start_date, end=end_date)

    # Reset index to make Date a column
    df = df.reset_index()

    # Convert Date to datetime if it's not already
    df['Date'] = pd.to_datetime(df['Date'])

    # Add day of week column
    df['Day'] = df['Date'].dt.day_name()

    # Filter for Wednesdays and Fridays
    wed_fri = df[df['Day'].isin(['Wednesday', 'Friday'])]

    # Sort by date
    wed_fri = wed_fri.sort_values('Date')

    #Separate dataframes for Wednesdays and Fridays
    wed_df = df[df['Day'].isin(['Wednesday'])]
    wed_df = wed_df.sort_values('Date')
    wed_df['Wednesday'] = wed_df['Date']
    wed_df = wed_df.rename(columns={'Open': 'Wednesday Open', 
                                    'High': 'Wednesday High',
                                    'Low': 'Wednesday Low',
                                    'Close': 'Wednesday Close'
                                    })
    wed_df['Wednesday Average'] = ((wed_df['Wednesday High'] + wed_df['Wednesday Low'])/2)
    fri_df = df[df['Day'].isin(['Friday'])]
    fri_df = fri_df.sort_values('Date')
    fri_df['Friday'] = fri_df['Date']
    fri_df = fri_df.rename(columns={'Open': 'Friday Open', 
                                    'High': 'Friday High',
                                    'Low': 'Friday Low',
                                    'Close': 'Friday Close'
                                    })
    fri_df['Friday Average'] = ((fri_df['Friday High'] + fri_df['Friday Low'])/2)
    
    #Copying the dataframes, as was unable to drop the extra Volume, Stock Split and Dividends columns for some reason. 
    wed_result_df = wed_df[['Date', 'Wednesday', 'Wednesday Open', 'Wednesday High', 'Wednesday Low', 'Wednesday Close', 'Wednesday Average']].copy()
    fri_result_df = fri_df[['Date', 'Friday', 'Friday Open', 'Friday High', 'Friday Low', 'Friday Close', 'Friday Average']].copy()
    
    #Using merge to match the Wednesdays with the next Friday
    result_df = pd.merge_asof(wed_result_df, fri_result_df, on='Date', direction='forward')
    #Using the average price to calculate delta between Friday and Wednesday
    result_df['Avg Difference'] = (result_df['Friday Average'] - result_df['Wednesday Average'])
    #Determine credit put spread based on target sell % and spread size
    result_df['Put Sold'] = (result_df['Wednesday Average'] - (result_df['Wednesday Average']*SELL_PERCENT)).apply(np.ceil)
    result_df['Put Buy'] = (result_df['Put Sold'] - SPREAD)
    #calculate Gain/Loss
    result_df['Gain/Loss'] = (
        np.select(
            condlist=[result_df['Friday Average'] <= result_df['Put Buy'],result_df['Friday Average'] < result_df['Put Sold']],
            choicelist=[SPREAD*SPREAD_COUNT*100*-1,PREMIUM-(result_df['Put Sold']-result_df['Friday Average'])*SPREAD_COUNT*100],
            default=PREMIUM
        ))

    print(result_df.to_string(index=False))

    # Output to CSV
    output_dir = '/app/output'
    os.makedirs(output_dir, exist_ok=True)
    result_file = os.path.join(output_dir, 'spy_analysis.csv')
    result_df.to_csv(result_file,index = False)

    # Print summary
    total_comparisons = result_df.shape[0]
    positive_count = (result_df['Avg Difference'] >= 0).sum()
    negative_count = (result_df['Avg Difference'] < 0).sum()
    mean_difference = result_df['Avg Difference'].mean()
    median_difference = result_df['Avg Difference'].median()
    std_difference = result_df['Avg Difference'].std()
    max_difference = result_df['Avg Difference'].max()
    min_difference = result_df['Avg Difference'].min()
    wins = (result_df['Friday Average'] >= result_df['Put Sold']).sum()
    losses = (result_df['Friday Average'] < result_df['Put Sold']).sum()
    max_losses = (result_df['Friday Average'] < result_df['Put Buy']).sum()
    remaining_cash = cash + result_df['Gain/Loss'].sum()
    print(f"\nSummary:")
    print(f"Total Wednesday-Friday pairs analyzed: {total_comparisons}")
    print(f"Positive differences (Friday > Wednesday): {positive_count} ({positive_count/total_comparisons:.2%})")
    print(f"Negative differences (Friday < Wednesday): {negative_count} ({negative_count/total_comparisons:.2%})")
    print(f"Mean difference: {mean_difference:.2f}")
    print(f"Median difference: {median_difference:.2f}")
    print(f"StdDev difference: {std_difference:.2f}")
    print(f"Max difference: {max_difference:.2f}")
    print(f"Min difference: ${min_difference:.2f}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Max Losses: {max_losses}")
    print(f"Cash remainder: ${remaining_cash:.2f}")

if __name__ == "__main__":
    analyze_spy()