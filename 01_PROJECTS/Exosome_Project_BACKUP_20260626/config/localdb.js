// ExoMuse 本地測試版本 — 資料存在 localStorage
// 模擬 Firebase 操作，不需任何後端

// ── 本地資料庫操作 ──
const LocalDB = {
    // 取得資料
    get(key, defaultValue = []) {
        try {
            return JSON.parse(localStorage.getItem(`exomuse_${key}`)) || defaultValue;
        } catch {
            return defaultValue;
        }
    },
    
    // 儲存資料
    set(key, data) {
        localStorage.setItem(`exomuse_${key}`, JSON.stringify(data));
    },
    
    // 產生 ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    },
    
    // 商品管理
    products: {
        getAll() {
            return LocalDB.get('products', []);
        },
        getById(id) {
            return LocalDB.products.getAll().find(p => p.id === id);
        },
        add(product) {
            const products = LocalDB.products.getAll();
            const newProduct = {
                ...product,
                id: LocalDB.generateId(),
                active: true,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            products.push(newProduct);
            LocalDB.set('products', products);
            return newProduct.id;
        },
        update(id, data) {
            const products = LocalDB.products.getAll();
            const index = products.findIndex(p => p.id === id);
            if (index >= 0) {
                products[index] = { ...products[index], ...data, updatedAt: new Date().toISOString() };
                LocalDB.set('products', products);
            }
        },
        delete(id) {
            const products = LocalDB.products.getAll();
            const index = products.findIndex(p => p.id === id);
            if (index >= 0) {
                products[index].active = false;
                LocalDB.set('products', products);
            }
        },
        getActive() {
            return LocalDB.products.getAll().filter(p => p.active);
        }
    },
    
    // 訂單管理
    orders: {
        getAll() {
            return LocalDB.get('orders', []);
        },
        add(order) {
            const orders = LocalDB.orders.getAll();
            const newOrder = {
                ...order,
                id: LocalDB.generateId(),
                status: 'pending',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            orders.unshift(newOrder);
            LocalDB.set('orders', orders);
            return newOrder.id;
        },
        updateStatus(id, status, note = '') {
            const orders = LocalDB.orders.getAll();
            const index = orders.findIndex(o => o.id === id);
            if (index >= 0) {
                orders[index].status = status;
                orders[index].statusNote = note;
                orders[index].updatedAt = new Date().toISOString();
                LocalDB.set('orders', orders);
            }
        },
        getByStatus(status) {
            if (status === 'all') return LocalDB.orders.getAll();
            return LocalDB.orders.getAll().filter(o => o.status === status);
        }
    },
    
    // 合作夥伴管理
    partners: {
        getAll() {
            return LocalDB.get('partners', []);
        },
        getById(id) {
            return LocalDB.partners.getAll().find(p => p.id === id);
        },
        getByEmail(email) {
            return LocalDB.partners.getAll().find(p => p.email === email);
        },
        add(partner) {
            const partners = LocalDB.partners.getAll();
            const newPartner = {
                ...partner,
                id: LocalDB.generateId(),
                active: true,
                createdAt: new Date().toISOString()
            };
            partners.push(newPartner);
            LocalDB.set('partners', partners);
            return newPartner.id;
        }
    },
    
    // 促銷活動
    promotions: {
        getAll() {
            return LocalDB.get('promotions', []);
        },
        getActive() {
            const now = new Date();
            return LocalDB.promotions.getAll().filter(p => {
                if (!p.active) return false;
                const start = p.startDate ? new Date(p.startDate) : null;
                const end = p.endDate ? new Date(p.endDate) : null;
                if (start && now < start) return false;
                if (end && now > end) return false;
                return true;
            });
        },
        add(promotion) {
            const promotions = LocalDB.promotions.getAll();
            const newPromo = {
                ...promotion,
                id: LocalDB.generateId(),
                active: true,
                createdAt: new Date().toISOString()
            };
            promotions.push(newPromo);
            LocalDB.set('promotions', promotions);
            return newPromo.id;
        },
        update(id, data) {
            const promotions = LocalDB.promotions.getAll();
            const index = promotions.findIndex(p => p.id === id);
            if (index >= 0) {
                promotions[index] = { ...promotions[index], ...data };
                LocalDB.set('promotions', promotions);
            }
        },
        delete(id) {
            const promotions = LocalDB.promotions.getAll();
            const index = promotions.findIndex(p => p.id === id);
            if (index >= 0) {
                promotions[index].active = false;
                LocalDB.set('promotions', promotions);
            }
        }
    },
    
    // 媒體素材
    media: {
        getAll() {
            return LocalDB.get('media', []);
        },
        add(file) {
            const media = LocalDB.media.getAll();
            const newFile = {
                id: LocalDB.generateId(),
                name: file.name,
                type: file.type,
                size: file.size,
                dataUrl: file.dataUrl,
                createdAt: new Date().toISOString()
            };
            media.push(newFile);
            LocalDB.set('media', media);
            return newFile.id;
        },
        delete(id) {
            const media = LocalDB.media.getAll();
            const filtered = media.filter(m => m.id !== id);
            LocalDB.set('media', filtered);
        }
    },
    
    // 設定
    settings: {
        get() {
            return LocalDB.get('settings', { lineToken: '', split: 0.3 });
        },
        update(data) {
            const settings = LocalDB.settings.get();
            LocalDB.set('settings', { ...settings, ...data });
        }
    },
    
    // 初始化預設資料
    initDefaultData() {
        // 如果沒有商品，建立預設商品
        if (LocalDB.products.getAll().length === 0) {
            const defaultProducts = [
                { name: '人類外泌體面膜', type: 'product', price: 1580, originalPrice: 1980, description: '15分鐘縮時保養，打造無瑕水潤透亮肌。含四胜肽、富勒烯、水膜磁。', imageUrl: 'images/mask.jpg', sortOrder: 1 },
                { name: '人類外泌體精華液', type: 'product', price: 3580, originalPrice: 4280, description: '一瓶重啟青春修復力。多重玻尿酸層層補水，富勒烯強效抗氧化。', imageUrl: 'images/essence.jpg', sortOrder: 2 },
                { name: '人類外泌體安瓶', type: 'product', price: 3980, originalPrice: 4680, description: '瞬效修護，重新定義年輕。多重胜肽煥活，撫平歲月紋理。', imageUrl: 'images/ampoule.jpg', sortOrder: 3 },
                { name: '人類外泌體養髮液', type: 'product', price: 4580, originalPrice: 5280, description: '美髮新境界，從髮根開始。臍帶間質幹細胞外泌體，深入滋養髮根。', imageUrl: 'images/hair.jpg', sortOrder: 4 }
            ];
            defaultProducts.forEach(p => LocalDB.products.add(p));
        }
        
        // 如果沒有促銷，建立預設促銷
        if (LocalDB.promotions.getAll().length === 0) {
            const now = new Date();
            const nextMonth = new Date(now);
            nextMonth.setMonth(nextMonth.getMonth() + 1);
            LocalDB.promotions.add({
                name: '限時 8 折優惠',
                type: 'discount',
                value: 0.8,
                minSpend: 0,
                startDate: now.toISOString(),
                endDate: nextMonth.toISOString(),
                code: ''
            });
        }
    }
};

// ── LINE Notify 通知 ──
const LineNotifier = {
    async notify(message, token = null) {
        const lineToken = token || LocalDB.settings.get().lineToken;
        if (!lineToken) {
            console.log('LINE Token 未設定，跳過通知');
            return false;
        }
        
        try {
            const formData = new FormData();
            formData.append('message', message);
            const response = await fetch('https://notify-api.line.me/api/notify', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${lineToken}` },
                body: formData
            });
            return response.ok;
        } catch (error) {
            console.error('LINE Notify 發送失敗:', error);
            return false;
        }
    },
    
    async newOrderNotify(order) {
        const items = order.items.map(item => 
            `  ${item.name} x${item.qty} = NT$ ${(item.price * item.qty).toLocaleString()}`
        ).join('\n');
        
        const message = `
🛒 新訂單通知
━━━━━━━━━━━━━━
📋 訂單編號：${order.id}
👤 客戶：${order.customer.name}
📱 電話：${order.customer.phone}
📍 地址：${order.customer.address}
━━━━━━━━━━━━━━
📦 商品：
${items}
━━━━━━━━━━━━━━
💰 總金額：NT$ ${order.total.toLocaleString()}
🎁 優惠：${order.discount ? `NT$ ${order.discount}` : '無'}
💳 實付：NT$ ${order.finalTotal.toLocaleString()}
━━━━━━━━━━━━━━
⏰ 下單時間：${new Date().toLocaleString('zh-TW')}
        `.trim();
        
        return this.notify(message);
    }
};

// 匯出
window.LocalDB = LocalDB;
window.LineNotifier = LineNotifier;
