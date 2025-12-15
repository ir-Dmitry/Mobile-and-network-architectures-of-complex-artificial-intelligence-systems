const today = new Date().toISOString().split('T')[0];
document.getElementById('dateInput').value = today;

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function setPeriod(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    document.getElementById('dateInput').value = formatDate(d);
    getRates();
}

async function getRates() {
    const date = document.getElementById('dateInput').value;
    if (!date) {
        showError("Укажите дату");
        return;
    }

    showLoading(true);
    clearError();

    try {
        const res = await fetch(`/api/rates?date=${date}`);
        const data = await res.json();

        if (data.error) {
            showError(data.error);
            showResult("");
        } else {
            let html = `<h3>Курсы на ${data.date}:</h3><table><tr><th>Валюта</th><th>Курс</th></tr>`;
            for (const [code, rate] of Object.entries(data.rates)) {
                html += `<tr><td>${code}</td><td>${rate.toFixed(5)}</td></tr>`;
            }
            html += `</table>`;
            showResult(html);
        }
    } catch (e) {
        showError("Ошибка соединения с сервером");
    } finally {
        showLoading(false);
    }
}

async function loadHistory() {
    showLoading(true);
    try {
        const res = await fetch("/api/history?limit=30");
        const data = await res.json();
        if (!data.history || data.history.length === 0) {
            document.getElementById('history').innerHTML = "<p>История пуста</p>";
            return;
        }
        let html = `<table><tr><th>Дата курса</th><th>Валюта</th><th>Курс</th><th>Сохранено</th></tr>`;
        data.history.forEach(r => {
            html += `<tr><td>${r.date}</td><td>${r.currency}</td><td>${r.rate.toFixed(5)}</td><td>${r.saved_at.split(' ')[0]}</td></tr>`;
        });
        html += `</table>`;
        document.getElementById('history').innerHTML = html;
    } catch (e) {
        showError("Не удалось загрузить историю");
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(msg) {
    document.getElementById('error').textContent = msg;
}

function clearError() {
    document.getElementById('error').textContent = '';
}

function showResult(html) {
    document.getElementById('result').innerHTML = html;
}

// Загружаем историю при старте
loadHistory();