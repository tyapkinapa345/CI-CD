Шаг 2.2. Создайте папку в HDFS и загрузите файл
bash
docker exec -it namenode hdfs dfs -mkdir -p /finance/paysim_raw
docker exec -it namenode hdfs dfs -put /data/paysim_50k.csv /finance/paysim_raw/
3️⃣ Создание внешней таблицы в Hive (под вашу структуру)
Подключитесь к beeline:

bash
docker exec -it hive-server beeline -u jdbc:hive2://localhost:10000
Выполните:

sql
USE finance;

CREATE EXTERNAL TABLE IF NOT EXISTS paysim_raw (
    step INT,
    type STRING,
    amount DOUBLE,
    nameOrig STRING,
    oldbalanceOrg DOUBLE,
    newbalanceOrig DOUBLE,
    nameDest STRING,
    oldbalanceDest DOUBLE,
    newbalanceDest DOUBLE,
    isFraud INT,
    isFlaggedFraud INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'      -- в вашем примере разделитель табуляция? Проверьте. Если запятая, замените на ','
STORED AS TEXTFILE
LOCATION '/finance/paysim_raw'
TBLPROPERTIES ("skip.header.line.count"="1");
⚠️ Важно: уточните разделитель в вашем CSV. В примере выше он похож на табуляцию (визуально столбцы разделены пробелами, но в реальности может быть \t). Если файл с запятыми, используйте FIELDS TERMINATED BY ','.

Как проверить разделитель на хосте:

bash
head -1 ~/Downloads/bill16/paysim_50k.csv | cat -A
Если видите ^I – это табуляция. Если , – запятая.

4️⃣ Проверка загрузки
sql
SELECT COUNT(*) FROM paysim_raw;
SELECT * FROM paysim_raw LIMIT 10;
5️⃣ Оптимизированная таблица (Parquet + партиционирование)
Партиционировать логично по step (это номер часа/шага) или по type (тип транзакции). Для анализа трендов во времени лучше по step.

sql
CREATE TABLE paysim_opt (
    type STRING,
    amount DOUBLE,
    nameOrig STRING,
    oldbalanceOrg DOUBLE,
    newbalanceOrig DOUBLE,
    nameDest STRING,
    oldbalanceDest DOUBLE,
    newbalanceDest DOUBLE,
    isFraud INT,
    isFlaggedFraud INT
)
PARTITIONED BY (step INT)
STORED AS PARQUET;

SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT OVERWRITE TABLE paysim_opt PARTITION(step)
SELECT 
    type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    nameDest, oldbalanceDest, newbalanceDest,
    isFraud, isFlaggedFraud,
    step
FROM paysim_raw;
6️⃣ Аналитические запросы (HiveQL)
6.1. Общая сумма транзакций по типу (PAYMENT, TRANSFER, CASH_OUT, DEBIT)
sql
SELECT type, COUNT(*) AS cnt, SUM(amount) AS total_amount, AVG(amount) AS avg_amount
FROM paysim_opt
GROUP BY type
ORDER BY total_amount DESC;
6.2. Доля мошеннических транзакций по типу
sql
SELECT type, 
       COUNT(*) AS total_tx,
       SUM(isFraud) AS fraud_tx,
       ROUND(SUM(isFraud)*100.0/COUNT(*), 2) AS fraud_percent
FROM paysim_opt
GROUP BY type
ORDER BY fraud_percent DESC;
6.3. Транзакции, где баланс отправителя после перевода стал нулевым (подозрительно)
sql
SELECT step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, isFraud
FROM paysim_opt
WHERE newbalanceOrig = 0 AND amount > 0
LIMIT 20;
6.4. Количество мошеннических операций по шагам (временной ряд)
sql
SELECT step, COUNT(*) AS frauds_per_step
FROM paysim_opt
WHERE isFraud = 1
GROUP BY step
ORDER BY step;
6.5. Топ-10 получателей, на которых переведено больше всего денег (возможные «дропы»)
sql
SELECT nameDest, SUM(amount) AS total_received, COUNT(*) AS tx_count
FROM paysim_opt
WHERE type IN ('TRANSFER', 'CASH_OUT')
GROUP BY nameDest
ORDER BY total_received DESC
LIMIT 10;
6.6. Аномалии: транзакции, где сумма превышает 3 стандартных отклонения от среднего по типу
sql
WITH stats AS (
    SELECT type, AVG(amount) AS avg_amt, STDDEV(amount) AS std_amt
    FROM paysim_opt
    GROUP BY type
)
SELECT p.step, p.type, p.amount, p.isFraud
FROM paysim_opt p
JOIN stats s ON p.type = s.type
WHERE p.amount > s.avg_amt + 3 * s.std_amt
LIMIT 50;
6.7. Корреляция между isFlaggedFraud и isFraud (насколько точен флаг)
sql
SELECT 
    SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 1 THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 0 THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN isFlaggedFraud = 0 AND isFraud = 1 THEN 1 ELSE 0 END) AS false_negatives
FROM paysim_opt;
7️⃣ Оптимизация запросов (для больших данных)
Включите векторизацию:
SET hive.vectorized.execution.enabled = true;

Используйте бакетирование, если часто группируете по nameOrig или nameDest:

sql
CLUSTERED BY (nameOrig) INTO 16 BUCKETS;
Для ускорения агрегаций по типу можно создать материализованное представление (Hive 3.0+).

8️⃣ Экспорт результатов для визуализации
sql
-- Пример выгрузки в CSV (через beeline)
!outputformat csv2
SELECT step, SUM(amount) AS daily_sum FROM paysim_opt GROUP BY step ORDER BY step;
