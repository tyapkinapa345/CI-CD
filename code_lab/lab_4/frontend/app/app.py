import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="Order System", layout="wide")
st.title("📦 Order Management System")

# Список статусов (глобально, чтобы был доступен во всех блоках)
status_options = ['новый', 'в обработке', 'отправлен', 'доставлен', 'отменён']

# --- Боковая панель для создания заказа ---
with st.sidebar:
    st.header("➕ Create New Order")
    with st.form("create_order_form"):
        order_number = st.text_input("Order Number*", help="Unique alphanumeric")
        items = st.text_area("Items* (one per line)", help="Enter each item on new line")
        amount = st.number_input("Total Amount*", min_value=0.01, step=0.01, format="%.2f")
        address = st.text_area("Delivery Address*")
        status = st.selectbox("Status", status_options, index=0)
        submitted = st.form_submit_button("Create Order")
        
        if submitted:
            if not all([order_number, items, amount, address]):
                st.error("All fields are required")
            else:
                items_list = [item.strip() for item in items.split("\n") if item.strip()]
                if not items_list:
                    st.error("At least one item is required")
                else:
                    payload = {
                        "order_number": order_number,
                        "items": items_list,
                        "amount": amount,
                        "delivery_address": address,
                        "status": status
                    }
                    try:
                        resp = requests.post(f"{BACKEND_URL}/orders", json=payload)
                        if resp.status_code == 201:
                            st.success("Order created successfully!")
                            st.experimental_rerun()
                        else:
                            st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

# --- Основная область: список заказов ---
st.header("📋 All Orders")

@st.cache_data(ttl=5)
def fetch_orders():
    try:
        resp = requests.get(f"{BACKEND_URL}/orders")
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Failed to fetch orders")
            return []
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")
        return []

orders = fetch_orders()
if orders:
    df = pd.DataFrame(orders)
    df['items'] = df['items'].apply(lambda x: ", ".join(x))
    # Если колонки status нет (старые заказы), добавляем
    if 'status' not in df.columns:
        df['status'] = 'новый'
    df = df[['id', 'order_number', 'items', 'amount', 'delivery_address', 'status']]
    st.dataframe(df, use_container_width=True)
    
    # --- Удаление заказа ---
    st.subheader("🗑️ Delete Order")
    col1, col2 = st.columns([1, 3])
    with col1:
        order_id_to_delete = st.number_input("Order ID to delete", min_value=1, step=1)
    with col2:
        if st.button("Delete Order"):
            try:
                resp = requests.delete(f"{BACKEND_URL}/orders/{order_id_to_delete}")
                if resp.status_code == 204:
                    st.success("Order deleted")
                    st.cache_data.clear()
                    st.experimental_rerun()
                else:
                    st.error("Order not found")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # --- Обновление статуса ---
    st.subheader("✏️ Update Order Status")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        update_id = st.number_input("Order ID", min_value=1, step=1, key="update_status_id")
    with col2:
        new_status = st.selectbox("New Status", status_options, key="new_status")
    with col3:
        if st.button("Update Status"):
            try:
                resp = requests.put(f"{BACKEND_URL}/orders/{update_id}", json={"status": new_status})
                if resp.status_code == 200:
                    st.success("Status updated")
                    st.cache_data.clear()
                    st.experimental_rerun()
                else:
                    st.error("Order not found")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("No orders yet. Create one using the sidebar.")
