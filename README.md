
# 📈 Real-Time Stock Market Dashboard

A Python-based interactive stock market dashboard built using Streamlit. It allows users to explore stock prices, historical trends, trading volume, and financial indicators.

## 🚀 Features

- Search stocks using ticker symbols (AAPL, MSFT, GOOGL, etc.).
- Select different historical time periods.
- Display latest available stock price.
- Show previous closing price.
- Calculate 20-Day Moving Average.
- Calculate Relative Strength Index (RSI).
- Interactive historical stock price charts.
- Trading volume visualization.
- Export stock data as CSV.
- Fetch company information using Yahoo Finance API.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- yfinance
- Requests API
- NumPy

## 📂 Project Structure

```text
Stock_Market_Dashboard/
│
├── app.py
├── requirements.txt
├── README.md
└── .venv/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Stock_Market_Dashboard.git
```

### 2. Open the project folder

```bash
cd Stock_Market_Dashboard
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app.py
```

The dashboard will open in your browser at:

http://localhost:8501

## 📊 Stock Indicators

| Indicator | Description |
|---|---|
| Latest Price | Latest available stock price |
| Previous Close | Previous closing price |
| Moving Average | 20-day average price |
| RSI | Relative Strength Index |
| Trading Volume | Number of shares traded |

## 📡 Data Sources

- Yahoo Finance through yfinance for historical stock market data.
- Yahoo Finance search endpoint through Python Requests for company information.

## ⚠️ Disclaimer

This project is developed for educational purposes only. Stock market data may be delayed or incomplete. It does not provide financial advice or investment recommendations.

## 👨‍💻 Author

Developed as part of a Python internship project.
