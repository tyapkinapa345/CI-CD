from flask import Flask, jsonify
import pandas as pd
import numpy as np
import random

app = Flask(__name__)

def generate_data(n=100000):
    """Генерирует синтетические данные о кредитных рисках (100 000 записей)"""
    data = {
        'client_id': range(1, n+1),
        'credit_score': np.random.randint(300, 851, n),
        'income': np.random.randint(20000, 200001, n),
        'debt': np.random.randint(0, 100001, n),
        'overdue': np.random.choice(['yes', 'no'], n, p=[0.3, 0.7])
    }
    return pd.DataFrame(data)

@app.route('/report')
def get_report():
    df = generate_data()  # теперь 100 000 строк
    
    median_credit_score = df['credit_score'].median()
    mode_overdue = df['overdue'].mode()[0]
    
    return jsonify({
        "status": "success",
        "metrics": {
            "median_credit_score": float(median_credit_score),
            "mode_overdue": mode_overdue
        },
        "sample_size": len(df)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

