#!/usr/bin/env python3
"""
Revenue Math Calculator - Backwards Revenue Planning
Source: ALPHA009 - "$30k/mo = 309 sales @ $97 = 11 sales/day"
Also: ALPHA010 - Email flash sale tactic
Also: ALPHA307 - Pricing optimization 25-60% revenue increase

Works backwards from target revenue to exact traffic/conversion needed.

Usage:
    python3 revenue_math_calculator.py --target 10000 --price 39
    python3 revenue_math_calculator.py --target 30000 --price 97 --traffic-type warm
    python3 revenue_math_calculator.py --scenario-analysis
    python3 revenue_math_calculator.py --flash-sale --list-size 500 --price 97
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "OPS"

# Conversion rates by traffic temperature
CONVERSION_RATES = {
    "cold": {
        "rate": 0.01,
        "description": "Cold traffic (ads, cold email, SEO)",
        "source": "ALPHA009 - @knoxtwts",
    },
    "warm": {
        "rate": 0.025,
        "description": "Warm traffic (social followers, email subscribers)",
        "source": "ALPHA009 - @knoxtwts",
    },
    "hot": {
        "rate": 0.05,
        "description": "Hot traffic (past customers, engaged list)",
        "source": "ALPHA009 - @knoxtwts",
    },
    "flash_sale": {
        "rate": 0.10,
        "description": "Flash sale to warmed list (15-30 days value first)",
        "source": "ALPHA010 - $15-45k from 200 subs",
    },
}

# Price points and their characteristics
PRICE_TIERS = {
    "impulse": {"range": "$9-29", "avg": 19, "refund_rate": 0.02, "conv_multiplier": 1.5},
    "low": {"range": "$29-49", "avg": 39, "refund_rate": 0.03, "conv_multiplier": 1.2},
    "mid": {"range": "$49-97", "avg": 67, "refund_rate": 0.04, "conv_multiplier": 1.0},
    "premium": {"range": "$97-297", "avg": 197, "refund_rate": 0.05, "conv_multiplier": 0.7},
    "high_ticket": {"range": "$297-997", "avg": 497, "refund_rate": 0.06, "conv_multiplier": 0.4},
    "subscription_monthly": {"range": "$9-49/mo", "avg": 29, "refund_rate": 0.08, "conv_multiplier": 0.8},
    "subscription_annual": {"range": "$97-497/yr", "avg": 197, "refund_rate": 0.03, "conv_multiplier": 0.5},
}


def calculate_revenue_math(target_monthly, price, traffic_type="warm"):
    """Calculate exact requirements to hit revenue target."""
    conv = CONVERSION_RATES.get(traffic_type, CONVERSION_RATES["warm"])
    rate = conv["rate"]

    sales_needed = target_monthly / price
    daily_sales = sales_needed / 30
    daily_visitors = daily_sales / rate
    monthly_visitors = daily_visitors * 30

    # Multi-account strategy (ALPHA009)
    accounts_5 = monthly_visitors / 5 if monthly_visitors > 0 else 0
    accounts_10 = monthly_visitors / 10 if monthly_visitors > 0 else 0

    return {
        "target_monthly": target_monthly,
        "price": price,
        "traffic_type": traffic_type,
        "conversion_rate": rate,
        "sales_needed_monthly": round(sales_needed, 1),
        "sales_needed_daily": round(daily_sales, 1),
        "visitors_needed_daily": round(daily_visitors),
        "visitors_needed_monthly": round(monthly_visitors),
        "impression_to_visitor": {
            "at_2pct_ctr": round(monthly_visitors / 0.02),
            "at_5pct_ctr": round(monthly_visitors / 0.05),
        },
        "multi_account": {
            "visitors_per_account_5": round(accounts_5),
            "visitors_per_account_10": round(accounts_10),
        },
    }


def calculate_flash_sale(list_size, price, warmup_days=20):
    """Calculate flash sale potential (ALPHA010)."""
    # Flash sale conversion rates based on list warmth
    if warmup_days >= 30:
        rate = 0.15
        tier = "hot"
    elif warmup_days >= 20:
        rate = 0.10
        tier = "warm"
    elif warmup_days >= 10:
        rate = 0.06
        tier = "lukewarm"
    else:
        rate = 0.03
        tier = "cold"

    sales = list_size * rate
    revenue = sales * price

    return {
        "list_size": list_size,
        "price": price,
        "warmup_days": warmup_days,
        "list_temperature": tier,
        "conversion_rate": rate,
        "estimated_sales": round(sales),
        "estimated_revenue": round(revenue),
        "revenue_range": {
            "conservative": round(revenue * 0.5),
            "base": round(revenue),
            "optimistic": round(revenue * 1.5),
        },
        "reference": "ALPHA010: $15-45k from 200 subs with 15-30 days warmup",
    }


def scenario_analysis():
    """Run full scenario analysis across price points and traffic types."""
    targets = [1000, 5000, 10000, 30000, 50000, 100000]
    prices = [19, 39, 67, 97, 197, 497]

    print(f"\n{'='*80}")
    print("REVENUE MATH - SCENARIO ANALYSIS")
    print(f"{'='*80}")
    print(f"Source: ALPHA009 (@knoxtwts revenue math framework)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")

    for traffic_type in ["cold", "warm", "hot"]:
        conv = CONVERSION_RATES[traffic_type]
        print(f"\n{'='*80}")
        print(f"  TRAFFIC TYPE: {traffic_type.upper()} ({conv['description']})")
        print(f"  Conversion Rate: {conv['rate']*100}%")
        print(f"{'='*80}\n")

        print(f"{'Target':>10} | {'Price':>6} | {'Sales/mo':>9} | {'Sales/day':>9} | {'Visitors/day':>12} | {'Visitors/mo':>12}")
        print("-" * 80)

        for target in targets:
            for price in prices:
                result = calculate_revenue_math(target, price, traffic_type)
                if result["visitors_needed_daily"] <= 50000:  # Only show realistic ones
                    print(f"${target:>8,} | ${price:>4} | {result['sales_needed_monthly']:>8.0f} | {result['sales_needed_daily']:>8.1f} | {result['visitors_needed_daily']:>11,} | {result['visitors_needed_monthly']:>11,}")
            print("-" * 80)

    # Flash sale scenarios
    print(f"\n{'='*80}")
    print("FLASH SALE SCENARIOS (ALPHA010)")
    print(f"{'='*80}")
    print("15-30 days value emails, then 1 flash sale = $15-45K in 48 hours\n")

    for list_size in [200, 500, 1000, 2000, 5000, 10000]:
        for price in [29, 47, 97, 197]:
            result = calculate_flash_sale(list_size, price, warmup_days=20)
            print(f"  List: {list_size:>6,} | Price: ${price:>4} | Est Revenue: ${result['estimated_revenue']:>8,} ({result['revenue_range']['conservative']:,}-{result['revenue_range']['optimistic']:,})")
        print()


def pricing_optimization_analysis():
    """Show pricing optimization potential (ALPHA307)."""
    print(f"\n{'='*60}")
    print("PRICING OPTIMIZATION ANALYSIS")
    print(f"{'='*60}")
    print("Source: ALPHA307 - 25-60% revenue increase from pricing alone")
    print("Pricing optimization is 2-4x more impactful than acquisition\n")

    current_scenarios = [
        {"name": "Micro info product", "price": 29, "monthly_sales": 100},
        {"name": "Premium template", "price": 67, "monthly_sales": 50},
        {"name": "Course/workshop", "price": 197, "monthly_sales": 20},
        {"name": "SaaS subscription", "price": 29, "monthly_sales": 200},
    ]

    for scenario in current_scenarios:
        current_rev = scenario["price"] * scenario["monthly_sales"]
        print(f"\n  {scenario['name']}:")
        print(f"  Current: ${scenario['price']} x {scenario['monthly_sales']} = ${current_rev:,}/mo")

        for increase_pct in [25, 40, 60]:
            new_rev = round(current_rev * (1 + increase_pct / 100))
            print(f"  +{increase_pct}% optimization: ${new_rev:,}/mo (+${new_rev - current_rev:,})")

    print(f"\n  Key tactics (from alpha):")
    print(f"  - Animated paywalls: 2.9x conversion (ALPHA032)")
    print(f"  - Annual plans: 2.6x higher retention (ALPHA034)")
    print(f"  - Personalized name: +17% conversion (ALPHA035)")
    print(f"  - Dynamic discounts: +35% conversion (ALPHA036)")
    print(f"  - Contextual timing: 50% of trials start in onboarding (ALPHA033)")
    print(f"  - Credit/usage models: 126% YoY growth (ALPHA308)")


def main():
    parser = argparse.ArgumentParser(description="Revenue Math Calculator")
    parser.add_argument("--target", type=float, help="Monthly revenue target ($)")
    parser.add_argument("--price", type=float, help="Product price ($)")
    parser.add_argument("--traffic-type", type=str, default="warm", choices=["cold", "warm", "hot", "flash_sale"])
    parser.add_argument("--scenario-analysis", action="store_true", help="Run full scenario analysis")
    parser.add_argument("--flash-sale", action="store_true", help="Calculate flash sale potential")
    parser.add_argument("--list-size", type=int, default=500, help="Email list size for flash sale")
    parser.add_argument("--warmup-days", type=int, default=20, help="Days of value before flash sale")
    parser.add_argument("--pricing", action="store_true", help="Show pricing optimization analysis")
    args = parser.parse_args()

    if args.scenario_analysis:
        scenario_analysis()
        pricing_optimization_analysis()
    elif args.flash_sale:
        result = calculate_flash_sale(args.list_size, args.price or 97, args.warmup_days)
        print(f"\n{'='*50}")
        print("FLASH SALE CALCULATOR")
        print(f"{'='*50}")
        print(f"List size: {result['list_size']:,}")
        print(f"Price: ${result['price']}")
        print(f"Warmup days: {result['warmup_days']}")
        print(f"Temperature: {result['list_temperature']}")
        print(f"Conv rate: {result['conversion_rate']*100}%")
        print(f"Est. sales: {result['estimated_sales']}")
        print(f"Est. revenue: ${result['estimated_revenue']:,}")
        print(f"Range: ${result['revenue_range']['conservative']:,} - ${result['revenue_range']['optimistic']:,}")
    elif args.pricing:
        pricing_optimization_analysis()
    elif args.target and args.price:
        result = calculate_revenue_math(args.target, args.price, args.traffic_type)
        print(f"\n{'='*50}")
        print("REVENUE MATH")
        print(f"{'='*50}")
        print(f"Target: ${result['target_monthly']:,.0f}/mo")
        print(f"Price: ${result['price']}")
        print(f"Traffic: {result['traffic_type']} ({result['conversion_rate']*100}% conv)")
        print(f"\nSales needed: {result['sales_needed_monthly']:.0f}/mo ({result['sales_needed_daily']:.1f}/day)")
        print(f"Visitors needed: {result['visitors_needed_daily']:,}/day ({result['visitors_needed_monthly']:,}/mo)")
        print(f"\nImpressions needed (at 2% CTR): {result['impression_to_visitor']['at_2pct_ctr']:,}/mo")
        print(f"Impressions needed (at 5% CTR): {result['impression_to_visitor']['at_5pct_ctr']:,}/mo")
        print(f"\nWith 5 accounts: {result['multi_account']['visitors_per_account_5']:,} visitors per account")
        print(f"With 10 accounts: {result['multi_account']['visitors_per_account_10']:,} visitors per account")
    else:
        scenario_analysis()
        pricing_optimization_analysis()


if __name__ == "__main__":
    main()
