import React, { useState, useEffect } from 'react';

// Твой реальный Telegram ID
const ADMIN_TELEGRAM_ID = 8510236481;

export default function HustleCaseApp() {
  const [userId, setUserId] = useState<number | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  const [balance, setBalance] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'main' | 'admin'>('main');
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [opening, setOpening] = useState<boolean>(false);
  const [wonItem, setWonItem] = useState<any>(null);

  // Данные кассы (доступны только тебе)
  const [stats, setStats] = useState({ ownerProfit: 0, payoutPool: 0 });
  const [pendingPayouts, setPendingPayouts] = useState<any[]>([]);

  useEffect(() => {
    // Получаем Telegram ID пользователя из Telegram WebApp API
    if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
      const tgUser = window.Telegram.WebApp.initDataUnsafe.user;
      setUserId(tgUser.id);
      if (tgUser.id === ADMIN_TELEGRAM_ID) {
        setIsAdmin(true);
      }
    } else {
      // Для тестов в обычном браузере
      setUserId(ADMIN_TELEGRAM_ID);
      setIsAdmin(true);
    }
  }, []);

  const casesList = [
    { id: '1', name: 'Snake Case', price: 99, tag: 'Старт', tagColor: '#10b981', desc: 'Honey Bee / Обычный', emoji: '📦' },
    { id: '2', name: 'Sakura Case', price: 300, tag: 'Хит', tagColor: '#3b82f6', desc: 'Legionary / Black', emoji: '🌸' },
  ];

  const handleTopUp = (amount: number) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openInvoice(`https://t.me/invoice_link_placeholder`, (status: string) => {
        if (status === 'paid') {
          setBalance(prev => prev + amount);
        }
      });
    } else {
      setBalance(prev => prev + amount);
    }
  };

  const handleOpenCase = async (c: any) => {
    if (balance < c.price) {
      alert('Недостаточно звезд! Пополни баланс.');
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
          userId: userId || 0
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      setTimeout(() => {
        setBalance(data.newBalance);
        setWonItem(data.wonItem);
        if (data.isJackpot) {
          setPendingPayouts(prev => [...prev, { id: Date.now(), user: userId, item: data.wonItem.name }]);
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

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0e0e11', color: '#fff', fontFamily: '-apple-system, sans-serif', padding: '16px', boxSizing: 'border-box', paddingBottom: '90px' }}>
      
      {/* Шапка */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #222', paddingBottom: '12px' }}>
        <div>
          <div style={{ fontWeight: '800', fontSize: '16px' }}>💎 HUSTLE GIFTS</div>
          <div style={{ fontSize: '11px', color: '#888' }}>{isAdmin ? '👑 ВЛАДЕЛЕЦ (АДМИН)' : 'Кейсы Telegram Stars'}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button onClick={() => handleTopUp(200)} style={{ background: '#f59e0b', color: '#000', border: 'none', padding: '6px 10px', borderRadius: '8px', fontSize: '11px', fontWeight: 'bold', cursor: 'pointer' }}>
            +200 ⭐️
          </button>
          <div style={{ background: '#1c1c22', border: '1px solid #333', padding: '6px 12px', borderRadius: '16px', fontSize: '13px', fontWeight: 'bold', color: '#fbbf24' }}>
            ⭐ {balance}
          </div>
        </div>
      </div>

      {/* Основной экран (для обычных игроков) */}
      {activeTab === 'main' && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {casesList.map(c => (
              <div key={c.id} onClick={() => !opening && handleOpenCase(c)} style={{ background: '#16161c', border: '1px solid #262630', borderRadius: '14px', padding: '14px', cursor: 'pointer', position: 'relative' }}>
                <span style={{ position: 'absolute', top: '10px', right: '10px', background: c.tagColor, color: '#000', fontSize: '9px', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>{c.tag}</span>
                <div style={{ fontSize: '28px', marginBottom: '8px' }}>{c.emoji}</div>
                <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{c.name}</div>
                <div style={{ fontSize: '10px', color: '#777', marginBottom: '10px' }}>{c.desc}</div>
                <div style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '13px' }}>⭐ {c.price}</div>
              </div>
            ))}
          </div>

          {selectedCase && (
            <div style={{ marginTop: '20px', background: '#16161c', border: '1px solid #3b82f6', borderRadius: '14px', padding: '16px', textAlign: 'center' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '14px' }}>Кейс: {selectedCase.name}</h3>
              <div style={{ background: '#0e0e11', border: '1px solid #222', padding: '16px', borderRadius: '10px', marginBottom: '14px', fontSize: '13px' }}>
                {opening ? (
                  <span style={{ color: '#3b82f6' }}>Крутим рулетку... 🔄</span>
                ) : wonItem ? (
                  <div>
                    <div style={{ color: wonItem.isNft ? '#f59e0b' : '#aaa', fontWeight: 'bold', fontSize: '15px' }}>Выпало: {wonItem.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>Ценность: +{wonItem.value} ⭐</div>
                    {wonItem.isNft && (
                      <div style={{ fontSize: '10px', color: '#10b981', marginTop: '6px' }}>⏳ Заявка отправлена владельцу на выплату</div>
                    )}
                  </div>
                ) : (
                  <span style={{ color: '#666' }}>Нажми кнопку ниже для открытия</span>
                )}
              </div>
              <button onClick={() => handleOpenCase(selectedCase)} disabled={opening} style={{ width: '100%', padding: '12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: 'bold', cursor: 'pointer' }}>
                {opening ? 'Открываем...' : `Открыть за ⭐ ${selectedCase.price}`}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Экран ТОЛЬКО ТВОЙ (Скрыт от всех остальных) */}
      {activeTab === 'admin' && isAdmin && (
        <div style={{ background: '#16161c', border: '1px solid #fbbf24', borderRadius: '14px', padding: '16px' }}>
          <h3 style={{ margin: '0 0 12px 0', color: '#fbbf24', fontSize: '15px' }}>👑 Касса и Выплаты (Админка)</h3>
          
          <div style={{ background: '#0e0e11', padding: '12px', borderRadius: '10px', marginBottom: '12px', fontSize: '12px' }}>
            <div style={{ color: '#10b981', fontWeight: 'bold', marginBottom: '4px' }}>💰 Твой чистый профит (60%): {stats.ownerProfit} ⭐</div>
            <div style={{ color: '#3b82f6', fontWeight: 'bold' }}>🏦 Банк выплат (40%): {stats.payoutPool} ⭐</div>
          </div>

          <h4 style={{ fontSize: '13px', margin: '10px 0' }}>Запросы на отправку подарков:</h4>
          {pendingPayouts.length === 0 ? (
            <div style={{ fontSize: '11px', color: '#666' }}>Новых выигранных NFT пока нет</div>
          ) : (
            pendingPayouts.map(p => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#222', padding: '8px 12px', borderRadius: '8px', marginBottom: '8px', fontSize: '11px' }}>
                <div>
                  <div>Победитель TG ID: {p.user}</div>
                  <div style={{ color: '#fbbf24', fontWeight: 'bold' }}>Приз: {p.item}</div>
                </div>
                <button onClick={() => {
                  alert(`Подарок ${p.item} подтвержден для пользователя ${p.user}!`);
                  setPendingPayouts(prev => prev.filter(x => x.id !== p.id));
                }} style={{ background: '#10b981', color: '#000', border: 'none', padding: '6px 10px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
                  Выплатить 🎁
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {/* Нижняя навигация */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#121216', borderTop: '1px solid #222', display: 'flex', justifyContent: 'space-around', padding: '12px 0' }}>
        <button onClick={() => setActiveTab('main')} style={{ background: 'none', border: 'none', color: activeTab === 'main' ? '#3b82f6' : '#666', fontSize: '12px', fontWeight: 'bold' }}>🎁 Кейсы</button>
        
        {/* Кнопка "Владелец" скроется от всех кроме аккаунта 8510236481 */}
        {isAdmin && (
          <button onClick={() => setActiveTab('admin')} style={{ background: 'none', border: 'none', color: activeTab === 'admin' ? '#fbbf24' : '#666', fontSize: '12px', fontWeight: 'bold' }}>👑 Владелец</button>
        )}
      </div>

    </div>
  );
}
