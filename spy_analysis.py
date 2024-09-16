import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import os

def analyze_spy():
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

    # Initialize lists to store results
    results = []
    positive_count = 0
    negative_count = 0
    zero_count = 0
    negative_greater_than_ten_count = 0
    negative_greater_than_five_count = 0
    capital = 0
    gain = 2000
    put_sell_percent = 0.01
    spread_amount = 5
    spreads_sold = 20 

    # Iterate through the data
    for i in range(len(wed_fri) - 1):
        loss_amount = 0
        current_day = wed_fri.iloc[i]
        next_day = wed_fri.iloc[i + 1]
        
        if current_day['Day'] == 'Wednesday' and next_day['Day'] == 'Friday':
            wed_close = current_day['Close']
            fri_close = next_day['Close']
            difference = fri_close - wed_close
            #calc based on % below wed_close
            put_sell_price = wed_close - (wed_close * put_sell_percent)
            put_buy_price = put_sell_price - spread_amount
                     
            if difference > 0:
                positive_count += 1
                capital += gain
            elif difference < 0:
                negative_count += 1
                if fri_close <= put_buy_price:
                    loss_amount = spread_amount * spreads_sold * 100
                    negative_greater_than_ten_count += 1
                elif fri_close < put_sell_price:
                    loss_amount = (put_sell_price - fri_close) * spreads_sold * 100
                    negative_greater_than_five_count += 1
                else:
                    capital += gain
                capital -= loss_amount
            else:
                zero_count += 1

            results.append({
                'Wednesday': current_day['Date'].date(),
                'Friday': next_day['Date'].date(),
                'Wednesday Close': wed_close,
                'Friday Close': fri_close,
                'Difference': difference,
                'Capital': capital,
                'Loss': loss_amount,
                'Put Sold': put_sell_price,
                'Put Buy': put_buy_price
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Calculate average difference
    avg_difference = results_df['Difference'].mean()

    # Add average difference and counts to the DataFrame
    #results_df = results_df.concat({
    #    'Wednesday': 'Summary', 
    #    'Friday': '', 
    #    'Wednesday Close': '', 
    #    'Friday Close': '', 
    #    'Difference': f"Avg: {avg_difference:.2f}, Pos: {positive_count}, Neg: {negative_count}, Zero: {zero_count}"
    #}, ignore_index=True)

    # Output to CSV
    output_dir = '/app/output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'spy_analysis_results.csv')
    results_df.to_csv(output_file, index=False)
    print(f"Results have been saved to {output_file}")

    # Print results to console
    print(results_df.to_string(index=False))
    
    # Print summary
    total_comparisons = positive_count + negative_count + zero_count
    print(f"\nSummary:")
    print(f"Total Wednesday-Friday pairs analyzed: {total_comparisons}")
    print(f"Positive differences (Friday > Wednesday): {positive_count} ({positive_count/total_comparisons:.2%})")
    print(f"Negative differences (Friday < Wednesday): {negative_count} ({negative_count/total_comparisons:.2%})")
    print(f"Zero differences (Friday = Wednesday): {zero_count} ({zero_count/total_comparisons:.2%})")
    print(f"Average difference: ${avg_difference:.2f}")
    print(f"Max losses: {negative_greater_than_ten_count} ({negative_greater_than_ten_count/total_comparisons:.2%})")
    print(f"Losses: {negative_greater_than_five_count} ({negative_greater_than_five_count/total_comparisons:.2%})")
    print(f"Capital: ${capital}")

    #Calculate and print the median difference
    median_difference = results_df['Difference'].median()
    print(f"\nMedian difference: ${median_difference:.2f}")

    #Calculate and print the standard deviation difference
    std_difference = results_df['Difference'].std()
    print(f"\nStdDev difference: ${std_difference:.2f}")

    #Calculate and print the max difference
    max_difference = results_df['Difference'].max()
    print(f"\nMax difference: ${max_difference:.2f}")

    #Calculate and print the min difference
    min_difference = results_df['Difference'].min()
    print(f"\nMin difference: ${min_difference:.2f}")

if __name__ == "__main__":
    analyze_spy()