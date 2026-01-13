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

    clearError();
    clearResult();

    let rates = await tryGetRates(date);
    if (rates) {
        console.log("[getRates] Данные найдены в БД, отображаем");
        showResult(rates);
        return;
    }

    console.log("[getRates] Данные не найдены в БД, запрашиваем у ЦБ...");
    showError("Данные не найдены. Запрашиваем у ЦБ...");

    const ok = await fetchAndSaveRates(date);
    if (ok) {
        setTimeout(async () => {
            const fresh = await tryGetRates(date);
            if (fresh) {
                clearError();
                showResult(fresh);
            } else {
                console.error("[getRates] Данные НЕ появились в БД даже после обновления");
                showError("Данные обновлены, но не появились в БД");
            }
        }, 1000);
    } else {
        console.error("[getRates] Не удалось вызвать облачную функцию");
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
    console.log(`[tryGetRates] Запрашиваем данные из БД за дату: ${date}`);
    try {
        const url = `/api/rates?date=${date}`;
        const res = await fetch(url);
        console.log(`[tryGetRates] URL запроса:`, url);
        console.log(`[tryGetRates] Ответ от API:`, res.status, res.statusText);

        if (!res.ok) {
            console.error(`[tryGetRates] HTTP ошибка: ${res.status}`);
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        console.log(`[tryGetRates] Полученные данные:`, data);

        if (data.rates === null) {
            console.log("[tryGetRates] Данных в БД нет (rates: null)");
            return null;
        }

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
        console.error("[tryGetRates] ОШИБКА при запросе к API:", e);
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

        let html = `<table>`;
        html += `<tr>
            <th>Дата курса</th>
            <th>Валюта</th>
            <th>Курс</th>
            <th>Сохранено</th>
        </tr>`;
        data.history.forEach(r => {
            const savedDate = r.saved_at ? r.saved_at.split(' ')[0] : '—';
            html += `<tr>
                <td data-label="Дата курса">${r.date}</td>
                <td data-label="Валюта">${r.currency}</td>
                <td data-label="Курс">${r.rate.toFixed(5)}</td>
                <td data-label="Сохранено">${savedDate}</td>
            </tr>`;
        });
        html += `</table>`;
        document.getElementById('history').innerHTML = html;
    } catch (e) {
        showError("Не удалось загрузить историю");
        document.getElementById('history').innerHTML = "<p>Ошибка загрузки истории</p>";
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

function clearResult() {
    document.getElementById('result').innerHTML = '';
}

// Загружаем историю при старте
loadHistory();