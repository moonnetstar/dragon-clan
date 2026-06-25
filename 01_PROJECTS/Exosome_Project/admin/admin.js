// ExoMuse 合作夥伴後台 — 主要邏輯

// ── 全域變數 ──
let currentUser = null;
let partnerData = null;
let products = [];
let orders = [];
let promotions = [];
let lineToken = '';

// ── Toast 通知 ──
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ── 頁面切換 ──
function showSection(name) {
    document.querySelectorAll('[id^="sec-"]').forEach(el => el.classList.add('hidden'));
    document.getElementById(`sec-${name}`).classList.remove('hidden');
    document.querySelectorAll('.sidebar-link').forEach(el => {
        el.classList.toggle('active', el.dataset.section === name);
    });
    // Close mobile sidebar
    document.getElementById('sidebar').classList.add('hidden');
}

// ── 認證 ──
function showLogin() {
    document.getElementById('loginScreen').classList.remove('hidden');
    document.getElementById('registerScreen').classList.add('hidden');
}

function showRegister() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('registerScreen').classList.remove('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    try {
        await ExomeDB.loginPartner(email, password);
        showToast('登入成功！');
    } catch (err) {
        showToast('登入失敗：' + err.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const name = document.getElementById('regName').value;
    const phone = document.getElementById('regPhone').value;
    const split = parseFloat(document.getElementById('regSplit').value);
    const token = document.getElementById('regLineToken').value;
    
    try {
        const uid = await ExomeDB.registerPartner(email, password, {
            name, phone, split, lineToken: token
        });
        showToast('註冊成功！請登入。');
        showLogin();
    } catch (err) {
        showToast('註冊失敗：' + err.message, 'error');
    }
}

async function handleLogout() {
    await ExomeDB.logout();
    location.reload();
}

// ── 初始化 ──
ExomeDB.onAuthChange(async (user) => {
    if (!user) {
        document.getElementById('loginScreen').classList.remove('hidden');
        document.getElementById('dashboard').classList.add('hidden');
        return;
    }
    
    currentUser = user;
    partnerData = await ExomeDB.getPartner(user.uid);
    
    if (!partnerData) {
        showToast('找不到合作夥伴資料', 'error');
        return;
    }
    
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('registerScreen').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('partnerName').textContent = partnerData.name;
    document.getElementById('partnerInitial').textContent = partnerData.name.charAt(0);
    document.getElementById('currentSplit').textContent = Math.round(partnerData.split * 100) + '%';
    
    lineToken = partnerData.lineToken || '';
    if (lineToken) document.getElementById('lineTokenInput').value = lineToken;
    
    loadProducts();
    loadOrders();
    loadPromotions();
    loadMedia();
    
    // 監聽新訂單
    ExomeDB.onNewOrders(user.uid, (newOrders) => {
        const badge = document.getElementById('pendingOrdersBadge');
        badge.textContent = newOrders.length;
        badge.classList.toggle('hidden', newOrders.length === 0);
        document.getElementById('notifBadge').textContent = newOrders.length;
        document.getElementById('notifBadge').classList.toggle('hidden', newOrders.length === 0);
    });
});

// ═══════════════════════════════════════
// 商品管理
// ═══════════════════════════════════════

function loadProducts() {
    ExomeDB.onProductsChange((data) => {
        products = data;
        renderProducts();
    });
}

function renderProducts() {
    const container = document.getElementById('productList');
    if (!products.length) {
        container.innerHTML = '<div class="text-center py-16 text-warm-gray">尚無商品，點擊「新增商品」開始</div>';
        return;
    }
    
    container.innerHTML = products.map(p => `
        <div class="bg-white rounded-xl p-4 flex items-center gap-4 fade-in">
            <div class="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 bg-gray-100">
                ${p.imageUrl ? `<img src="${p.imageUrl}" class="w-full h-full object-cover">` : '<div class="w-full h-full flex items-center justify-center text-gray-300 text-xs">無圖</div>'}
            </div>
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-medium truncate">${p.name}</h4>
                    <span class="px-2 py-0.5 rounded-full text-[10px] ${p.type === 'video' ? 'bg-purple-100 text-purple-700' : p.type === 'promo' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'}">
                        ${p.type === 'video' ? '影片' : p.type === 'promo' ? '促銷' : '商品'}
                    </span>
                    ${!p.active ? '<span class="px-2 py-0.5 rounded-full text-[10px] bg-red-100 text-red-600">已下架</span>' : ''}
                </div>
                <p class="text-sm text-gold font-bold">NT$ ${p.price?.toLocaleString() || 0}</p>
                ${p.originalPrice ? `<p class="text-xs text-warm-gray line-through">NT$ ${p.originalPrice.toLocaleString()}</p>` : ''}
            </div>
            <div class="flex gap-2">
                <button onclick="editProduct('${p.id}')" class="btn-outline px-4 py-2 rounded-lg text-xs">編輯</button>
                <button onclick="deleteProduct('${p.id}')" class="btn-danger px-4 py-2 rounded-lg text-xs">刪除</button>
            </div>
        </div>
    `).join('');
}

function openProductModal(id = null) {
    document.getElementById('productModal').classList.remove('hidden');
    document.getElementById('productModalTitle').textContent = id ? '編輯商品' : '新增商品';
    document.getElementById('productForm').reset();
    document.getElementById('editProductId').value = id || '';
    document.getElementById('prodImagePreview').classList.add('hidden');
    
    if (id) {
        const p = products.find(x => x.id === id);
        if (p) {
            document.getElementById('prodName').value = p.name || '';
            document.getElementById('prodType').value = p.type || 'product';
            document.getElementById('prodPrice').value = p.price || '';
            document.getElementById('prodOriginalPrice').value = p.originalPrice || '';
            document.getElementById('prodDesc').value = p.description || '';
            document.getElementById('prodSort').value = p.sortOrder || 0;
            document.getElementById('prodActive').checked = p.active !== false;
            if (p.imageUrl) {
                document.getElementById('prodImagePreview').classList.remove('hidden');
                document.getElementById('prodImagePreview img').src = p.imageUrl;
            }
        }
    }
}

function closeProductModal() {
    document.getElementById('productModal').classList.add('hidden');
}

function previewProductImage(e) {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        document.getElementById('prodImagePreview').classList.remove('hidden');
        document.getElementById('prodImagePreview img').src = url;
    }
}

