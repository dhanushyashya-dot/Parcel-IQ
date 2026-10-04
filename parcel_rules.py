import pandas as pd

def run_rules(df):
    recommendations = []

    fedex_ups_under30 = df[
        (df['Carrier'].isin(['FedEx', 'UPS'])) &
        (df['Parcel Weight - lbs'] <= 30)
    ]
    if len(fedex_ups_under30) > 0:
        current_spend = fedex_ups_under30['Carrier Cost'].sum()
        savings = round(current_spend * 0.50, 2)
        recommendations.append({
            'rule': 'Carrier Cost Optimization',
            'finding': f"{len(fedex_ups_under30)} parcels on FedEx/UPS under 30 lbs. Current spend: ${round(current_spend, 2)}",
            'recommendation': f"Switch to Maersk Parcel Standard. 50% cheaper with regional last-mile (GLS, OnTrac, LSO, UniUni, GOFO). Estimated savings: ${savings}",
            'parcels_affected': len(fedex_ups_under30),
            'estimated_savings': savings
        })

    long_zone_expedited = df[
        (df['Zone'] >= 7) &
        (df['Service Level'].isin(['2-Day', 'Overnight'])) &
        (df['Carrier'].isin(['FedEx', 'UPS']))
    ]
    if len(long_zone_expedited) > 0:
        spend = long_zone_expedited['Carrier Cost'].sum()
        savings = round(spend * 0.40, 2)
        recommendations.append({
            'rule': 'Zone 7-9 Expedited Optimization',
            'finding': f"{len(long_zone_expedited)} expedited parcels in Zone 7-9. Spend: ${round(spend, 2)}",
            'recommendation': f"Switch to Maersk Expedited for time-sensitive Zone 7-9 shipments. Estimated savings: ${savings}",
            'parcels_affected': len(long_zone_expedited),
            'estimated_savings': savings
        })

    service_mismatch = df[
        (df['Zone'] <= 4) &
        (df['Service Level'].isin(['2-Day', 'Overnight']))
    ]
    if len(service_mismatch) > 0:
        spend = service_mismatch['Carrier Cost'].sum()
        savings = round(spend * 0.30, 2)
        recommendations.append({
            'rule': 'Service Level Right-sizing',
            'finding': f"{len(service_mismatch)} parcels using expedited service for Zone 1-4. Unnecessary premium spend: ${round(spend, 2)}",
            'recommendation': f"Downgrade to Ground service for Zone 1-4. Estimated savings: ${savings}",
            'parcels_affected': len(service_mismatch),
            'estimated_savings': savings
        })

    dim_triggered = df[df['DIM Weight Applied'] == 'Y']
    if len(dim_triggered) > 0:
        excess = (dim_triggered['Chargeable Weight - lbs'] - dim_triggered['Parcel Weight - lbs']).sum()
        recommendations.append({
            'rule': 'DIM Weight / Packaging Audit',
            'finding': f"{len(dim_triggered)} parcels billed on DIM weight. Total excess weight charged: {round(excess, 1)} lbs",
            'recommendation': "Audit packaging. Switch to poly mailers for soft goods. Right-size boxes.",
            'parcels_affected': len(dim_triggered),
            'estimated_savings': 0
        })

    carrier_zone_perf = df.groupby(['Carrier', 'Zone']).apply(
        lambda x: round((x['Delivery Status'] == 'On Time').mean() * 100, 1)
    ).reset_index()
    carrier_zone_perf.columns = ['Carrier', 'Zone', 'OnTime_Pct']
    underperforming = carrier_zone_perf[carrier_zone_perf['OnTime_Pct'] < 80]
    if len(underperforming) > 0:
        for _, row in underperforming.iterrows():
            recommendations.append({
                'rule': 'Carrier Performance Alert',
                'finding': f"{row['Carrier']} Zone {row['Zone']}: {row['OnTime_Pct']}% on-time (below 80% threshold)",
                'recommendation': f"Reduce volume with {row['Carrier']} in Zone {int(row['Zone'])}. Shift to better performing carrier.",
                'parcels_affected': len(df[(df['Carrier'] == row['Carrier']) & (df['Zone'] == row['Zone'])]),
                'estimated_savings': 0
            })

    return recommendations
