# Data dictionary

## `data/prices.csv`

| Column | Description |
|---|---|
| `date` | Business date |
| `US_Equity` | Synthetic equity index level |
| `Tech_Equity` | Synthetic technology equity index level |
| `Gov_Bond` | Synthetic government-bond index level |
| `Corporate_Bond` | Synthetic corporate-bond index level |
| `USD_INR` | Synthetic USD/INR-style FX index level |
| `Gold` | Synthetic gold index level |

## `data/portfolio.csv`

| Column | Description |
|---|---|
| `asset` | Asset identifier matching `prices.csv` |
| `asset_class` | Broad asset class |
| `position_value_cr` | Synthetic position value in INR crore |
