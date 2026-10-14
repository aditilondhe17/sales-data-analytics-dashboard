
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Sales Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Data Analytics Dashboard")
st.write("Analyze your sales data using interactive charts and filters.")

# CSV Upload
uploaded_file = st.file_uploader(
    "📂 Upload your Sales CSV file",
    type=["csv"]
)

# Sample data for when no CSV is uploaded
sample_data = {
    "Date": [
        "2026-01-05", "2026-01-12", "2026-02-03",
        "2026-02-15", "2026-03-08", "2026-03-20",
        "2026-04-02", "2026-04-18"
    ],
    "Product": [
        "Laptop", "Mobile", "Headphones", "Laptop",
        "Mobile", "Tablet", "Headphones", "Tablet"
    ],
    "Category": [
        "Electronics", "Electronics", "Accessories", "Electronics",
        "Electronics", "Electronics", "Accessories", "Electronics"
    ],
    "Region": [
        "West", "South", "North", "West",
        "East", "South", "North", "West"
    ],
    "Quantity": [2, 5, 10, 3, 4, 2, 8, 3],
    "UnitPrice": [50000, 15000, 1000, 50000, 15000, 25000, 1000, 25000]
}

# Read uploaded CSV or use sample data
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Date", "Region", "Product",
            "Category", "Sales", "Quantity"
        ]

        missing_columns = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_columns:
            st.error(
                "Missing columns: " + ", ".join(missing_columns)
                + ". Please upload a CSV with the required columns."
            )
            st.stop()

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
        df = df.dropna(
            subset=["Date", "Region", "Product", "Category", "Sales", "Quantity"]
        )
        df["Revenue"] = df["Sales"]

        st.success("CSV uploaded successfully!")

    except Exception as e:
        st.error(f"Could not read the CSV file: {e}")
        st.stop()

else:
    df = pd.DataFrame(sample_data)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    st.info("Showing sample data. Upload your CSV to view your own sales.")

# Show data
st.subheader("📄 Sales Data Preview")
st.dataframe(df, use_container_width=True)

if df.empty:
    st.warning("No valid data found in this CSV.")
    st.stop()

# Sidebar filters
st.sidebar.header("🔎 Filter Sales")

regions = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df["Region"].astype(str).unique()),
    default=sorted(df["Region"].astype(str).unique())
)

categories = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["Category"].astype(str).unique()),
    default=sorted(df["Category"].astype(str).unique())
)

filtered_df = df[
    df["Region"].astype(str).isin(regions)
    & df["Category"].astype(str).isin(categories)
]

# KPI cards
st.subheader("📈 Sales Summary")

if filtered_df.empty:
    st.warning("No data matches the selected filters. Change your filters.")
    st.stop()

total_revenue = filtered_df["Revenue"].sum()
total_orders = len(filtered_df)
total_units = filtered_df["Quantity"].sum()
avg_order_value = total_revenue / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_units:,.0f}")
col4.metric("Avg. Revenue per Row", f"₹{avg_order_value:,.0f}")

st.divider()

# Charts
left, right = st.columns(2)

with left:
    st.subheader("💰 Revenue by Product")

    product_sales = (
        filtered_df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    fig1 = px.bar(
        product_sales,
        x="Product",
        y="Revenue",
        color="Product",
        title="Product Revenue",
        labels={"Revenue": "Revenue (₹)", "Product": "Product"}
    )

    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("🌍 Revenue by Region")

    region_sales = (
        filtered_df.groupby("Region", as_index=False)["Revenue"]
        .sum()
    )

    fig2 = px.pie(
        region_sales,
        names="Region",
        values="Revenue",
        title="Regional Sales Share",
        hole=0.35
    )

    st.plotly_chart(fig2, use_container_width=True)

# Monthly revenue chart
st.subheader("📅 Monthly Revenue Trend")

monthly_sales = filtered_df.copy()
monthly_sales["Month"] = (
    monthly_sales["Date"].dt.to_period("M").astype(str)
)

monthly_sales = (
    monthly_sales.groupby("Month", as_index=False)["Revenue"]
    .sum()
)

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="Revenue",
    markers=True,
    title="Monthly Revenue",
    labels={"Revenue": "Revenue (₹)", "Month": "Month"}
)

st.plotly_chart(fig3, use_container_width=True)

# Filtered data table
st.subheader("📋 Filtered Sales Records")
st.dataframe(filtered_df, use_container_width=True)

# Download filtered data
csv_download = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Sales CSV",
    data=csv_download,
    file_name="filtered_sales.csv",
    mime="text/csv"
)