async function saveProduct(e) {
    e.preventDefault();
    const id = document.getElementById('editProductId').value;
    const imageFile = document.getElementById('prodImageInput').files[0];
    const videoFile = document.getElementById('prodVideoInput').files[0];
    
    const data = {
        name: document.getElementById('prodName').value,
        type: document.getElementById('prodType').value,
        price: parseInt(document.getElementById('prodPrice').value) || 0,
        originalPrice: parseInt(document.getElementById('prodOriginalPrice').value) || null,
        description: document.getElementById('prodDesc').value,
        sortOrder: parseInt(document.getElementById('prodSort').value) || 0,
        active: document.getElementById('prodActive').checked,
        partnerId: currentUser.uid
    };
    
    try {
        // 上傳圖片
        if (imageFile) {
            const result = await ExomeDB.uploadImage(imageFile, `products/${currentUser.uid}`);
            data.imageUrl = result.url;
            data.imagePath = result.path;
        }
        
        // 上傳影片
        if (videoFile) {
            const result = await ExomeDB.uploadVideo(videoFile, `videos/${currentUser.uid}`);
            data.videoUrl = result.url;
            data.videoPath = result.path;
        }
        
        if (id) {
            await ExomeDB.updateProduct(id, data);
            showToast('商品已更新');
        } else {
            await ExomeDB.addProduct(data);
            showToast('商品已新增');
        }
        closeProductModal();
    } catch (err) {
        showToast('儲存失敗：' + err.message, 'error');
    }
}

function editProduct(id) {
    openProductModal(id);
}

async function deleteProduct(id) {
    if (!confirm('確定要刪除這個商品嗎？')) return;
    try {
        await ExomeDB.deleteProduct(id);
        showToast('商品已刪除');
    } catch (err) {
        showToast('刪除失敗：' + err.message, 'error');
    }
}

// ═══════════════════════════════════════
// 訂單管理
// ═══════════════════════════════════════

function loadOrders() {
    ExomeDB.getPartnerOrders(currentUser.uid).then(data => {
        orders = data;
        renderOrders();
    });
}

