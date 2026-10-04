import pandas as pd

def run_analysis(df):
    results = {}

    results['total_parcels'] = len(df)
    results['total_spend'] = round(df['Carrier Cost'].sum(), 2)
    results['avg_cost'] = round(df['Carrier Cost'].mean(), 2)
    results['avg_weight'] = round(df['Parcel Weight - lbs'].mean(), 2)
    results['ontime_rate'] = round((df['Delivery Status'] == 'On Time').mean() * 100, 1)

    results['carrier_summary'] = df.groupby('Carrier').agg(
        Volume=('Carrier Cost', 'count'),
        Total_Spend=('Carrier Cost', 'sum'),
        Avg_Cost=('Carrier Cost', 'mean'),
        OnTime_Pct=('Delivery Status', lambda x: round((x == 'On Time').mean() * 100, 1))
    ).round(2).reset_index()

    results['zone_summary'] = df.groupby('Zone').agg(
        Volume=('Carrier Cost', 'count'),
        Total_Spend=('Carrier Cost', 'sum')
    ).round(2).reset_index()

    results['service_summary'] = df.groupby('Service Level').agg(
        Volume=('Carrier Cost', 'count'),
        Total_Spend=('Carrier Cost', 'sum')
    ).round(2).reset_index()

    results['dim_count'] = len(df[df['DIM Weight Applied'] == 'Y'])
    results['dim_pct'] = round(results['dim_count'] / len(df) * 100, 1)

    results['residential_count'] = len(df[df['Residential Flag'] == 'Y'])
    results['residential_pct'] = round(results['residential_count'] / len(df) * 100, 1)

    results['top_states'] = df['Destination State/Province'].value_counts().head(10).reset_index()
    results['top_states'].columns = ['State', 'Volume']

    return results
