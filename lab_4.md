dev@dev-vm:~/Downloads/lab__4/frontend$ cd ../backend
dev@dev-vm:~/Downloads/lab__4/backend$ microk8s kubectl logs deployment/backend-deploy --tail=50
    return json_serializer(value)
  File "/usr/local/lib/python3.10/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
  File "/usr/local/lib/python3.10/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/local/lib/python3.10/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
  File "/usr/local/lib/python3.10/json/encoder.py", line 179, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
sqlalchemy.exc.StatementError: (builtins.TypeError) Object of type OrderItem is not JSON serializable
[SQL: INSERT INTO orders (order_number, items, amount, delivery_address, status) VALUES (%(order_number)s, %(items)s, %(amount)s, %(delivery_address)s, %(status)s) RETURNING orders.id]
[parameters: [{'order_number': 'ORD-1', 'amount': 25.0, 'delivery_address': '10 Lenin Street', 'items': [OrderItem(name='mouse', quantity=1)]}]]
INFO:     10.1.44.116:59062 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:36560 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37476 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37488 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37496 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54338 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54354 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54362 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:42844 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:42860 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:42862 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34022 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34034 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34048 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:52186 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:52190 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:52204 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37426 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37428 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:37430 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34024 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34028 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:34036 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:53516 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:53518 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:53534 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50128 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50140 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50142 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50708 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50716 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:50718 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:44628 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:44642 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:44650 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54644 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54648 - "GET /orders HTTP/1.1" 200 OK
INFO:     10.0.2.15:54650 - "GET /orders HTTP/1.1" 200 OK
dev@dev-vm:~/Downloads/lab__4/backend$ microk8s kubectl describe pod -l app=backend | grep Image:
    Image:          my-backend:v4
    

# Лабораторная работа №4.1 Создание и развертывание полнофункционального приложения в Kubernetes

|Вариант|Название системы|Бизнес-задача|Данные (Пример)|
|--------|-------------------|--------------|------------------|
|16|Order System|Управление заказами клиентов.|Номер заказа, список товаров, сумма, адрес доставки.|

## 1. Титульный лист

- **Дисциплина:** Интеграция и развертывание программного обеспечения с помощью контейнеров (Docker и Kubernetes)  
- **Тема:** Трёхзвенное приложение (Frontend + Backend + Database) в Kubernetes  
- **Технологический стек:** Python, FastAPI, Streamlit, PostgreSQL, Docker, MicroK8s, kubectl  
- **Цель:** Применить знания по контейнеризации и оркестрации, настроить взаимодействие микросервисов.


## 2. Описание архитектуры

Приложение реализует **управление заказами клиентов** (CRUD + дополнительное поле «статус»).  
Состоит из трёх независимых сервисов:

| Компонент   | Технология       | Роль                                                                 |
|-------------|------------------|----------------------------------------------------------------------|
| **Backend** | FastAPI + SQLAlchemy | REST API (CRUD), валидация данных, бизнес-логика                     |
| **Frontend**| Streamlit        | Пользовательский интерфейс: форма создания, таблица заказов, удаление, обновление статуса |
| **Database**| PostgreSQL 13    | Хранение заказов (поля: id, order_number, items(JSON), amount, delivery_address, status) |

### Взаимодействие сервисов

- Frontend обращается к Backend через HTTP по имени `backend-service:8000` (K8s Service).
- Backend подключается к PostgreSQL по имени `postgres-service:5432`.
- Все сервисы запущены в одном namespace `default` кластера MicroK8s.
- Для доступа из браузера используется NodePort `30080` на Frontend.

### Дополнительно реализовано

По собственной инициативе добавлено поле **«статус заказа»** (`status`), что позволило:
- Расширить бизнес-логику (новый, в обработке, отправлен, доставлен, отменён).
- Добавить возможность обновления статуса через интерфейс.
- Продемонстрировать работу с обновлением (PUT) и расширением схемы БД.

---

## 3. Структура проекта

```
code_lab/lab_4/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── crud.py
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── k8s/
    └── fullstack.yaml
```

## 4. Листинги кода (основные файлы)

### 4.1 Backend – `backend/main.py` (сокращённо)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine, Base
from schemas import OrderCreate, OrderUpdate, OrderResponse
import crud

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Order System API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    if crud.get_order_by_number(db, order.order_number):
        raise HTTPException(400, "Order number already exists")
    return crud.create_order(db, order)

@app.get("/orders", response_model=List[OrderResponse])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order_update: OrderUpdate, db: Session = Depends(get_db)):
    db_order = crud.update_order(db, order_id, order_update)
    if not db_order:
        raise HTTPException(404, "Order not found")
    return db_order

@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    if not crud.delete_order(db, order_id):
        raise HTTPException(404, "Order not found")
```

### 4.2 Frontend – `frontend/app.py` (фрагмент с формой и статусом)

```python
import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8000")
status_options = ['новый', 'в обработке', 'отправлен', 'доставлен', 'отменён']