function renderOrders(filter = 'all') {
    const container = document.getElementById('orderList');
    const filtered = filter === 'all' ? orders : orders.filter(o => o.status === filter);
    
    if (!filtered.length) {
        container.innerHTML = '<div class="text-center py-16 text-warm-gray">尚無訂單</div>';
        return;
    }
    
    container.innerHTML = filtered.map(o => `
        <div class="bg-white rounded-xl p-5 fade-in cursor-pointer hover:shadow-md transition-shadow" onclick="viewOrder('${o.id}')">
            <div class="flex items-center justify-between mb-3">
                <div>
                    <span class="text-xs text-warm-gray">訂單編號</span>
                    <p class="font-mono text-sm font-medium">${o.id.slice(0, 12)}...</p>
                </div>
                <span class="px-3 py-1 rounded-full text-xs font-medium status-${o.status}">
                    ${getStatusText(o.status)}
                </span>
            </div>
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm font-medium">${o.customer?.name || '未知'}</p>
                    <p class="text-xs text-warm-gray">${o.items?.length || 0} 件商品</p>
                </div>
                <p class="font-serif text-lg font-bold text-gold">NT$ ${o.finalTotal?.toLocaleString() || 0}</p>
            </div>
        </div>
    `).join('');
}

function getStatusText(status) {
    const map = { pending: '待處理', confirmed: '已確認', shipped: '已出貨', completed: '已完成', cancelled: '已取消' };
    return map[status] || status;
}

function filterOrders() {
    renderOrders(document.getElementById('orderFilter').value);
}

