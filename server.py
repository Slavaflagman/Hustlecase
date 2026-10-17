<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hustle Case & Crash</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #08090d;
            --card-bg: rgba(20, 22, 30, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --primary: #ffffff;
            --accent: #f3ba2f;
            --text-main: #ffffff;
            --text-muted: #8c909d;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            max-width: 480px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding-bottom: 40px;
        }

        /* Шапка */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 14px 18px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        .logo { font-size: 16px; font-weight: 700; letter-spacing: -0.5px; }
        .balance-badge { font-size: 13px; font-weight: 600; color: var(--accent); display: flex; align-items: center; gap: 6px; }

        /* Вкладки переключения */
        .tabs {
            display: flex;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            padding: 4px;
            border-radius: 14px;
        }
        .tab-btn {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 10px;
            font-weight: 600;
            font-size: 13px;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.2s;
        }
        .tab-btn.active {
            background: #ffffff;
            color: #08090d;
        }

        .view-section { display: none; flex-direction: column; gap: 16px; }
        .view-section.active { display: flex; }

        /* Карточки Bento */
        .bento-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 18px;
            backdrop-filter: blur(10px);
        }
        .section-title { font-size: 14px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px; }

        /* Список кейсов */
        .cases-grid { display: flex; flex-direction: column; gap: 10px; }
        .case-card {
            background: rgba(25, 28, 38, 0.5);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .case-info h3 { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
        .case-info p { font-size: 12px; color: var(--text-muted); }
        
        .action-btn {
            background: #ffffff;
            color: #08090d;
            border: none;
            padding: 10px 16px;
            font-weight: 700;
            font-size: 13px;
            border-radius: 10px;
            cursor: pointer;
        }

        /* Экран Краша */
        .crash-screen {
            background: #111318;
            border: 1px solid var(--card-border);
            border-radius: 14px;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
        }
        .crash-multiplier { font-size: 40px; font-weight: 700; letter-spacing: -1px; }
        .crash-status { font-size: 12px; color: var(--text-muted); margin-top: 6px; }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .input-row {
            display: flex;
            gap: 8px;
        }
        input {
            width: 100%;
            background: #1a1c24;
            border: 1px solid var(--card-border);
            color: #fff;
            padding: 12px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
        }
        .preset-btn {
            flex: 1;
            background: #1a1c24;
            border: 1px solid var(--card-border);
            color: #fff;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
        }

        /* Модальное окно рулетки кейсов */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(8, 9, 13, 0.9);
            backdrop-filter: blur(10px);
            z-index: 100;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .roulette-window {
            width: 90%; max-width: 400px; height: 110px;
            background: #151821; border: 1px solid var(--card-border);
            border-radius: 14px; overflow: hidden; position: relative; display: flex; align-items: center;
        }
        .roulette-pointer {
            position: absolute; top: 0; left: 50%; transform: translateX(-50%);
            width: 2px; height: 100%; background: #ffffff; z-index: 10;
        }
        .roulette-track { display: flex; position: absolute; left: 0; transition: transform 4s cubic-bezier(0.15, 0.85, 0.35, 1); }
        .roulette-item {
            min-width: 130px; height: 85px; background: #202430; margin: 0 6px; border-radius: 10px;
            display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 10px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .r-title { font-size: 12px; font-weight: 600; text-align: center; margin-bottom: 4px; }
        .r-price { font-size: 11px; color: var(--accent); }
    </style>
</head>
<body>

    <div class="container">
        <!-- Шапка -->
        <div class="header">
            <div class="logo">HUSTLE HUB</div>
            <div class="balance-badge" onclick="topUpTestBalance()">
                <span id="userBalanceVal">...</span> ⭐ <span style="font-size: 10px; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">+ тест</span>
            </div>
        </div>

        <!-- Навигация по вкладкам -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('cases', this)">Кейсы</button>
            <button class="tab-btn" onclick="switchTab('crash', this)">Краш</button>
        </div>

        <!-- ВКЛАДКА КЕЙСОВ -->
        <div id="casesView" class="view-section active">
            <div class="bento-card">
                <div class="section-title">Призовой пул платформы</div>
                <div style="font-size: 28px; font-weight: 700; color: var(--accent);" id="poolBalanceVal">... ⭐</div>
            </div>

            <div class="section-title">Доступные кейсы</div>
            <div class="cases-grid" id="casesContainer">
                <div style="color: var(--text-muted); text-align: center; padding: 20px;">Загрузка кассы...</div>
            </div>
        </div>

        <!-- ВКЛАДКА КРАША -->
        <div id="crashView" class="view-section">
            <div class="bento-card">
                <div class="crash-screen">
                    <div class="crash-multiplier" id="crashMultiplierView">1.00x</div>
                    <div class="crash-status" id="crashStatusView">Ожидание ставки</div>
                </div>

                <div style="margin-top: 15px;" class="input-group">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
                        <span>Сумма ставки</span>
                        <span>Целевой множитель</span>
                    </div>
                    <div class="input-row">
                        <input type="number" id="crashBetInput" value="50">
                        <input type="number" id="crashTargetInput" value="2.00" step="0.1">
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button class="preset-btn" onclick="addCrashBet(50)">+50</button>
                        <button class="preset-btn" onclick="addCrashBet(100)">+100</button>
                        <button class="preset-btn" onclick="addCrashBet(500)">+500</button>
                    </div>
                    <button class="action-btn" style="width: 100%; margin-top: 5px; padding: 14px;" onclick="startCrashGame()">Запустить ракету</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Модалка рулетки кейсов -->
    <div class="modal" id="rouletteModal">
        <div class="roulette-window">
            <div class="roulette-pointer"></div>
            <div class="roulette-track" id="rouletteTrack"></div>
        </div>
        <div style="margin-top: 20px; font-size: 16px; font-weight: 700;" id="rouletteResultText">Открытие кейса...</div>
        <button class="action-btn" style="margin-top: 20px; display: none;" id="closeRouletteBtn" onclick="closeRouletteModal()">Забрать в инвентарь</button>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        const userId = tg.initDataUnsafe?.user?.id || 12345;
        let casesData = [];

        // Инициализация данных
        function loadData() {
            fetch(`/api/user/${userId}`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('userBalanceVal').innerText = data.balance;
                });

            fetch('/api/cases')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('poolBalanceVal').innerText = data.payout_pool + ' ⭐';
                    casesData = data.cases;
                    const container = document.getElementById('casesContainer');
                    container.innerHTML = '';
                    
                    casesData.forEach(c => {
                        container.innerHTML += `
                            <div class="case-card">
                                <div class="case-info">
                                    <h3>${c.name}</h3>
                                    <p>Стоимость: ${c.price} ⭐</p>
                                </div>
                                <button class="action-btn" onclick="openCase(${c.id})">Открыть</button>
                            </div>
                        `;
                    });
                });
        }

        loadData();

        // Тестовое пополнение для проверки
        function topUpTestBalance() {
            fetch('/api/user/topup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, amount: 500 })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('userBalanceVal').innerText = data.balance;
                tg.HapticFeedback.notificationOccurred('success');
            });
        }

        // Переключение вкладок
        function switchTab(tabName, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabName + 'View').classList.add('active');
        }

        // --- ЛОГИКА ОТКРЫТИЯ КЕЙСА ---
        function openCase(caseId) {
            const caseItem = casesData.find(c => c.id === caseId);
            if (!caseItem) return;

            const modal = document.getElementById('rouletteModal');
            const track = document.getElementById('rouletteTrack');
            const resultText = document.getElementById('rouletteResultText');
            const closeBtn = document.getElementById('closeRouletteBtn');

            modal.style.display = 'flex';
            resultText.innerText = 'Вращение барабана...';
            closeBtn.style.display = 'none';
            track.style.transition = 'none';
            track.style.transform = 'translateX(0px)';

            // Запрос на бэкенд для определения выигрыша
            fetch('/api/spin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, case_id: caseId })
            })
            .then(res => {
                if (!res.ok) throw new Error('Недостаточно средств');
                return res.json();
            })
            .then(data => {
                document.getElementById('userBalanceVal').innerText = data.new_balance;
                
                // Рендерим ленту рулетки с выигрышем на 30 позиции
                let itemsHTML = '';
                const prizes = caseItem.prizes;
                for (let i = 0; i < 40; i++) {
                    let p = (i === 30) ? [data.prize, data.prize_cost] : prizes[Math.floor(Math.random() * prizes.length)];
                    itemsHTML += `
                        <div class="roulette-item">
                            <div class="r-title">${p[0]}</div>
                            <div class="r-price">${p[1]} ⭐</div>
                        </div>
                    `;
                }
                track.innerHTML = itemsHTML;

                setTimeout(() => {
                    tg.HapticFeedback.impactOccurred('medium');
                    track.style.transition = 'transform 4s cubic-bezier(0.15, 0.85, 0.35, 1)';
                    track.style.transform = `translateX(-${30 * 142 - 142}px)`;
                }, 50);

                setTimeout(() => {
                    tg.HapticFeedback.notificationOccurred('success');
                    resultText.innerText = `Вы выиграли: ${data.prize}!`;
                    closeBtn.style.display = 'block';
                    loadData();
                }, 4100);

            })
            .catch(err => {
                modal.style.display = 'none';
                alert('Ошибка: ' + err.message);
            });
        }

        function closeRouletteModal() {
            document.getElementById('rouletteModal').style.display = 'none';
        }

        // --- ЛОГИКА КРАША ---
        function addCrashBet(amount) {
            const input = document.getElementById('crashBetInput');
            input.value = parseInt(input.value || 0) + amount;
        }

        function startCrashGame() {
            const bet = parseInt(document.getElementById('crashBetInput').value);
            const target = parseFloat(document.getElementById('crashTargetInput').value);
            const multiplierView = document.getElementById('crashMultiplierView');
            const statusView = document.getElementById('crashStatusView');

            if (!bet || bet <= 0) {
                alert('Введите ставку');
                return;
            }

            statusView.innerText = "Ракеты взлетает...";
            multiplierView.innerText = "1.00x";

            fetch('/api/crash/play', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, bet: bet, target_multiplier: target })
            })
            .then(res => {
                if (!res.ok) throw new Error('Ошибка ставки');
                return res.json();
            })
            .then(data => {
                document.getElementById('userBalanceVal').innerText = data.new_balance;
                
                let current = 1.00;
                let interval = setInterval(() => {
                    current += 0.04;
                    if (current >= data.crashed_at || current >= target) {
                        clearInterval(interval);
                        if (data.won) {
                            multiplierView.innerText = data.crashed_at.toFixed(2) + 'x';
                            statusView.innerText = `Успешно! Выигрыш: ${data.payout} ⭐`;
                            tg.HapticFeedback.notificationOccurred('success');
                        } else {
                            multiplierView.innerText = data.crashed_at.toFixed(2) + 'x';
                            statusView.innerText = "КРАШ!";
                            tg.HapticFeedback.notificationOccurred('error');
                        }
                        loadData();
                    } else {
                        multiplierView.innerText = current.toFixed(2) + 'x';
                    }
                }, 40);
            })
            .catch(err => {
                statusView.innerText = "Недостаточно средств";
            });
        }
    </script>
</body>
</html>
