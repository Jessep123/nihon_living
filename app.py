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
        padding: 0 4px;
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

.weekly-donut-card {
    max-width: 460px;
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

@media (max-width: 576px) {
    .weekly-donut-card {
        margin: 10px 0;
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
        with ui.layout_columns(fill=False):
    
            with ui.value_box(showcase=ui.img(src="flight_socks.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                        "Total"
                        @render.express
                        def week_cost():
                            week_expenses = week_df()
                            price_col = input.weekly_currency()
                            cost = week_expenses[price_col].sum()
                            f"{currency_symbol()}{cost:,.2f}"

            # with ui.value_box(showcase=ui.img(src="chomp.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
            #     "Groceries"
            #     @render.express
            #     def groceries_week():
            #         week_expenses = week_df()
            #         price_col = input.weekly_currency()

            #         week_groceries = (
            #             week_expenses.loc[
            #                 week_expenses["Category"] == "Groceries",
            #                 price_col
            #             ].sum()
            #         )
            #         f"{currency_symbol()}{week_groceries:,.2f}"

            # with ui.value_box(showcase=ui.img(src="chomp.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
            #                         "Eating Out"
            #                         @render.express
            #                         def eating_out_week():
            #                             week_expenses = week_df()
            #                             price_col = input.weekly_currency()

            #                             week_snacks = (
            #                                 week_expenses.loc[
            #                                     week_expenses["Category"] == "Eating Out",
            #                                     price_col
            #                                 ].sum()
            #                             )
            #                             f"{currency_symbol()}{week_snacks:,.2f}"

            # with ui.value_box(showcase=ui.img(src="woof.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
            #     "Misc"
            #     @render.express
            #     def misc_week():
            #         week_expenses = week_df()
            #         price_col = input.weekly_currency()

            #         week_misc = (
            #             week_expenses.loc[
            #                 week_expenses["Category"] == "Misc",
            #                 price_col
            #             ].sum()
            #         )

            #         f"{currency_symbol()}{week_misc:,.2f}"

            # with ui.value_box(showcase=ui.img(src="woof.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
            #                         "Gas"
            #                         @render.express
            #                         def gas_week():
            #                             week_expenses = week_df()
            #                             price_col = input.weekly_currency()

            #                             week_gas = (
            #                                 week_expenses.loc[
            #                                     week_expenses["Category"] == "Gas",
            #                                     price_col
            #                                 ].sum()
            #                             )
            
            #                             f"{currency_symbol()}{week_gas:,.2f}"


        with ui.card(class_="weekly-donut-card"):
            ui.h5("Weekly spending by category", class_="weekly-donut-title")

            @render.plot(alt="Weekly spending by category")
            def weekly_donut():
                price_col = input.weekly_currency()

                donut_df = (
                    week_df()
                    .groupby("Category", as_index=False)[price_col]
                    .sum()
                )

                donut_df = donut_df[donut_df[price_col] > 0]

                fig, ax = plt.subplots(figsize=(4.4, 4.6), dpi=150)

                if donut_df.empty:
                    ax.text(
                        0.5, 0.5, "No spending this week",
                        ha="center", va="center", fontsize=13,
                    )
                    ax.axis("off")
                    return fig

                colors = [
                    "#2ca02c",  # green
                    "#1f77b4",  # blue
                    "#ff7f0e",  # orange
                    "#9467bd",  # purple
                    "#a21414",  # red
                    "#17becf",  # teal
                ]

                total = donut_df[price_col].sum()
                symbol = currency_symbol()

                wedges, _ = ax.pie(
                    donut_df[price_col],
                    colors=colors[:len(donut_df)],
                    startangle=90,
                    counterclock=False,
                    wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2),
                )

                ax.text(
                    0, 0.10, "Total",
                    ha="center", va="center",
                    fontsize=10, color="#6c757d",
                )
                ax.text(
                    0, -0.08, f"{symbol}{total:,.0f}",
                    ha="center", va="center",
                    fontsize=19, fontweight="bold", color="#212529",
                )

                legend_labels = [
                    f"{row['Category']}  {symbol}{row[price_col]:,.0f}"
                    for _, row in donut_df.iterrows()
                ]

                ax.legend(
                    wedges,
                    legend_labels,
                    loc="upper center",
                    bbox_to_anchor=(0.5, -0.03),
                    ncol=2,
                    frameon=False,
                    fontsize=8,
                    columnspacing=1.2,
                    handlelength=1,
                )

                ax.set(aspect="equal")
                fig.subplots_adjust(top=0.95, bottom=0.18)

                return fig

            @render.data_frame
            def week_table():
                df = week_df()

                columns_to_show = [
                    "Category",
                    "Price",
                    "Price NZD",
                    "Note",
                    "Person"
                ]
                df["Price NZD"] = df["Price NZD"].round(2)
                df["Price"] = df["Price"].round(2)

                return df[columns_to_show]
# ================================================================================================================================
# Today Tab
# ================================================================================================================================
    with ui.panel_conditional("input.view == 'Today'"):
                with ui.layout_columns(fill=False):
                    ui.input_date(
                                            "today_date",
                                            "Select day",
                                            value=date.today(),
                                            min=min_date,
                                            max=max_date,
                                        )
                    
                    with ui.value_box(showcase=ui.img(src="flight_socks.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                        "Total"
                        @render.express
                        def today_cost():
                            today_expenses = today_df()
                            price_col = input.today_currency()
                            cost = today_expenses[price_col].sum()
                            f"{currency_symbol()}{cost:,.2f}"

                    with ui.value_box(showcase=ui.img(src="chomp.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                        "Groceries"
                        @render.express
                        def groceries_today():
                            today_expenses = today_df()
                            price_col = input.today_currency()

                            today_groceries = (
                                today_expenses.loc[
                                    today_expenses["Category"] == "Groceries",
                                    price_col
                                ].sum()
                            )
                            f"{currency_symbol()}{today_groceries:,.2f}"

                    with ui.value_box(showcase=ui.img(src="chomp.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                                            "Eating Out"
                                            @render.express
                                            def eating_out_today():
                                                today_expenses = today_df()
                                                price_col = input.today_currency()
                    
                                                today_snacks = (
                                                    today_expenses.loc[
                                                        today_expenses["Category"] == "Eating Out",
                                                        price_col
                                                    ].sum()
                                                )
                                                f"{currency_symbol()}{today_snacks:,.2f}"

                    with ui.value_box(showcase=ui.img(src="woof.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                        "Misc"
                        @render.express
                        def misc_today():
                            today_expenses = today_df()
                            price_col = input.today_currency()

                            today_misc = (
                                today_expenses.loc[
                                    today_expenses["Category"] == "Misc",
                                    price_col
                                ].sum()
                            )

                            f"{currency_symbol()}{today_misc:,.2f}"

                    with ui.value_box(showcase=ui.img(src="woof.jpeg", style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; margin-top: 10px;", showcase_layout="left center")):
                                            "Gas"
                                            @render.express
                                            def gas_today():
                                                today_expenses = today_df()
                                                price_col = input.today_currency()
                    
                                                today_gas = (
                                                    today_expenses.loc[
                                                        today_expenses["Category"] == "Gas",
                                                        price_col
                                                    ].sum()
                                                )
                    
                                                f"{currency_symbol()}{today_gas:,.2f}"

                    
                    ui.input_radio_buttons(
                        "today_currency",
                        "",
                        choices={"Price NZD": "NZD", "Price": "Yen"},
                        selected="Price"
                    )


                    @render.data_frame
                    def today_table():
                        df = today_df()

                        columns_to_show = [
                            "Category",
                            "Price",
                            "Price NZD",
                            "Note",
                            "Person"
                        ]
                        df["Price NZD"] = df["Price NZD"].round(2)
                        df["Price"] = df["Price"].round(2)

                        return df[columns_to_show]

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

    setting = input.weekly_setting()

    # If user selects calendar week, dataframe filters to current week of the year
    if setting == "calendar":
        current_year, current_week, _ = datetime.now().isocalendar()
        week_expenses = df[
            (df['Date'].dt.isocalendar().year == current_year) & 
            (df['Date'].dt.isocalendar().week == current_week)
        ]

    # If last 7 days selected, dataframe filters to last 7 days
    else:
        cutoff_date = date.today() - pd.Timedelta(days=6)  
        week_expenses = df[
            (df['Date'].dt.isocalendar().day >= cutoff_date)
        ]

    return week_expenses