function viewOrder(id) {
    const order = orders.find(o => o.id === id);
    if (!order) return;
    
    document.getElementById('orderModal').classList.remove('hidden');
    document.getElementById('orderDetail').innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <span class="text-xs text-warm-gray">訂單編號</span>
                <span class="font-mono text-sm">${order.id}</span>
            </div>
            <div class="flex items-center justify-between">
                <span class="text-xs text-warm-gray">狀態</span>
                <span class="px-3 py-1 rounded-full text-xs font-medium status-${order.status}">${getStatusText(order.status)}</span>
            </div>
            <hr>
            <div>
                <p class="text-xs text-warm-gray mb-1">客戶資料</p>
                <p class="text-sm"><strong>${order.customer?.name}</strong></p>
                <p class="text-sm text-warm-gray">${order.customer?.phone}</p>
                <p class="text-sm text-warm-gray">${order.customer?.address}</p>
            </div>
            <hr>
            <div>
                <p class="text-xs text-warm-gray mb-2">商品明細</p>
                ${(order.items || []).map(item => `
                    <div class="flex justify-between text-sm py-1">
                        <span>${item.name} x${item.qty}</span>
                        <span>NT$ ${(item.price * item.qty).toLocaleString()}</span>
                    </div>
                `).join('')}
            </div>
            <hr>
            <div class="flex justify-between">
                <span class="text-sm">總金額</span>
                <span class="font-serif text-lg font-bold text-gold">NT$ ${order.finalTotal?.toLocaleString()}</span>
            </div>
            <hr>
            <div class="flex gap-2">
                ${order.status === 'pending' ? `
                    <button onclick="updateOrderStatus('${order.id}', 'confirmed')" class="btn-gold flex-1 py-2.5 rounded-xl text-sm">確認訂單</button>
                    <button onclick="updateOrderStatus('${order.id}', 'cancelled')" class="btn-danger flex-1 py-2.5 rounded-xl text-sm">取消訂單</button>
                ` : ''}
                ${order.status === 'confirmed' ? `
                    <button onclick="updateOrderStatus('${order.id}', 'shipped')" class="btn-gold flex-1 py-2.5 rounded-xl text-sm">標記已出貨</button>
                ` : ''}
                ${order.status === 'shipped' ? `
                    <button onclick="updateOrderStatus('${order.id}', 'completed')" class="btn-gold flex-1 py-2.5 rounded-xl text-sm">標記已完成</button>
                ` : ''}
            </div>
        </div>
    `;
}

function closeOrderModal() {
    document.getElementById('orderModal').classList.add('hidden');
}

async function updateOrderStatus(orderId, status) {
    try {
        await ExomeDB.updateOrderStatus(orderId, status);
        showToast('訂單狀態已更新');
        closeOrderModal();
        loadOrders();
    } catch (err) {
        showToast('更新失敗：' + err.message, 'error');
    }
}

// ═══════════════════════════════════════
// 促銷活動
// ═══════════════════════════════════════

function loadPromotions() {
    ExomeDB.getActivePromotions().then(data => {
        promotions = data;
        renderPromotions();
    });
}

function renderPromotions() {
    const container = document.getElementById('promoList');
    if (!promotions.length) {
        container.innerHTML = '<div class="text-center py-16 text-warm-gray">尚無促銷活動</div>';
        return;
    }
    
    container.innerHTML = promotions.map(p => `
        <div class="bg-white rounded-xl p-5 fade-in">
            <div class="flex items-center justify-between mb-3">
                <h4 class="font-medium">${p.name}</h4>
                <span class="px-3 py-1 rounded-full text-xs bg-green-100 text-green-700">進行中</span>
            </div>
            <div class="text-sm text-warm-gray space-y-1">
                <p>類型：${getPromoTypeText(p.type)}</p>
                <p>折扣：${p.value}${p.type === 'discount' ? '折' : p.type === 'amount' ? '元' : ''}</p>
                <p>期間：${formatDate(p.startDate)} ~ ${formatDate(p.endDate)}</p>
                ${p.code ? `<p>折扣碼：<span class="font-mono text-gold">${p.code}</span></p>` : ''}
            </div>
            <div class="flex gap-2 mt-4">
                <button onclick="deletePromotion('${p.id}')" class="btn-danger px-4 py-2 rounded-lg text-xs">刪除</button>
            </div>
        </div>
    `).join('');
}

function getPromoTypeText(type) {
    const map = { discount: '折扣', amount: '金額折抵', bogo: '買一送一', gift: '滿額贈品' };
    return map[type] || type;
}

function formatDate(date) {
    if (!date) return '';
    const d = date.toDate ? date.toDate() : new Date(date);
    return d.toLocaleDateString('zh-TW');
}

function openPromoModal() {
    document.getElementById('promoModal').classList.remove('hidden');
    document.getElementById('promoForm').reset();
}

function closePromoModal() {
    document.getElementById('promoModal').classList.add('hidden');
}

async function savePromo(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('promoName').value,
        type: document.getElementById('promoType').value,
        value: parseFloat(document.getElementById('promoValue').value),
        minSpend: parseInt(document.getElementById('promoMinSpend').value) || 0,
        startDate: new Date(document.getElementById('promoStart').value),
        endDate: new Date(document.getElementById('promoEnd').value),
        code: document.getElementById('promoCode').value || null
    };
    
    try {
        await ExomeDB.addPromotion(data);
        showToast('促銷活動已新增');
        closePromoModal();
        loadPromotions();
    } catch (err) {
        showToast('新增失敗：' + err.message, 'error');
    }
}

async function deletePromotion(id) {
    if (!confirm('確定要刪除這個促銷活動嗎？')) return;
    try {
        await ExomeDB.deletePromotion(id);
        showToast('促銷活動已刪除');
        loadPromotions();
    } catch (err) {
        showToast('刪除失敗：' + err.message, 'error');
    }
}

// ═══════════════════════════════════════
// 媒體素材
// ═══════════════════════════════════════

async function loadMedia() {
    try {
        const files = await ExomeDB.listFiles(`media/${currentUser.uid}`);
        renderMedia(files);
    } catch (err) {
        // 資料夾可能不存在，忽略
    }
}

function renderMedia(files) {
    const container = document.getElementById('mediaGrid');
    if (!files.length) {
        container.innerHTML = '<div class="text-center py-16 text-warm-gray col-span-full">尚無素材，點擊上方上傳</div>';
        return;
    }
    
    container.innerHTML = files.map(f => `
        <div class="relative group rounded-xl overflow-hidden bg-gray-100 aspect-square">
            ${f.name.match(/\.(mp4|mov|avi)$/i) 
                ? `<div class="w-full h-full flex items-center justify-center text-4xl">🎬</div>`
                : `<img src="${f.url}" class="w-full h-full object-cover">`
            }
            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <button onclick="copyMediaUrl('${f.url}')" class="px-3 py-1.5 rounded-lg bg-white text-xs">複製連結</button>
                <button onclick="deleteMedia('${f.path}')" class="px-3 py-1.5 rounded-lg bg-red-500 text-white text-xs">刪除</button>
            </div>
        </div>
    `).join('');
}

async function handleMediaUpload(e) {
    const files = Array.from(e.target.files);
    for (const file of files) {
        try {
            const isVideo = file.type.startsWith('video/');
            const result = isVideo 
                ? await ExomeDB.uploadVideo(file, `media/${currentUser.uid}`)
                : await ExomeDB.uploadImage(file, `media/${currentUser.uid}`);
            showToast(`${file.name} 上傳成功`);
        } catch (err) {
            showToast(`${file.name} 上傳失敗`, 'error');
        }
    }
    loadMedia();
}

function copyMediaUrl(url) {
    navigator.clipboard.writeText(url);
    showToast('連結已複製');
}

async function deleteMedia(path) {
    if (!confirm('確定要刪除這個檔案嗎？')) return;
    try {
        await ExomeDB.deleteFile(path);
        showToast('檔案已刪除');
        loadMedia();
    } catch (err) {
        showToast('刪除失敗', 'error');
    }
}

// ═══════════════════════════════════════
// 設定
// ═══════════════════════════════════════

async function saveLineToken() {
    const token = document.getElementById('lineTokenInput').value.trim();
    if (!token) {
        showToast('請輸入 Token', 'error');
        return;
    }
    try {
        await ExomeDB.updatePartner(currentUser.uid, { lineToken: token });
        lineToken = token;
        showToast('LINE Token 已儲存');
    } catch (err) {
        showToast('儲存失敗', 'error');
    }
}

async function testLineNotify() {
    if (!lineToken) {
        showToast('請先設定 LINE Token', 'error');
        return;
    }
    const ok = await LineNotifier.notify('🔔 ExoMuse 後台測試通知\n\n您的 LINE Notify 設定成功！未來新訂單會自動通知您。', lineToken);
    showToast(ok ? '測試通知已發送' : '發送失敗，請確認 Token 是否正確', ok ? 'success' : 'error');
}

// ═══════════════════════════════════════
// 廣告文案產生器
// ═══════════════════════════════════════

const adProducts = {
    mask:    { name: '人類外泌體面膜',   price: 1580, originalPrice: 1980 },
    essence: { name: '人類外泌體精華液', price: 3580, originalPrice: 4280 },
    ampoule: { name: '人類外泌體安瓶',   price: 3980, originalPrice: 4680 },
    hair:    { name: '人類外泌體養髮液', price: 4580, originalPrice: 5280 },
    promo:   { name: '節日促銷包',       price: 9980, originalPrice: 12800 }
};

let adStyle = 'luxury';

function setAdStyle(style) {
    adStyle = style;
    document.querySelectorAll('.ad-style-btn').forEach(btn => {
        if (btn.dataset.style === style) {
            btn.classList.add('active', 'border-gold/30', 'bg-gold/5', 'text-gold');
            btn.classList.remove('border-gray-200', 'text-warm-gray');
        } else {
            btn.classList.remove('active', 'border-gold/30', 'bg-gold/5', 'text-gold');
            btn.classList.add('border-gray-200', 'text-warm-gray');
        }
    });
    generateAdCopy();
}

function generateAdCopy() {
    const productId = document.getElementById('adProduct').value;
    const audience = document.getElementById('adAudience').value;
    const p = adProducts[productId];
    if (!p) return;

    const styleMap = {
        luxury: {
            title: `✨ ${p.name} — 極致奢華肌膚體驗`,
            body: `【${p.name}】${audience}的首選。\n\n採用人類來源外泌體，深層修護肌底。\n\n🌟 人類來源外泌體 × 富勒烯強效抗氧化\n🌟 臺灣唯一合法認證\n\n💝 限時優惠 NT$ ${p.price.toLocaleString()}（原价 NT$ ${p.originalPrice?.toLocaleString() || p.price.toLocaleString()}）\n\n立即體驗 →`,
            hashtags: '#ExoMuse #外泌體 #人類來源 #奢華保養 #護膚新革命 #ISEV認證'
        },
        urgency: {
            title: `🔥 最後機會！${p.name} 限時特惠`,
            body: `⚡ ${audience} 注意！\n\n${p.name} 限時優惠中！\n\n💰 特惠價：NT$ ${p.price.toLocaleString()}（省 NT$ ${(p.originalPrice - p.price).toLocaleString()}！）\n📦 買3件再享8折\n\n數量有限，售完即止！`,
            hashtags: '#ExoMuse #限時優惠 #外泌體保養 #最後機會 #買3件8折'
        },
        educate: {
            title: `📚 為什麼${audience}都在討論${p.name}？`,
            body: `【外泌體科學小教室】\n\n你知道什麼是「人類來源外泌體」嗎？\n\n${p.name}採用：\n✅ 人類臍帶間質幹細胞外泌體\n✅ 多重玻尿酸深層補水\n✅ 富勒烯強效抗氧化\n✅ 多重胜肽煥活\n\n符合 ISEV 國際標準，臺灣唯一合法。\n\n特惠價 NT$ ${p.price.toLocaleString()}`,
            hashtags: '#外泌體知識 #ExoMuse #科學護膚 #人類來源 #ISEV #保養新知'
        }
    };

    const copy = styleMap[adStyle];
    document.getElementById('adCopy').textContent = copy.body;
    document.getElementById('adTitle').textContent = copy.title;
    document.getElementById('adHashtags').textContent = copy.hashtags;
}

// ── 側邊欄 ──
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('hidden');
}

function toggleNotif() {
    showSection('orders');
}
