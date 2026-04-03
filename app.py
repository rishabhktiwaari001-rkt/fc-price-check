import streamlit as st
import pandas as pd

# 1. App Setup
st.set_page_config(page_title="FC Price Check", page_icon="🛒", layout="centered")

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('discount_data.csv')
    # Convert ProductID to string to handle barcode scans perfectly
    df['ProductID'] = df['ProductID'].astype(str).str.strip()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ 'discount_data.csv' file not found. Please check GitHub.")
    st.stop()

# 3. UI Design
st.title("🛒 FC Quick Price Lookup")
st.markdown("Scan barcode or type **Product ID** below:")

product_id = st.text_input("Enter Product ID:", placeholder="e.g., 17237878")

# 4. Search Logic
if product_id:
    search_query = str(product_id).strip()
    result = df[df['ProductID'] == search_query]

    if not result.empty:
        row = result.iloc[0]
        
        name = row['ProductName']
        mrp = float(row['MRP'])
        
        # Handle empty discount cells safely
        sale_price_raw = row['After Discount']
        discount_pct_raw = row['% discount']
        
        if pd.isna(sale_price_raw) or str(sale_price_raw).strip() == '': 
            sale_price = mrp
        else:
            sale_price = float(sale_price_raw)
            
        if pd.isna(discount_pct_raw) or str(discount_pct_raw).strip() == '': 
            discount_pct = 0.0
        else:
            discount_pct = float(discount_pct_raw)

        # Display Results
        st.success("✅ Product Found!")
        st.subheader(name)
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        col1.metric(label="MRP", value=f"₹{mrp:,.2f}")
        col2.metric(label="Discount", value=f"{discount_pct:.0f}%")
        
        savings = mrp - sale_price
        col3.metric(
            label="Final Sale Price", 
            value=f"₹{sale_price:,.2f}", 
            delta=f"-₹{savings:,.2f}" if savings > 0 else None, 
            delta_color="inverse"
        )
    else:
        st.error("⚠️ Product not found in today's discount list. Please check the ID.")