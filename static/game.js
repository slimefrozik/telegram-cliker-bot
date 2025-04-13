const tg = window.Telegram.WebApp;
tg.expand();

let gameState = {
    coins: 0,
    clickPower: 1,
    autoIncome: 0,
    clickLevel: 1,
    autoLevel: 0,
    clickUpgradeCost: 10,
    autoUpgradeCost: 50
};

const elements = {
    coins: document.getElementById('coins'),
    clickBtn: document.getElementById('click-btn'),
    clickPower: document.getElementById('click-power'),
    clickLevel: document.getElementById('click-level'),
    clickPrice: document.getElementById('click-price'),
    autoLevel: document.getElementById('auto-level'),
    autoPrice: document.getElementById('auto-price')
};

// Загрузка сохранённых данных
function loadGame() {
    tg.sendData(JSON.stringify({ action: 'load' }));
    tg.onEvent('mainButtonClicked', sendGameData);
}

// Клик по кнопке
elements.clickBtn.addEventListener('click', () => {
    gameState.coins += gameState.clickPower;
    updateUI();
});

// Прокачка
document.querySelectorAll('.upgrade-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const type = this.dataset.type;
        const cost = type === 'click' ? gameState.clickUpgradeCost : gameState.autoUpgradeCost;
        
        if (gameState.coins >= cost) {
            gameState.coins -= cost;
            
            if (type === 'click') {
                gameState.clickPower += 1;
                gameState.clickLevel += 1;
                gameState.clickUpgradeCost = Math.floor(10 * Math.pow(1.3, gameState.clickLevel));
            } else {
                gameState.autoIncome += 1;
                gameState.autoLevel += 1;
                gameState.autoUpgradeCost = Math.floor(50 * Math.pow(1.5, gameState.autoLevel));
            }
            
            updateUI();
        }
    });
});

// Автоматический доход
setInterval(() => {
    gameState.coins += gameState.autoIncome;
    updateUI();
}, 1000);

// Обновление интерфейса
function updateUI() {
    elements.coins.textContent = gameState.coins;
    elements.clickPower.textContent = gameState.clickPower;
    elements.clickLevel.textContent = gameState.clickLevel;
    elements.clickPrice.textContent = gameState.clickUpgradeCost;
    elements.autoLevel.textContent = gameState.autoIncome;
    elements.autoPrice.textContent = gameState.autoUpgradeCost;
}

// Отправка данных боту
function sendGameData() {
    tg.sendData(JSON.stringify(gameState));
    tg.close();
}

loadGame();
updateUI();