# Форма создания заказа
with st.sidebar:
    with st.form("create_order_form"):
        order_number = st.text_input("Order Number*")
        items = st.text_area("Items* (one per line)")
        amount = st.number_input("Total Amount*", min_value=0.01)
        address = st.text_area("Delivery Address*")
        status = st.selectbox("Status", status_options)
        submitted = st.form_submit_button("Create Order")
        if submitted:
            payload = { "order_number": order_number, "items": items_list,
                        "amount": amount, "delivery_address": address, "status": status }
            requests.post(f"{BACKEND_URL}/orders", json=payload)

# Отображение таблицы и обновление статуса
orders = fetch_orders()
if orders:
    df = pd.DataFrame(orders)
    df['items'] = df['items'].apply(lambda x: ", ".join(x))
    st.dataframe(df[['id','order_number','items','amount','delivery_address','status']])
    
    # Обновление статуса
    update_id = st.number_input("Order ID", key="upd_id")
    new_status = st.selectbox("New Status", status_options, key="new_st")
    if st.button("Update Status"):
        requests.put(f"{BACKEND_URL}/orders/{update_id}", json={"status": new_status})
```

### 4.3 Dockerfile (Backend)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.4 Kubernetes манифест – `k8s/fullstack.yaml` (фрагменты)

```yaml
# PostgreSQL Deployment + Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_USER
          value: "orderuser"
        - name: POSTGRES_PASSWORD
          value: "orderpass"
        - name: POSTGRES_DB
          value: "orders_db"
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
    - port: 5432

# Backend Deployment + Service (аналогично, image: my-backend:v3)
# Frontend Deployment + Service (type: NodePort, nodePort: 30080)
```


## 5. Трудности и их преодоление

В ходе выполнения работы возникло несколько **нетривиальных технических проблем**, которые были успешно решены.

### 5.1 Несовместимость синтаксиса Python 3.10+ с образом 3.9

**Проблема:**  
В коде использовался синтаксис объединения типов `str | None`, который появился в Python 3.10. Однако в `Dockerfile` был указан базовый образ `python:3.9-slim`. При запуске контейнера бэкенд падал с ошибкой:
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

**Решение:**  
Был переписан `schemas.py` с заменой `str | None` на `Optional[str]` (из `typing`), а `list[str]` на `List[str]`. Это обеспечило совместимость с Python 3.9.

### 5.2 Импорт локальных Docker-образов в MicroK8s

**Проблема:**  
Образы `my-backend:v2` и `my-frontend:v2` были собраны в Docker, но Kubernetes (containerd) не мог их найти – поды переходили в состояние `ImagePullBackOff`.

**Решение:**  
Вместо `docker push` (нет реестра) использовали двухэтапный импорт:
```bash
docker save my-backend:v2 | microk8s ctr image import -
docker save my-frontend:v2 | microk8s ctr image import -
```
При этом важно было избежать промежуточных tar-файлов из-за нехватки места на диске (использован прямой pipe).

### 5.3 Отсутствие Kubernetes Services для БД и бэкенда

**Проблема:**  
При проверке `kubectl get svc` обнаружилось, что сервисы `postgres-service` и `backend-service` не создались, хотя были прописаны в `fullstack.yaml`. Причина – синтаксическая ошибка в YAML (отсутствие разделителя `---` перед сервисами). В результате бэкенд не мог разрешить DNS-имена и падал с ошибкой:
```
could not translate host name "postgres-service" to address
```

**Решение:**  
Сервисы были созданы вручную через `kubectl expose`:
```bash
microk8s kubectl expose deployment postgres-deploy --port=5432 --target-port=5432 --name=postgres-service
microk8s kubectl expose deployment backend-deploy --port=8000 --target-port=8000 --name=backend-service
```
После этого поды бэкенда и фронтенда успешно нашли друг друга.

### 5.4 Сбой сетевого плагина Calico

**Проблема:**  
Поды зависали в состоянии `ContainerCreating` с ошибкой:
```
plugin type="calico" failed (add): error getting ClusterInformation: connection is unauthorized: Unauthorized
```

**Решение:**  
Перезапуск пода Calico в пространстве `kube-system`:
```bash
microk8s kubectl rollout restart daemonset calico-node -n kube-system
microk8s kubectl rollout restart deployment calico-kube-controllers -n kube-system
```
После этого сеть заработала, и поды перешли в `Running`.

### 5.5 Нехватка места на диске при сборке образов

**Проблема:**  
При попытке сохранить образы в tar-файлы возникала ошибка `no space left on device`. Диск виртуальной машины (68 ГБ) был заполнен на 58%, но свободного места оказалось недостаточно из-за кэша Docker и старых образов.

**Решение:**  
Очистка Docker и MicroK8s:
```bash
docker system prune -a -f
microk8s ctr image list | grep -v k8s | xargs -r microk8s ctr image rm
```
А также была использована прямая передача через pipe (избегая создания больших временных файлов).

### 5.6 Добавление поля «статус» (сверх требований)

Хотя по заданию требовались только базовые поля, было решено расширить функциональность для более реалистичного использования. Это потребовало:
- Добавления колонки `status` в модель `models.py` и в схему `schemas.py`.
- Выполнения миграции БД (без потери данных):
  ```sql
  ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'новый';
  ```
- Модификации интерфейса: выбор статуса при создании, отображение в таблице, отдельная форма для обновления статуса через PUT-запрос.
- Пересборки образов с тегом `v3` и обновления деплойментов.

Этот опыт показал, как легко расширять приложение без остановки работы кластера.

---

## 6. Последовательность команд для развёртывания

Ниже приведён итоговый порядок действий, который привёл к работающему приложению.

```bash
# 1. Очистка предыдущих ресурсов
microk8s kubectl delete deployment --all
microk8s kubectl delete svc backend-service frontend-service postgres-service

