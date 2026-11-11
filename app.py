#Required packages and whatnot
import json
import os

from datetime import date, datetime
from xmlrpc.client import Transport

from google_sheet_import import load_processed_data
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


from faicons import icon_svg
import plotly.express as px
import plotly.io as pio

# Load data and compute static values
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui, app

import plotly.graph_objs as go

# importing data
df_full = load_processed_data()

df_data = reactive.value(df_full)


# ================================================================================================================================
# UI
# ================================================================================================================================

ui.tags.style("""
.bslib-value-box {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px;
    min-height: 92px;
    padding: 10px 12px;
}

.bslib-value-box .value-box-showcase {
    order: 0;
    flex-shrink: 0;
    margin: 0;
    width: 70px !important;
    height: 70px !important;
}

.bslib-value-box .value-box-showcase img {
    width: 100% !important;
    height: 100% !important;
}

.bslib-value-box .value-box-area {
    order: 1;
    flex: 1;
    min-width: 0;
}

.sidebar {
    padding: 12px !important;
}

@media (max-width: 768px) {
    .bslib-value-box {
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px;
        padding: 8px 10px;
        min-height: 78px;
    }

    .bslib-value-box .value-box-showcase {
        width: 56px !important;
        height: 56px !important;
        flex-shrink: 0;
        margin: 0;
    }

    .bslib-value-box .value-box-area {
        width: auto;
        flex: 1;
    }

    .bslib-value-box .value-box-area .value-box-title,
    .bslib-value-box .value-box-area .value-box-value {
        font-size: 1.25rem;
        line-height: 1.2;
    }

    .shiny-input-container {
        margin-bottom: 8px;
    }

    .form-group, .checkboxgroup, .radio-buttons {
        font-size: 0.95rem;
    }
}

@media (max-width: 480px) {
    .bslib-value-box {
        flex-direction: row !important;
        align-items: center !important;
        gap: 6px;
        padding: 6px 8px;
        min-height: 60px;
    }

    .bslib-value-box .value-box-showcase {
        width: 44px !important;
        height: 44px !important;
        flex-shrink: 0;
        margin: 0;
    }

    .bslib-value-box .value-box-showcase img {
        width: 44px !important;
        height: 44px !important;
        margin-top: 0 !important;
    }

    .bslib-value-box .value-box-area {
        width: auto;
        flex: 1;
    }

    .bslib-value-box .value-box-area .value-box-title {
        font-size: 0.85rem;
        line-height: 1.1;
    }

    .bslib-value-box .value-box-area .value-box-value {
        font-size: 1rem;
        line-height: 1.1;
    }
}

.weekly-summary .card {
    margin-bottom: 12px;
}

.weekly-summary {
    max-width: 520px;
    margin: 0 auto;
    padding: 16px;
    background: #ffffff;
    border: 1px solid #e8eaed;
    border-radius: 18px;
    box-shadow: 0 3px 14px rgba(0, 0, 0, 0.06);
}

.weekly-summary .bslib-value-box,
.weekly-summary .weekly-category-card,
.weekly-summary .weekly-donut-card {
    margin-left: 0;
    margin-right: 0;
    border: 0;
    box-shadow: none;
    background: transparent;
}

.weekly-summary .bslib-value-box {
    padding-left: 0;
    padding-right: 0;
}

.weekly-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 8px 24px;
    margin-bottom: 12px;
}

.weekly-controls .shiny-input-container {
    width: auto;
    margin: 0;
}

.weekly-summary .data-frame,
.weekly-summary .shiny-data-frame {
    overflow-x: auto;
}

@media (max-width: 576px) {
    .weekly-summary {
        margin: 0;
        padding: 12px;
        border-radius: 14px;
    }

    .weekly-summary .bslib-value-box {
        min-height: 68px;
        padding: 8px 10px;
        margin-bottom: 8px;
    }

    .weekly-summary .bslib-value-box .value-box-title {
        font-size: 0.8rem;
    }

    .weekly-summary .bslib-value-box .value-box-value {
        font-size: 1.1rem;
    }

    .weekly-summary .card-body {
        padding: 10px;
    }

    .weekly-controls {
        gap: 6px 14px;
    }

    .weekly-summary .form-check-inline,
    .weekly-summary .radio-inline {
        display: block;
        margin: 0 0 6px 0;
    }

    .weekly-summary .js-plotly-plot {
        width: 100% !important;
    }
}

.weekly-donut-card {
    max-width: 360px;
    margin: 12px auto;
}

.weekly-donut-title {
    text-align: center;
    margin: 4px 0 0;
    font-size: 1rem;
}

.weekly-donut-card img {
    width: 100%;
    height: auto;
    display: block;
}

.weekly-category-card {
    display: block;
    max-width: 420px;
    margin: 12px auto;
}

.weekly-category-title {
    margin: 0 0 8px;
    font-size: 1rem;
    font-weight: 600;
}

.weekly-category-row {
    display: grid;
    grid-template-columns: 12px minmax(0, 1fr) auto;
    align-items: center;
    gap: 10px;
    padding: 11px 0;
    border-bottom: 1px solid #edf0f2;
}

.weekly-category-row:last-child {
    border-bottom: 0;
}

.weekly-category-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.weekly-category-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.weekly-category-value {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

.weekly-category-total {
    margin-bottom: 4px;
    padding: 12px 10px;
    background: #f4f7f8;
    border: 0;
    border-radius: 10px;
}

.weekly-category-total .weekly-category-name,
.weekly-category-total .weekly-category-value {
    font-weight: 700;
}

.weekly-category-total-marker {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #212529;
}

.weekly-transactions {
    margin-top: 12px;
    border-top: 1px solid #edf0f2;
}

.weekly-transactions summary {
    padding: 12px 0;
    cursor: pointer;
    font-weight: 600;
    color: #343a40;
}

.weekly-transactions[open] summary {
    border-bottom: 1px solid #edf0f2;
    margin-bottom: 10px;
}

@media (max-width: 576px) {
    .weekly-donut-card {
        display: none;
    }

    .weekly-category-card {
        display: block;
        margin: 10px 0;
    }

    .weekly-summary .bslib-value-box {
        min-height: 72px;
    }
}
""")

