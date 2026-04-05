import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="Order System", layout="wide")
st.title("📦 Order Management System")

status_options = ['новый', 'в обработке', 'отправлен', 'доставлен', 'отменён']

# --- Инициализация сессии для списка товаров ---
if 'items_list' not in st.session_state:
    st.session_state.items_list = []  # каждый элемент: {"name": "", "quantity": 1}

# --- Функции для работы со списком товаров ---
def add_item():
    name = st.session_state.get('new_item_name', '').strip()
    qty = st.session_state.get('new_item_quantity', 1)
    if name:
        st.session_state.items_list.append({"name": name, "quantity": qty})
        st.session_state.new_item_name = ''
        st.session_state.new_item_quantity = 1
        st.rerun()

def remove_item(idx):
    st.session_state.items_list.pop(idx)
    st.rerun()

# --- Боковая панель ---
with st.sidebar:
    st.header("➕ Create New Order")

    # Добавление товара (ВНЕ формы)
    st.subheader("Add item")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.text_input("Item name", key="new_item_name", placeholder="e.g., Laptop")
    with col2:
        st.number_input("Quantity", min_value=1, step=1, key="new_item_quantity", value=1)
    with col3:
        st.button("➕ Add", on_click=add_item, use_container_width=True)

    # Отображение текущего списка товаров
    if st.session_state.items_list:
        st.write("**Current items:**")
        for idx, item in enumerate(st.session_state.items_list):
            col_a, col_b, col_c = st.columns([2, 1, 0.5])
            col_a.write(f"{item['name']}")
            col_b.write(f"x{item['quantity']}")
            if col_c.button("❌", key=f"del_{idx}"):
                remove_item(idx)
    else:
        st.info("No items added yet")

    # Форма для остальных полей заказа
    with st.form("create_order_form"):
        order_number = st.text_input("Order Number*", help="Unique alphanumeric")
        amount = st.number_input("Total Amount*", min_value=0.01, step=0.01, format="%.2f")
        address = st.text_area("Delivery Address*")
        status = st.selectbox("Status", status_options, index=0)
        submitted = st.form_submit_button("Create Order")

        if submitted:
            if not all([order_number, address]) or not st.session_state.items_list:
                st.error("Order number, address and at least one item are required")
            else:
                payload = {
                    "order_number": order_number,
                    "items": st.session_state.items_list,
                    "amount": amount,
                    "delivery_address": address,
                    "status": status
                }
                try:
                    resp = requests.post(f"{BACKEND_URL}/orders", json=payload)
                    if resp.status_code == 201:
                        st.success("Order created successfully!")
                        st.session_state.items_list = []
                        st.rerun()
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
    
    # --- Обработка items: преобразуем список объектов в строку "name (quantity), ..." ---
    def format_items(items_list):
        if not items_list:
            return ""
        return ", ".join([f"{item['name']} ({item['quantity']})" for item in items_list])
    
    def total_quantity(items_list):
        return sum(item['quantity'] for item in items_list)
    
    df['items_str'] = df['items'].apply(format_items)
    df['total_quantity'] = df['items'].apply(total_quantity)
    
    # --- Подготовка таблицы для вывода ---
    display_df = df.rename(columns={
        'id': 'ID',
        'order_number': 'Order №',
        'items_str': 'Items',
        'total_quantity': 'Total Qty',
        'amount': 'Amount ($)',
        'delivery_address': 'Address',
        'status': 'Status'
    })
    columns_order = ['ID', 'Order №', 'Items', 'Total Qty', 'Amount ($)', 'Address', 'Status']
    st.dataframe(display_df[columns_order], use_container_width=True)
    
    # --- Статистика ---
    st.subheader("📊 Statistics")
    total_orders = len(df)
    total_revenue = df['amount'].sum()
    total_items_sold = df['total_quantity'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Orders", total_orders)
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
        st.metric("Total Items Sold", total_items_sold)
    with col2:
        st.write("**Orders by Status**")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            st.dataframe(status_counts, use_container_width=True)
    
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
                    st.rerun()
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
                    st.rerun()
                else:
                    st.error("Order not found")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("No orders yet. Create one using the sidebar.")
