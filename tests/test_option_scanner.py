from app.options.models import OptionContract
from app.options.scanner import OptionScanner


contracts = [

OptionContract(
"HAL",
"NEXT_MONTH",
4500,
"CE",
100,
700000,
1500000,
22,
0.45,
-3
),


OptionContract(
"HAL",
"NEXT_MONTH",
4600,
"CE",
120,
900000,
2500000,
24,
0.55,
-2
),


OptionContract(
"HAL",
"NEXT_MONTH",
4700,
"CE",
80,
300000,
800000,
35,
0.30,
-6
)

]


scanner = OptionScanner()


results = scanner.scan(
    contracts,
    "BUY"
)


for item in results:

    print(
        item["option"].strike,
        item["option"].option_type,
        item["score"]
    )