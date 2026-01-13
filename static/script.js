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

    // Сначала пробуем показать то, что есть
    let rates = await tryGetRates(date);
    if (rates) {
        showResult(rates);
        return;
    }

    // Если данных нет — обновляем
    showError("Данные не найдены. Запрашиваем у ЦБ...");
    const ok = await fetchAndSaveRates(date);
    if (ok) {
        // Ждём немного и запрашиваем снова
        setTimeout(async () => {
            const fresh = await tryGetRates(date);
            if (fresh) {
                showResult(fresh);
            } else {
                showError("Данные обновлены, но не появились в БД");
            }
        }, 1000);
    }
}

async function fetchAndSaveRates(date) {
    try {
        const res = await fetch(`https://functions.yandexcloud.net/d4ee03meuoirktv7k4ol?date=${date}`);
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Ошибка обновления");
        return true;
    } catch (e) {
        showError("Не удалось обновить курсы: " + e.message);
        return false;
    }
}

async function tryGetRates(date) {
    try {
        const res = await fetch(`/api/rates?date=${date}`);
        const data = await res.json();
        if (data.error) return null;
        let html = `<h3>Курсы на ${data.date}:</h3><table>`;
        html += `<tr><th>Валюта</th><th>Курс</th></tr>`;
        for (const [code, rate] of Object.entries(data.rates)) {
            html += `<tr>
                <td data-label="Валюта">${code}</td>
                <td data-label="Курс">${rate.toFixed(5)}</td>
            </tr>`;
        }
        html += `</table>`;
        return html;
    } catch (e) {
        showError("Ошибка соединения с сервером");
        return null;
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
        // let html = `<table><tr><th>Дата курса</th><th>Валюта</th><th>Курс</th><th>Сохранено</th></tr>`;
        // data.history.forEach(r => {
        //     html += `<tr><td>${r.date}</td><td>${r.currency}</td><td>${r.rate.toFixed(5)}</td><td>${r.saved_at.split(' ')[0]}</td></tr>`;
        // });
        // html += `</table>`;

        let html = `<table>`;
        html += `<tr>
            <th>Дата курса</th>
            <th>Валюта</th>
            <th>Курс</th>
            <th>Сохранено</th>
        </tr>`;
        data.history.forEach(r => {
            html += `<tr>
                <td data-label="Дата курса">${r.date}</td>
                <td data-label="Валюта">${r.currency}</td>
                <td data-label="Курс">${r.rate.toFixed(5)}</td>
                <td data-label="Сохранено">${r.saved_at.split(' ')[0]}</td>
            </tr>`;
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