# ================================================================================================================================
# Sidebar
# ================================================================================================================================
with ui.layout_sidebar():
    with ui.sidebar(open="desktop"):
        min_date = df_full["Date"].min().date()
        max_date = df_full["Date"].max().date()

        ui.input_date_range(
            "date_range",
            "Select date range",
            start=min_date,
            end=max_date,
            min=min_date,
            max=max_date,
        )

        ui.input_radio_buttons(
            "who",
            "Which Person",
            ["Jesse", "Bridget"],
            selected=["Jesse"],
            inline=True,
        )

        ui.input_radio_buttons(
            "avg_type",
            "Average Type",
            choices={"mean": "Mean", "median": "Median"},
            selected="mean",
        )

        ui.input_action_button("reset", "Reset filter")

    ui.input_select(
        "view",
        "View",
        choices=[
            "Weekly Summary",
            "Today", 
            "Explore",
            "Dataframe",
        ],
        selected="Weekly Summary",
    )
# ================================================================================================================================
# Weekly Summary
# ================================================================================================================================
    with ui.panel_conditional("input.view == 'Weekly Summary'", class_="weekly-summary"):

        with ui.card(class_="weekly-category-card"):
            ui.h5("Weekly spending", class_="weekly-category-title")

            @render.ui
            def weekly_category_list():
                price_col = input.weekly_currency()
                category_df = (
                    week_df()
                    .groupby("Category", as_index=False)[price_col]
                    .sum()
                )

                total = category_df[price_col].sum()
                category_df = category_df[
                    (category_df[price_col] > 0)
                    | (category_df["Category"] == "Gas")
                ]
                category_df = category_df.sort_values(price_col, ascending=False)

                colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd", "#a21414", "#17becf"]
                symbol = currency_symbol()
                rows = [
                    ui.div(
                        ui.span(class_="weekly-category-total-marker"),
                        ui.span("Total", class_="weekly-category-name"),
                        ui.span(
                            f"{symbol}{total:,.0f}",
                            class_="weekly-category-value",
                        ),
                        class_="weekly-category-row weekly-category-total",
                    )
                ]

                for index, (_, row) in enumerate(category_df.iterrows()):
                    rows.append(
                        ui.div(
                            ui.span(
                                class_="weekly-category-dot",
                                style=f"background-color: {colors[index % len(colors)]};",
                            ),
                            ui.span(str(row["Category"]), class_="weekly-category-name"),
                            ui.span(
                                f"{symbol}{row[price_col]:,.0f}",
                                class_="weekly-category-value",
                            ),
                            class_="weekly-category-row",
                        )
                    )

                return ui.div(*rows, class_="weekly-category-list")

        with ui.tags.details(class_="weekly-transactions"):
            ui.tags.summary("View transactions")

            @render.data_frame
            def week_table():
                df = week_df()

                columns_to_show = [
                    "Category",
                    input.weekly_currency(),
                    "Note",
                ]
                df["Price NZD"] = df["Price NZD"].round(2)
                df["Price"] = df["Price"].round(2)

                return df[columns_to_show]

        with ui.div(class_="weekly-controls"):
            ui.input_radio_buttons(
                "weekly_currency",
                "",
                choices={"Price NZD": "NZD", "Price": "Yen"},
                selected="Price",
                inline=True,
            )

            ui.input_radio_buttons(
                "weekly_setting",
                "",
                choices={
                    "calendar": "Calendar Week",
                    "last_7_days": "Last 7 Days",
                },
                selected="calendar",
                inline=True,
            )
