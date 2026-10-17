import React, { useState } from 'react';

export default function HustleCaseApp() {
  const [balance, setBalance] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'main' | 'profile'>('main');
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [opening, setOpening] = useState<boolean>(false);
  const [wonItem, setWonItem] = useState<any>(null);

  const casesList = [
    { id: '1', name: 'Snake Case', price: 99, tag: 'Старт', tagColor: '#10b981', desc: 'Honey Bee / Обычный', emoji: '📦' },
    { id: '2', name: 'Sakura Case', price: 300, tag: 'Хит', tagColor: '#3b82f6', desc: 'Legionary / Black', emoji: '🌸' },
  ];

  // Пополнение баланса реальными звездами Telegram Stars
  const handleTopUp = (amount: number) => {
    if (window.Telegram?.WebApp) {
      // Здесь вызываем счет Telegram Stars
      window.Telegram.WebApp.openInvoice(`https://t.me/invoice_link_placeholder`, (status: string) => {
        if (status === 'paid') {
          setBalance(prev => prev + amount);
          alert(`Успешно пополнено на ⭐️ ${amount}!`);
        }
      });
    } else {
      // Фолбэк для теста вне ТГ
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
          telegramPaymentChargeId: "real_stars_paid"
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error);

      setTimeout(() => {
        setBalance(data.newBalance);
        setWonItem(data.wonItem);
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
          <div style={{ fontSize: '11px', color: '#888' }}>Кейсы Telegram Stars</div>
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

      {/* Список кейсов */}
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
                  <span style={{ color: '#3b82f6' }}>Проверяем баланс и крутим... 🔄</span>
                ) : wonItem ? (
                  <div>
                    <div style={{ color: wonItem.isNft ? '#f59e0b' : '#aaa', fontWeight: 'bold', fontSize: '15px' }}>Выпало: {wonItem.name}</div>
                    <div style={{ fontSize: '11px', color: '#888' }}>Ценность: +{wonItem.value} ⭐</div>
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

      {/* Нижняя навигация */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#121216', borderTop: '1px solid #222', display: 'flex', justifyContent: 'space-around', padding: '12px 0' }}>
        <button onClick={() => setActiveTab('main')} style={{ background: 'none', border: 'none', color: '#3b82f6', fontSize: '12px', fontWeight: 'bold' }}>🎁 Кейсы</button>
      </div>
    </div>
  );
}
