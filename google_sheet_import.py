from datetime import date

import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# ---------------------------------------------------------------------------
# Google Sheets
# ---------------------------------------------------------------------------

def get_google_sheet_data():
    """Load and clean expense data from the Responses sheet."""

    service_account_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )

    SPREADSHEET_ID = "1CZ8w92CqJ2s5U95tMpqN_2pcfWwbc1ciLeIl8qM7RMc"
    RANGE_NAME = "Responses"

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes,
    )

    # Build the service
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
    ).execute()

    values = result.get("values", [])

    if not values:
        return pd.DataFrame(), pd.DataFrame()

    # Convert to DataFrame
    headers = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=headers)


    # -----------------------------------------------------------------------
    # Data types
    # -----------------------------------------------------------------------

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        format="%m/%d/%Y %H:%M:%S",
        errors="coerce",
    )

    df["Category"] = df["Category"].astype("string")
    df["Person"] = df["Person"].astype("string")
    df["Note"] = df["Note"].astype("string")

    df["Price"] = pd.to_numeric(
        df["Price"],
        errors="coerce",
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%m/%d/%Y",
        errors="coerce",
    )



    # -----------------------------------------------------------------------
    # Expense date
    # -----------------------------------------------------------------------

    purchase_col = "Date"

    purchase_raw = df[purchase_col].replace(
        ["", " ", "NA"],
        pd.NA,
    )

    purchase_dt = pd.to_datetime(
        purchase_raw,
        errors="coerce",
    )

    df["Date"] = (
        purchase_dt
        .fillna(df["Timestamp"])
        .dt.normalize()
    )

    return df 


# ---------------------------------------------------------------------------
# Both
# ---------------------------------------------------------------------------

def split_both_rows(df):
    """
    Split shared expenses: groceries 60/40, everything else 50/50.
    """

    rows = []

    for _, row in df.iterrows():
        person = str(row.get("Person", "")).strip().casefold()
        category = str(row.get("Category", "")).strip().casefold()

        if person == "both":
            jesse_share = 0.6 if category == "groceries" else 0.5

            for name, share in [
                ("Jesse", jesse_share),
                ("Bridget", 1 - jesse_share),
            ]:
                new_row = row.copy()
                new_row["Person"] = name
                new_row["Price"] = row["Price"] * share
                rows.append(new_row)
        else:
            rows.append(row.copy())

    return pd.DataFrame(rows, columns=df.columns).reset_index(drop=True)


def add_nzd_converted_column(df):
    """Convert each row's yen price to NZD using its date."""
    df = df.copy()

    df["Price NZD"] = pd.Series(
        pd.NA, index=df.index, dtype="Float64"
    )

    if df.empty:
        return df

    @lru_cache(maxsize=None)
    def get_rate(expense_date):
        response = requests.get(
            "https://api.frankfurter.dev/v2/rates",
            params={
                "base": "JPY",
                "quotes": "NZD",
                "date": expense_date,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return float(data[0]["rate"]) if data else pd.NA

    def convert_row(row):
        expense_date = pd.to_datetime(row["Date"], errors="coerce")
        price = pd.to_numeric(row["Price"], errors="coerce")

        if pd.isna(expense_date) or pd.isna(price):
            return pd.NA

        if expense_date.date() > date.today():
            return pd.NA

        rate = get_rate(expense_date.strftime("%Y-%m-%d"))
        return price * rate

    df["Price NZD"] = df.apply(convert_row, axis=1).astype("Float64")

    return df

# ---------------------------------------------------------------------------
# Final processed dataset
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_processed_data():
    df_full = get_google_sheet_data()

    df_both_split = split_both_rows(
        df_full
    )



    df_final = add_nzd_converted_column(
        df_both_split
    )

    
    return df_final
