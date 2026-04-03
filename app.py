import streamlit as st
import pandas as pd

# 1. App Setup
st.set_page_config(page_title="FC Price Check", page_icon="🛒", layout="centered")

# 2. Load Data (Bulletproof Mac CSV Reader)
@st.cache_data
def load_data():
    # 'utf-8-sig' Mac ke hidden codes (BOM) ko automatically hata deta hai
    df = pd.read_csv('discount_data.csv', encoding='utf-8-sig')
    
    # Sabhi columns ke aage-peeche se invisible spaces hatana
    df.columns = df.columns.str.strip()
    
    # ProductID ko string mein convert karna
    df['ProductID'] = df['ProductID'].astype(str).str.strip()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ 'discount_data.csv' file not found. Please check GitHub.")
    st.stop()
except Exception as e:
    st.error(f"❌ File read error: {e}")
    st.stop()

# 3. UI Design
st.title("🛒 FC Quick Price Lookup")
st.markdown("Scan barcode or type **Product ID** below:")

product_id = st.text_input("Enter Product ID:", placeholder="e.g., 17237878")

# 4. Search Logic
if product_id:
    search_query = str(product_id).strip()
    
    # Extra safety check ki column hai ya nahi
    if 'ProductID' not in df.columns:
        st.error(f"❌ Error: ProductID column gayab hai. Excel file check karein. Columns mile: {', '.join(df.columns)}")
        st.stop()
        
    result = df[df['ProductID'] == search_query]

    if not result.empty:
        row = result.iloc[0]
        
        # .get() use kiya hai taaki minor spelling mistake pe app crash na ho
        name = row.get('ProductName', 'Unknown Product')
        mrp = float(row.get('MRP', 0))
        
        sale_price_raw = row.get('After Discount', mrp)
        discount_pct_raw = row.get('% discount', 0)
        
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
