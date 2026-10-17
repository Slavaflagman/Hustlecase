const CASES = {
  '1': { 
    id: '1', 
    name: 'Snake Case', 
    price: 99, 
    items: [
      { name: 'Тюльпан (Дешёвый мусор)', value: 25, isNft: false },
      { name: 'Golden Snake Box (NFT)', value: 500, isNft: true }
    ] 
  },
  '2': { 
    id: '2', 
    name: 'Sakura Case', 
    price: 300, 
    items: [
      { name: 'Лепесток (Дешёвый мусор)', value: 50, isNft: false },
      { name: 'Sakura Flower (NFT)', value: 2500, isNft: true }
    ] 
  }
};

let payoutPool = 0;   
let ownerProfit = 0;  

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const { caseId, telegramPaymentChargeId, userBalance } = req.body;
  const targetCase = CASES[caseId];

  if (!targetCase) return res.status(404).json({ error: 'Кейс не найден' });

  if (!telegramPaymentChargeId && userBalance < targetCase.price) {
    return res.status(400).json({ 
      error: 'Нужно пополнить баланс через Telegram Stars!',
      needPayment: true 
    });
  }

  const ownerShare = Math.floor(targetCase.price * 0.60);
  const poolShare = targetCase.price - ownerShare;

  ownerProfit += ownerShare;
  payoutPool += poolShare;

  const trashItem = targetCase.items[0];
  const nftItem = targetCase.items[1];

  let wonItem = trashItem;
  let isJackpot = false;

  if (payoutPool >= nftItem.value) {
    if (Math.random() < 0.08) {
      wonItem = nftItem;
      payoutPool -= nftItem.value;
      isJackpot = true;
    }
  }

  const newBalance = userBalance - targetCase.price + (wonItem.isNft ? 0 : wonItem.value);

  return res.status(200).json({
    success: true,
    wonItem,
    isJackpot,
    newBalance,
    payoutPool,
    ownerProfit
  });
}
