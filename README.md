SPY_analysis

Simple script to determine historical profitability (or not) of opening 3 DTE put credit spreads or credit iron condors on SPY. 

Some rules/assumptions:

Spreads are sold on Wednesday and let to expire on Friday on the same day, based on casual observation of increased volatility Wednesday with the presumption of lower volatity on Friday.

Assuming a fixed target for the premiums received.

Strike prices selected are based on a percentage of the closing date on Wednesday

Instructions:

1. docker build -t spy-analysis .
2. docker run -v $(pwd)/spy_output:/app/output spy-analysis


Issues:

Containerized as I'm having issues with loading pandas module directly.

Todo:
- Input variables
- dataframe optimization
- Use a different data set that includes either average or lowest prices for the day instead of closing price

