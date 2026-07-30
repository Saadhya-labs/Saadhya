from app.data.market_data import MarketData


def main():
    print("=" * 45)
    print("           SAADHYA AI")
    print("=" * 45)

    symbol = input("Enter Stock Symbol (e.g. RELIANCE.NS): ").strip().upper()

    print("\nDownloading market data...\n")

    market = MarketData()
    df = market.get_history(symbol)

    if df.empty:
        print("No data found for the symbol.")
        return

    latest = df.iloc[-1]

    print("=" * 45)
    print(f"Stock         : {symbol}")
    print(f"Date          : {latest['Date'].date()}")
    print(f"Open          : ₹{latest['Open']:.2f}")
    print(f"High          : ₹{latest['High']:.2f}")
    print(f"Low           : ₹{latest['Low']:.2f}")
    print(f"Close         : ₹{latest['Close']:.2f}")
    print(f"Volume        : {int(latest['Volume']):,}")
    print("=" * 45)


if __name__ == "__main__":
    main()