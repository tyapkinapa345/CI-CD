import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")

st.set_page_config(page_title="Система управления заказами", layout="wide")
st.title("📦 Система управления заказами")

# Список статусов (глобально, чтобы был доступен во всех блоках)
status_options = ['новый', 'в обработке', 'отправлен', 'доставлен', 'отменён']

# --- Боковая панель для создания заказа ---
with st.sidebar:
    st.header("➕ Создать новый заказ")
    with st.form("create_order_form"):
        order_number = st.text_input("Номер заказа*", help="Уникальный буквенно-цифровой")
        items = st.text_area("Товары* (каждый с новой строки)", help="Вводите каждый товар с новой строки")
        amount = st.number_input("Общая сумма*", min_value=0.01, step=0.01, format="%.2f")
        address = st.text_area("Адрес доставки*")
        status = st.selectbox("Статус", status_options, index=0)
        submitted = st.form_submit_button("Создать заказ")
        
        if submitted:
            if not all([order_number, items, amount, address]):
                st.error("Все поля обязательны для заполнения")
            else:
                items_list = [item.strip() for item in items.split("\n") if item.strip()]
                if not items_list:
                    st.error("Укажите хотя бы один товар")
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
                            st.success("Заказ успешно создан!")
                            st.experimental_rerun()
                        else:
                            st.error(f"Ошибка: {resp.json().get('detail', 'Неизвестная ошибка')}")
                    except Exception as e:
                        st.error(f"Ошибка подключения: {e}")

# --- Основная область: список заказов ---
st.header("📋 Все заказы")

@st.cache_data(ttl=5)
def fetch_orders():
    try:
        resp = requests.get(f"{BACKEND_URL}/orders")
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Не удалось загрузить заказы")
            return []
    except Exception as e:
        st.error(f"Не удаётся подключиться к серверу: {e}")
        return []

orders = fetch_orders()
if orders:
    df = pd.DataFrame(orders)
    df['items'] = df['items'].apply(lambda x: ", ".join(x))
    # Если колонки status нет (старые заказы), добавляем
    if 'status' not in df.columns:
        df['status'] = 'новый'
    df = df[['id', 'order_number', 'items', 'amount', 'delivery_address', 'status']]
    st.dataframe(
        df,
        column_config={
            "id": "ID",
            "order_number": "Номер заказа",
            "items": "Товары",
            "amount": "Сумма",
            "delivery_address": "Адрес доставки",
            "status": "Статус"
        },
        use_container_width=True
    )
    
    # --- Удаление заказа ---
    st.subheader("🗑️ Удалить заказ")
    col1, col2 = st.columns([1, 3])
    with col1:
        order_id_to_delete = st.number_input("ID заказа для удаления", min_value=1, step=1)
    with col2:
        if st.button("Удалить заказ"):
            try:
                resp = requests.delete(f"{BACKEND_URL}/orders/{order_id_to_delete}")
                if resp.status_code == 204:
                    st.success("Заказ удалён")
                    st.cache_data.clear()
                    st.experimental_rerun()
                else:
                    st.error("Заказ не найден")
            except Exception as e:
                st.error(f"Ошибка: {e}")
    
    # --- Обновление статуса ---
    st.subheader("✏️ Обновить статус заказа")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        update_id = st.number_input("ID заказа", min_value=1, step=1, key="update_status_id")
    with col2:
        new_status = st.selectbox("Новый статус", status_options, key="new_status")
    with col3:
        if st.button("Обновить статус"):
            try:
                resp = requests.put(f"{BACKEND_URL}/orders/{update_id}", json={"status": new_status})
                if resp.status_code == 200:
                    st.success("Статус обновлён")
                    st.cache_data.clear()
                    st.experimental_rerun()
                else:
                    st.error("Заказ не найден")
            except Exception as e:
                st.error(f"Ошибка: {e}")
else:
    st.info("Пока нет заказов. Создайте через боковую панель.")
