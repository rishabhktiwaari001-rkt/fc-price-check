import streamlit as st
import pandas as pd

# 1. Page Setup (Design)
st.set_page_config(page_title="FC Price Check", page_icon="🛒", layout="centered")

# 2. Data Load Karna
@st.cache_data
def load_data():
    # File padhna (File ka naam exactly 'discount_data.csv' hona chahiye)
    df = pd.read_csv('discount_data.csv')
    
    # ProductID ko text/string mein convert karna taaki barcode scanner smoothly kaam kare
    df['ProductID'] = df['ProductID'].astype(str).str.strip()
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ 'discount_data.csv' file nahi mili. Kripya GitHub par file check karein ki naam ekdam sahi hai ya nahi.")
    st.stop()

# 3. Dashboard UI (Screen par jo dikhega)
st.title("🛒 FC Quick Price Lookup")
st.markdown("Niche barcode scan karein ya **Product ID** type karein:")

# Input Box
product_id = st.text_input("Enter Product ID:", placeholder="e.g., 17237878")

# 4. Search aur Dikhane ka Logic
if product_id:
    # Galti se type hue spaces ko hatana
    search_query = str(product_id).strip()
    
    # Data sheet mein product dhoondna
    result = df[df['ProductID'] == search_query]

    if not result.empty:
        # Product milne par data nikalna
        row = result.iloc[0]
        
        name = row['ProductName']
        mrp = float(row['MRP'])
        
        # Discount aur Sale Price ko safely read karna
        sale_price_raw = row['After Discount']
        discount_pct_raw = row['% discount']
        
        # Agar Excel sheet mein discount khali ho, toh MRP ko hi Sale Price maan lo
        if pd.isna(sale_price_raw) or sale_price_raw == 0 or str(sale_price_raw).strip() == '': 
            sale_price = mrp
        else:
            sale_price = float(sale_price_raw)
            
        if pd.isna(discount_pct_raw) or str(discount_pct_raw).strip() == '': 
            discount_pct = 0.0
        else:
            discount_pct = float(discount_pct_raw)

        # Screen par Result dikhana
        st.success("✅ Product Found!")
        st.subheader(name)
        st.divider()
        
        # 3 Boxes mein Price aur Discount dikhana
        col1, col2, col3 = st.columns(3)
        col1.metric(label="MRP", value=f"₹{mrp:,.2f}")
        col2.metric(label="Discount", value=f"{discount_pct:.0f}%")
        
        # Kitne paise bache (Savings) calculate karna
        savings = mrp - sale_price
        col3.metric(
            label="Final Sale Price", 
            value=f"₹{sale_price:,.2f}", 
            delta=f"-₹{savings:,.2f}" if savings > 0 else None, 
            delta_color="inverse"
        )
        
    else:
        # Agar product list mein na ho
        st.error("⚠️ Product aaj ki discount list me nahi mila. Kripya ID check karein.")