# ================================================================================================================================
# Today Tab
# ================================================================================================================================
    with ui.panel_conditional("input.view == 'Today'", class_="weekly-summary today-summary"):
        # The day picker stays above the same summary layout used by Weekly Summary.
        with ui.div(class_="today-date-control"):
            ui.input_date(
                "today_date", "Select day", value=date.today(), min=min_date, max=max_date,
            )

        with ui.card(class_="weekly-category-card"):
            ui.h5("Today's spending", class_="weekly-category-title")

            @render.ui
            def today_category_list():
                price_col = input.today_currency()
                category_df = today_df().groupby("Category", as_index=False)[price_col].sum()
                total = category_df[price_col].sum()
                category_df = category_df[
                    (category_df[price_col] > 0) | (category_df["Category"] == "Gas")
                ].sort_values(price_col, ascending=False)

                colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd", "#a21414", "#17becf"]
                symbol = "$" if price_col == "Price NZD" else "\N{YEN SIGN}"
                rows = [
                    ui.div(
                        ui.span(class_="weekly-category-total-marker"),
                        ui.span("Total", class_="weekly-category-name"),
                        ui.span(f"{symbol}{total:,.0f}", class_="weekly-category-value"),
                        class_="weekly-category-row weekly-category-total",
                    )
                ]
                for index, (_, row) in enumerate(category_df.iterrows()):
                    rows.append(
                        ui.div(
                            ui.span(class_="weekly-category-dot", style=f"background-color: {colors[index % len(colors)]};"),
                            ui.span(str(row["Category"]), class_="weekly-category-name"),
                            ui.span(f"{symbol}{row[price_col]:,.0f}", class_="weekly-category-value"),
                            class_="weekly-category-row",
                        )
                    )
                return ui.div(*rows, class_="weekly-category-list")

        with ui.tags.details(class_="weekly-transactions"):
            ui.tags.summary("View transactions")

            @render.data_frame
            def today_table():
                df = today_df().copy()
                columns_to_show = ["Category", input.today_currency(), "Note"]
                df["Price NZD"] = df["Price NZD"].round(2)
                df["Price"] = df["Price"].round(2)
                return df[columns_to_show]

        with ui.div(class_="weekly-controls"):
            ui.input_radio_buttons(
                "today_currency",
                "",
                choices={"Price NZD": "NZD", "Price": "Yen"},
                selected="Price",
                inline=True,
            )