# 2. Сборка образов с тегом v3 (исправленный код + статус)
cd backend
docker build -t my-backend:v3 .
cd ../frontend
docker build -t my-frontend:v3 .

# 3. Импорт образов в MicroK8s
docker save my-backend:v3 | microk8s ctr image import -
docker save my-frontend:v3 | microk8s ctr image import -

# 4. Применение манифеста (после исправления синтаксиса YAML)
cd ../k8s
microk8s kubectl apply -f fullstack.yaml

# 5. Ручное создание отсутствующих сервисов
microk8s kubectl expose deployment postgres-deploy --port=5432 --target-port=5432 --name=postgres-service
microk8s kubectl expose deployment backend-deploy --port=8000 --target-port=8000 --name=backend-service

# 6. Проверка статуса подов
microk8s kubectl get pods -w

# 7. Добавление колонки status в существующую БД (если не пересоздавали под)
microk8s kubectl exec -it deployment/postgres-deploy -- psql -U orderuser -d orders_db -c "ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'новый';"

# 8. Обновление образов в деплойментах
microk8s kubectl set image deployment/backend-deploy backend=my-backend:v3
microk8s kubectl set image deployment/frontend-deploy frontend=my-frontend:v3

# 9. Доступ к приложению
# Открыть в браузере http://localhost:30080
```

---

## 7. Скриншоты

### 7.1 Сборка образов

![Сборка backend](screenshots/docker_build_backend.png)  
*Команда `docker build -t my-backend:v3` успешно выполнена.*

![Сборка frontend](screenshots/docker_build_frontend.png)  
*Использован флаг `--no-cache` для принудительного копирования обновлённого кода.*

### 7.2 Статус подов в Kubernetes

![kubectl get pods](screenshots/kubectl_get_pods.png)  
*Все три пода: postgres-deploy, backend-deploy, frontend-deploy – в состоянии `Running` (1/1).*

### 7.3 Работающее приложение в браузере

![Форма создания заказа](screenshots/order_form.png)  

![Таблица заказов](screenshots/orders_table.png)  

## 8. Местонахождение файлов

Все файлы находся в данном репозитории [lab__4](code_lab/lab_4).

Так же приложен файл [команды в терминале](terminal_lab__4.sh). Неполный из-за прекращения отображения ранее использованных команд некоторое количество строк назад.

На всякий пожарный - [Ctrl+P страницы](OrderSystem.pdf). ~Форма немного съехала при проведение операции сохранения~

## 9. Заключение

В ходе лабораторной работы было создано и развёрнуто в кластере Kubernetes трёхзвенное приложение «Order System».  
Реализованы все обязательные CRUD-операции, а также дополнительная функция управления статусом заказа.  
Приложение работает стабильно, данные сохраняются в PostgreSQL, интерфейс доступен через NodePort.  
Преодолены реальные проблемы, связанные с версиями Python, импортом образов в containerd, настройкой Kubernetes Services и сетевым плагином Calico.

---

## UPD

**UPD-1: Можно добавить суммирование количество заказов и сумму прибыли... но пока это только идея без реализации. Может быть - когда-нибудь в ~ближайшем~ далёком будущем осуществлю при необходимости. А пока это не входит в задание.**

**UPD-2: Можно добавить колонку "Количество товаров". Может стоит реализовать? Так будет как-то выглядеть эстетичнее. По UPD-1 можно вывести небольшую табличку. Точнее 2: "Количество заказов и прибыль" и "Количество заказов по статусу"**

## Реализация UPD

Обновленный `frontend/app.py`
```python
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
```

Строчка `backend/models.py`
```python
items = Column(JSON, nullable=False)   # пример: [{"name": "мышь", "quantity": 10}, ...]
```

 `backend/schemas.py`
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class OrderItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=10000)

class OrderCreate(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=50)
    items: List[OrderItem]   # теперь список объектов с name и quantity
    amount: float = Field(..., gt=0)
    delivery_address: str = Field(..., min_length=5)
    status: Optional[str] = Field('новый', max_length=50)

    @validator('order_number')
    def order_number_alphanumeric(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Order number must be alphanumeric (dash/underscore allowed)')
        return v

class OrderUpdate(BaseModel):
    order_number: Optional[str] = None
    items: Optional[List[OrderItem]] = None
    amount: Optional[float] = Field(None, gt=0)
    delivery_address: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)

class OrderResponse(OrderCreate):
    id: int
    class Config:
        orm_mode = True
```
