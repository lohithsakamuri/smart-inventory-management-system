import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ---------- DATABASE ----------
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
quantity INTEGER,
price REAL
)
""")

conn.commit()

# ---------- TITLE ----------
st.title("📦 Smart Inventory Management System")

st.markdown("""
<style>
.stApp {
background-color:#f5f7fa;
}
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
menu = st.sidebar.selectbox(
"Menu",
["Add Product","View Products"]
)

# ---------- ADD PRODUCT ----------
if menu == "Add Product":

    st.subheader("Add New Product")

    name = st.text_input("Product Name")

    category = st.selectbox(
    "Category",
    ["Electronics","Grocery","Clothing","Furniture","Other"]
    )

    quantity = st.number_input("Quantity",min_value=0)
    price = st.number_input("Price",min_value=0.0)

    if st.button("Add Product"):

        if name == "":
            st.warning("Enter product name")

        else:
            cursor.execute(
            "INSERT INTO products(name,category,quantity,price) VALUES(?,?,?,?)",
            (name,category,quantity,price)
            )

            conn.commit()

            st.success("✅ Product Added Successfully")
            st.rerun()

# ---------- VIEW PRODUCTS ----------
elif menu == "View Products":

    st.subheader("📋 Inventory List")

    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()

    df = pd.DataFrame(
    data,
    columns=["ID","Name","Category","Quantity","Price"]
    )

    # ---------- SEARCH ----------
    search = st.text_input("🔍 Search Product")

    if search:
        df = df[df["Name"].str.contains(search,case=False)]

    st.dataframe(df,use_container_width=True)

    # ---------- LOW STOCK ----------
    low_stock = df[df["Quantity"] < 5]

    if not low_stock.empty:
        st.warning("⚠️ Low Stock Products")
        st.dataframe(low_stock,use_container_width=True)

    # ---------- UPDATE ----------
    st.subheader("✏️ Update Product Quantity")

    product_ids = df["ID"].tolist()

    if product_ids:

        update_id = st.selectbox("Select Product ID",product_ids)
        new_quantity = st.number_input("New Quantity",min_value=0)

        if st.button("Update Quantity"):

            cursor.execute(
            "UPDATE products SET quantity=? WHERE id=?",
            (new_quantity,update_id)
            )

            conn.commit()

            st.success("✅ Quantity Updated Successfully")
            st.rerun()

    # ---------- DELETE ----------
    st.subheader("🗑 Delete Product")

    if product_ids:

        delete_id = st.selectbox("Select Product ID to Delete",product_ids)

        if st.button("Delete Product"):

            cursor.execute(
            "DELETE FROM products WHERE id=?",
            (delete_id,)
            )

            conn.commit()

            st.success("✅ Product Deleted")
            st.rerun()

    # ---------- INVENTORY VALUE ----------
    df["Total Value"] = df["Quantity"] * df["Price"]

    total_products = len(df)
    total_quantity = df["Quantity"].sum()
    total_value = df["Total Value"].sum()

    st.subheader("📊 Inventory Dashboard")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("📦 Total Products",total_products)

    with col2:
        st.metric("📊 Total Quantity",total_quantity)

    with col3:
        st.metric("💰 Total Inventory Value",f"₹ {total_value}")

    st.divider()

    # ---------- BAR CHART ----------
    st.subheader("📊 Product Quantity Overview")

    bar_fig = px.bar(
    df,
    x="Name",
    y="Quantity",
    title="Stock Quantity per Product",
    color="Category"
    )

    st.plotly_chart(bar_fig,use_container_width=True)

    # ---------- PIE CHART ----------
    st.subheader("📊 Inventory Value Distribution")

    pie_fig = px.pie(
    df,
    names="Category",
    values="Total Value",
    title="Inventory Value by Category"
    )

    st.plotly_chart(pie_fig,use_container_width=True)

    # ---------- CSV DOWNLOAD ----------
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
    label="📥 Download Inventory CSV",
    data=csv,
    file_name="inventory.csv",
    mime="text/csv"
    )