# ================================================================================================================================
# Summary Stats Tab
# ================================================================================================================================

    with ui.panel_conditional("input.view == 'Summary Stats'"):
        with ui.layout_columns(fill=False):
            with ui.value_box(showcase=ui.img(src="7_11_bby.JPG", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                "Daily Spend"
                @render.express
                def daily_spend():
                    df = filtered_df()
                    daily_total = df[df['Category'] != "Flights"].groupby("Date")["Price NZD"].sum()
                    value = avg_calc(daily_total)
                    f"${value:,.2f}"

            with ui.value_box(showcase=ui.img(src="chomp.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                "Daily Food"
                @render.express
                def daily_food():
                    df = filtered_df()
                    daily_food = df[df['Category'] == 'Food'].groupby("Date")["Price NZD"].sum()
                    value = avg_calc(daily_food)
                    f"${value:,.2f}"

            with ui.value_box(showcase=ui.img(src="nap.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                "Accom"
                @render.express
                def accom_av():
                    df = filtered_df()
                    accom = df[df['Category'] == 'Accom'].groupby("Date")["Price NZD"].sum()
                    value = avg_calc(accom)
                    f"${value:,.2f}"

            with ui.value_box(showcase=ui.img(src="flight_socks.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                "Total"
                @render.express
                def flight_cost():
                    df = filtered_df()
                    cost = df["Price NZD"].sum()
                    f"${cost:,.2f}"


# ================================================================================================================================
# Reactive calcs and functions
# ================================================================================================================================
@reactive.calc
def filtered_df():
    df = filtered_df_person().copy()
    df["Date"] = pd.to_datetime(df["Date"])

    selected_range = input.date_range()
    if selected_range:
        start_date, end_date = selected_range
        df = df[
            (df["Date"].dt.date >= start_date)
            & (df["Date"].dt.date <= end_date)
        ]

    return df

@reactive.calc
def filtered_df_person():
    df = df_full.copy()

    selected_person = input.who()
    if selected_person:
        df = df[df["Person"] == selected_person]

    return df

def avg_calc(data):
    selected = input.avg_type()
    if selected == "mean":
        value = data.mean()
    else:
        value = data.median()

    return value

@reactive.calc
def currency_symbol():
    return "$" if input.weekly_currency() == "Price NZD" else "¥"

@reactive.effect
@reactive.event(input.reset)
def reset_filters():
    ui.update_date_range("date_range", start=min_date, end=max_date)
    ui.update_date("today_date", value=date.today())
    ui.update_checkbox_group("who", selected=["Jesse"])
    ui.update_radio_buttons("avg_type", selected = "mean")


@reactive.calc
def today_df():
    df = filtered_df_person().copy()

    selected_day = input.today_date()
    if selected_day is None:
        selected_day = date.today()


    today_expenses = df[
        df["Date"].dt.date == selected_day
    ]

    return today_expenses

@reactive.calc
def week_df():
    df = filtered_df_person().copy()
    df["Date"] = pd.to_datetime(df["Date"])

    setting = input.weekly_setting()

    # If user selects calendar week, dataframe filters to current week of the year
    if setting == "calendar":
        current_year, current_week, _ = datetime.now().isocalendar()
        week_expenses = df[
            (df['Date'].dt.isocalendar().year == current_year) & 
            (df['Date'].dt.isocalendar().week == current_week)
        ]

    # If last 7 days selected, dataframe filters to last 7 days
    elif setting == "last_7_days":
        today = date.today()
        cutoff_date = today - pd.Timedelta(days=6)

        week_expenses = df[
            (df["Date"].dt.date >= cutoff_date)
            & (df["Date"].dt.date <= today)
        ]

    return week_expenses
