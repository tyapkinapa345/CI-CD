const express = require('express');
const ss = require('simple-statistics');

const app = express();
const PORT = process.env.PORT || 5000;

// Генерация синтетических данных о кредитных рисках
function generateData(n = 100) {
  const clients = [];
  for (let i = 1; i <= n; i++) {
    clients.push({
      client_id: i,
      credit_score: Math.floor(Math.random() * (850 - 300 + 1) + 300), // от 300 до 850
      income: Math.floor(Math.random() * (200000 - 20000 + 1) + 20000), // от 20k до 200k
      debt: Math.floor(Math.random() * (100000 - 0 + 1) + 0),           // от 0 до 100k
      overdue: Math.random() < 0.3 ? 'yes' : 'no'                       // 30% просрочек
    });
  }
  return clients;
}

// Маршрут для аналитического отчёта
app.get('/report', (req, res) => {
  const data = generateData(150);  // генерируем 150 записей

  // Извлекаем кредитные рейтинги для расчёта медианы
  const creditScores = data.map(c => c.credit_score);
  const medianCreditScore = ss.median(creditScores);

  // Для моды собираем все значения поля overdue
  const overdueValues = data.map(c => c.overdue);
  const modeOverdue = ss.mode(overdueValues);

  res.json({
    status: 'success',
    metrics: {
      median_credit_score: medianCreditScore,
      mode_overdue: modeOverdue
    },
    sample_size: data.length
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});