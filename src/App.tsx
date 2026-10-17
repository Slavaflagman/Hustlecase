import React, { useState, useEffect } from 'react';

// Ваш Telegram ID владельца
const ADMIN_TELEGRAM_ID = 8510236481;

export default function HustleCaseApp() {
  const [userId, setUserId] = useState<number | null>(null);
  const [username, setUsername] = useState<string>('Игрок');
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  // У всех новых игроков изначально 0 звёзд
  const [balance, setBalance] = useState<number>(0);
  const [customStarsInput, setCustomStarsInput] = useState<number>(99);
  const [showTopUpModal, setShowTopUpModal] = useState<boolean>(false);

  const [activeTab, setActiveTab] = useState<'main' | 'admin'>('main');
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [opening, setOpening] = useState<boolean>(false);
  const [wonItem, setWonItem] = useState<any>(null);

  // Статистика и мониторинг для владельца
  const [stats, setStats] = useState({ ownerProfit: 0, payoutPool: 0 });
  const [pendingPayouts, setPendingPayouts] = useState<any[]>([]);
  const [activePlayers, setActivePlayers] = useState<any[]>([
    { id: 8510236481, name: '@slava', balance: 0, status: 'В сети' },
    { id: 1029384756, name: '@user_test', balance: 150, status: 'Крутит кейс' }
  ]);
  const [liveLogs, setLiveLogs] = useState<any[]>([]);

  useEffect(() => {
    if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
      const tgUser = window.Telegram.WebApp.initDataUnsafe.user;
      setUserId(tgUser.id);
      setUsername(tgUser.username ? `@${tgUser.username}` : (tgUser.first_name || 'Игрок'));
      if (tgUser.id === ADMIN_TELEGRAM_ID) {
        setIsAdmin(true);
      }
    } else {
      setUserId(ADMIN_TELEGRAM_ID);
      setUsername('@slava');
      setIsAdmin(true);
    }
  }, []);

  // Оплата Telegram Stars (от 50 до 1000 звёзд)
  const handlePayStars = async (amount: number) => {
    if (amount < 50 || amount > 1000) {
      alert('Сумма доната должна быть от 50 до 1000 звёзд');
      return;
    }

    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openInvoice(`https://t.me/invoice_placeholder_${amount}`, (status: string) => {
        if (status === 'paid') {
          setBalance(prev => prev + amount);
          setShowTopUpModal(false);
          alert(`Успешно пополнено на ${amount} звёзд`);
        }
      });
    } else {
      setBalance(prev => prev + amount);
      setShowTopUpModal(false);
      alert(`Тестовое пополнение на ${amount} звёзд`);
    }
  };

  const handleOpenCase = async (c: any) => {
    if (balance < c.price) {
      setShowTopUpModal(true);
      return;
    }

    setSelectedCase(c);
    setOpening(true);
    setWonItem(null);

    try {
      const res = await fetch('/api/open-case', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          caseId: c.id,
          userBalance: balance,
          userId: userId || 0,
          telegramPaymentChargeId: "real_stars_verified"
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      setTimeout(() => {
        setBalance(data.newBalance);
        setWonItem(data.wonItem);

        // Фиксация активности для админ-панели
        const newLog = {
          id: Date.now(),
          user: username,
          caseName: c.name,
          won: data.wonItem.name,
          price: c.price,
          time: new Date().toLocaleTimeString()
        };
        setLiveLogs(prev => [newLog, ...prev]);

        if (data.isJackpot) {
          setPendingPayouts(prev => [...prev, { id: Date.now(), user: username, userId, item: data.wonItem.name }]);
        }
        if (data.ownerProfit !== undefined) {
          setStats({ ownerProfit: data.ownerProfit, payoutPool: data.payoutPool });
        }
        setOpening(false);
      }, 1500);

    } catch (err: any) {
      alert(err.message || 'Ошибка сервера');
      setOpening(false);
    }
  };

  const casesList = [
    { id: '1', name: 'Snake Case', price: 99, tag: 'Старт', tagColor: '#10b981', desc: 'Honey Bee / Обычный' },
    { id: '2', name: 'Sakura Case', price: 300, tag: 'Хит', tagColor: '#3b82f6', desc: 'Legionary / Black' },
    { id: '3', name: 'Cigar Case', price: 350, tag: 'Премиум', tagColor: '#ef4444', desc: 'Smoke Sway / Snoop' },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0e0e11', color: '#fff', fontFamily: '-apple-system, sans-serif', padding: '16px', boxSizing: 'border-box', paddingBottom: '90px' }}>
      
      {/* Шапка */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #222', paddingBottom: '12px' }}>
        <div>
          <div style={{ fontWeight: '800', fontSize: '16px', letterSpacing: '0.5px' }}>HUSTLE GIFTS</div>
          <div style={{ fontSize: '11px', color: '#888' }}>{isAdmin ? 'Владелец системы' : 'Кейсы Telegram Stars'}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button onClick={() => setShowTopUpModal(true)} style={{ background: '#f59e0b', color: '#000', border: 'none', padding: '6px 12px', borderRadius: '8px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>
            + Пополнить
          </button>
          <div style={{ background: '#1c1c22', border: '1px solid #333', padding: '6px 12px', borderRadius: '12px', fontSize: '13px', fontWeight: 'bold', color: '#fbbf24' }}>
            Баланс: {balance} Stars
          </div>
        </div>
      </div>

      {/* Окно выбора суммы доната */}
      {showTopUpModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, padding: '16px' }}>
          <div style={{ background: '#16161c', border: '1px solid #333', borderRadius: '14px', padding: '20px', width: '100%', maxWidth: '340px', textAlign: 'center', position: 'relative' }}>
            <button onClick={() => setShowTopUpModal(false)} style={{ position: 'absolute', top: '12px', right: '12px', background: 'none', border: 'none', color: '#888', fontSize: '16px', cursor: 'pointer' }}>Закрыть</button>
            
            <h3 style={{ margin: '0 0 6px 0', fontSize: '16px' }}>Пополнение баланса</h3>
            <p style={{ fontSize: '11px', color: '#888', marginBottom: '16px' }}>Укажите сумму от 50 до 1000 звёзд</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '14px' }}>
              {[50, 99, 200, 350, 500, 1000].map(val => (
                <button key={val} onClick={() => setCustomStarsInput(val)} style={{ background: customStarsInput === val ? '#3b82f6' : '#222', color: '#fff', border: '1px solid #333', padding: '8px', borderRadius: '6px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer' }}>
                  {val} Stars
                </button>
              ))}
            </div>

            <div style={{ marginBottom: '16px' }}>
              <input 
                type="number" 
                min="50" 
                max="1000" 
                value={customStarsInput} 
                onChange={(e) => setCustomStarsInput(Number(e.target.value))}
                style={{ width: '100%', padding: '10px', background: '#0e0e11', border: '1px solid #3b82f6', borderRadius: '6px', color: '#fbbf24', fontSize: '16px', fontWeight: 'bold', textAlign: 'center', boxSizing: 'border-box' }}
              />
            </div>

            <button onClick={() => handlePayStars(customStarsInput)} style={{ width: '100%', padding: '12px', background: '#10b981', color: '#000', border: 'none', borderRadius: '8px', fontWeight: 'bold', fontSize: '13px', cursor: 'pointer' }}>
              Оплатить {customStarsInput} Stars через Telegram
            </button>
          </div>
        </div>
      )}

      {/* Экран кейсов для пользователей */}
      {activeTab === 'main' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {casesList.map(c => (
              <div key={c.id} onClick={() => !opening && handleOpenCase(c)} style={{ background: '#16161c', border: '1px solid #262630', borderRadius: '12px', padding: '14px', cursor: 'pointer', position: 'relative' }}>
                <span style={{ position: 'absolute', top: '10px', right: '10px', background: c.tagColor, color: '#000', fontSize: '9px', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>{c.tag}</span>
                <div style={{ fontSize: '14px', fontWeight: 'bold', marginTop: '12px' }}>{c.name}</div>
                <div style={{ fontSize: '10px', color: '#777', marginBottom: '10px' }}>{c.desc}</div>
                <div style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '13px' }}>{c.price} Stars</div>
              </div>
            ))}
          </div>

          {selectedCase && (
            <div style={{ marginTop: '20px', background: '#16161c', border: '1px solid #3b82f6', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '14px' }}>Кейс: {selectedCase.name}</h3>
              <div style={{ background: '#0e0e11', border: '1px solid #222', padding: '16px', borderRadius: '8px', marginBottom: '14px', fontSize: '13px' }}>
                {opening ? (
                  <span style={{ color: '#3b82f6' }}>Обработка запроса...</span>
                ) : wonItem ? (
                  <div>
                    <div style={{ color: wonItem.isNft ? '#f59e0b' : '#aaa', fontWeight: 'bold', fontSize: '15px' }}>Выпало: {wonItem.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>Ценность: +{wonItem.value} Stars</div>
                    {wonItem.isNft && (
                      <div style={{ fontSize: '10px', color: '#10b981', marginTop: '6px' }}>Заявка отправлена владельцу на обработку</div>
                    )}
                  </div>
                ) : (
                  <span style={{ color: '#666' }}>Нажмите кнопку ниже для открытия</span>
                )}
              </div>
              <button onClick={() => handleOpenCase(selectedCase)} disabled={opening} style={{ width: '100%', padding: '12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer' }}>
                {opening ? 'Открытие...' : `Открыть за ${selectedCase.price} Stars`}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Панель Владельца */}
      {activeTab === 'admin' && isAdmin && (
        <div style={{ background: '#16161c', border: '1px solid #fbbf24', borderRadius: '12px', padding: '16px' }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#fbbf24', fontSize: '15px' }}>Панель управления владельца</h3>
          
          {/* Балансы кассы */}
          <div style={{ background: '#0e0e11', padding: '12px', borderRadius: '8px', marginBottom: '14px', fontSize: '12px' }}>
            <div style={{ color: '#10b981', fontWeight: 'bold', marginBottom: '4px' }}>Чистый доход (60%): {stats.ownerProfit} Stars</div>
            <div style={{ color: '#3b82f6', fontWeight: 'bold' }}>Банк выплат (40%): {stats.payoutPool} Stars</div>
          </div>

          {/* Список игроков онлайн */}
          <h4 style={{ fontSize: '12px', margin: '12px 0 6px 0', color: '#aaa', textTransform: 'uppercase' }}>Активные пользователи:</h4>
          <div style={{ background: '#0e0e11', borderRadius: '8px', padding: '8px', marginBottom: '14px' }}>
            {activePlayers.map(p => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #1a1a20', fontSize: '11px' }}>
                <div>
                  <span style={{ fontWeight: 'bold' }}>{p.name}</span> <span style={{ color: '#666' }}>(ID: {p.id})</span>
                </div>
                <div>
                  <span style={{ color: '#fbbf24', marginRight: '8px' }}>{p.balance} Stars</span>
                  <span style={{ color: '#10b981' }}>{p.status}</span>
                </div>
              </div>
            ))}
          </div>

          {/* История прокруток (Live Feed) */}
          <h4 style={{ fontSize: '12px', margin: '12px 0 6px 0', color: '#aaa', textTransform: 'uppercase' }}>История открытий кейсов:</h4>
          <div style={{ background: '#0e0e11', borderRadius: '8px', padding: '8px', maxHeight: '120px', overflowY: 'auto', marginBottom: '14px' }}>
            {liveLogs.length === 0 ? (
              <div style={{ fontSize: '11px', color: '#555' }}>История пока пуста</div>
            ) : (
              liveLogs.map(log => (
                <div key={log.id} style={{ fontSize: '10px', padding: '4px 0', borderBottom: '1px solid #1a1a20', color: '#ccc' }}>
                  [{log.time}] <strong style={{ color: '#3b82f6' }}>{log.user}</strong> открыл {log.caseName} за {log.price} Stars $\rightarrow$ <span style={{ color: '#fbbf24' }}>{log.won}</span>
                </div>
              ))
            )}
          </div>

          {/* Запросы выплат */}
          <h4 style={{ fontSize: '12px', margin: '12px 0 6px 0', color: '#aaa', textTransform: 'uppercase' }}>Запросы на выплату NFT:</h4>
          {pendingPayouts.length === 0 ? (
            <div style={{ fontSize: '11px', color: '#555' }}>Запросов нет</div>
          ) : (
            pendingPayouts.map(p => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#222', padding: '8px 12px', borderRadius: '6px', marginBottom: '8px', fontSize: '11px' }}>
                <div>
                  <div>{p.user} (ID: {p.userId})</div>
                  <div style={{ color: '#fbbf24', fontWeight: 'bold' }}>Приз: {p.item}</div>
                </div>
                <button onClick={() => {
                  alert(`Приз ${p.item} подтверждён для ${p.user}`);
                  setPendingPayouts(prev => prev.filter(x => x.id !== p.id));
                }} style={{ background: '#10b981', color: '#000', border: 'none', padding: '6px 10px', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>
                  Подтвердить выплату
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Навигация */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#121216', borderTop: '1px solid #222', display: 'flex', justifyContent: 'space-around', padding: '12px 0' }}>
        <button onClick={() => setActiveTab('main')} style={{ background: 'none', border: 'none', color: activeTab === 'main' ? '#3b82f6' : '#666', fontSize: '12px', fontWeight: 'bold' }}>Кейсы</button>
        {isAdmin && (
          <button onClick={() => setActiveTab('admin')} style={{ background: 'none', border: 'none', color: activeTab === 'admin' ? '#fbbf24' : '#666', fontSize: '12px', fontWeight: 'bold' }}>Владелец</button>
        )}
      </div>

    </div>
  );
}
