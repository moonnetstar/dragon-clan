// Firebase 初始化與資料庫操作模組
// 使用 Firebase v9+ Modular SDK

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js';
import { 
    getFirestore, collection, doc, getDocs, getDoc, 
    setDoc, updateDoc, deleteDoc, addDoc, 
    query, where, orderBy, onSnapshot, serverTimestamp 
} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js';
import { 
    getStorage, ref, uploadBytes, getDownloadURL, deleteObject, listAll 
} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-storage.js';
import { 
    getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword,
    signOut, onAuthStateChanged 
} from 'https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js';

// ── Firebase 配置 ──
// ⚠️ 請替換為您的 Firebase 專案配置
const firebaseConfig = {
    apiKey: "AIzaSyCH-Hu28_Oz6i8MSraiD1l29Qn12U04RrI",
    authDomain: "exomuse-shop.firebaseapp.com",
    projectId: "exomuse-shop",
    storageBucket: "exomuse-shop.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// 初始化
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);
const auth = getAuth(app);

// ── 資料庫操作類別 ──
class ExomeDB {
    
    // ═══════════════════════════════════════
    // 商品管理
    // ═══════════════════════════════════════
    
    // 取得所有上架商品
    static async getProducts() {
        const q = query(collection(db, 'products'), where('active', '==', true), orderBy('sortOrder', 'asc'));
        const snapshot = await getDocs(q);
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    }
    
    // 取得單一商品
    static async getProduct(id) {
        const docRef = doc(db, 'products', id);
        const snapshot = await getDoc(docRef);
        return snapshot.exists() ? { id: snapshot.id, ...snapshot.data() } : null;
    }
    
    // 新增商品
    static async addProduct(product) {
        const docRef = await addDoc(collection(db, 'products'), {
            ...product,
            active: true,
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp()
        });
        return docRef.id;
    }
    
    // 更新商品
    static async updateProduct(id, data) {
        const docRef = doc(db, 'products', id);
        await updateDoc(docRef, { ...data, updatedAt: serverTimestamp() });
    }
    
    // 刪除商品（軟刪除）
    static async deleteProduct(id) {
        const docRef = doc(db, 'products', id);
        await updateDoc(docRef, { active: false, deletedAt: serverTimestamp() });
    }
    
    // 監聽商品變化（即時更新）
    static onProductsChange(callback) {
        const q = query(collection(db, 'products'), where('active', '==', true), orderBy('sortOrder', 'asc'));
        return onSnapshot(q, (snapshot) => {
            const products = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
            callback(products);
        });
    }
    
    // ═══════════════════════════════════════
    // 訂單管理
    // ═══════════════════════════════════════
    
    // 建立訂單
    static async createOrder(order) {
        const docRef = await addDoc(collection(db, 'orders'), {
            ...order,
            status: 'pending',  // pending → confirmed → shipped → completed
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp()
        });
        return docRef.id;
    }
    
    // 取得合作方的所有訂單
    static async getPartnerOrders(partnerId) {
        const q = query(
            collection(db, 'orders'), 
            where('partnerId', '==', partnerId), 
            orderBy('createdAt', 'desc')
        );
        const snapshot = await getDocs(q);
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    }
    
    // 更新訂單狀態
    static async updateOrderStatus(orderId, status, note = '') {
        const docRef = doc(db, 'orders', orderId);
        await updateDoc(docRef, { 
            status, 
            statusNote: note,
            updatedAt: serverTimestamp() 
        });
    }
    
    // 監聽新訂單（即時通知）
    static onNewOrders(partnerId, callback) {
        const q = query(
            collection(db, 'orders'),
            where('partnerId', '==', partnerId),
            where('status', '==', 'pending'),
            orderBy('createdAt', 'desc')
        );
        return onSnapshot(q, (snapshot) => {
            const orders = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
            callback(orders);
        });
    }
    
    // ═══════════════════════════════════════
    // 媒體素材管理
    // ═══════════════════════════════════════
    
    // 上傳圖片
    static async uploadImage(file, path = 'products') {
        const storageRef = ref(storage, `${path}/${Date.now()}_${file.name}`);
        const snapshot = await uploadBytes(storageRef, file);
        const url = await getDownloadURL(snapshot.ref);
        return { url, path: snapshot.ref.fullPath };
    }
    
    // 上傳影片
    static async uploadVideo(file, path = 'videos') {
        const storageRef = ref(storage, `${path}/${Date.now()}_${file.name}`);
        const snapshot = await uploadBytes(storageRef, file);
        const url = await getDownloadURL(snapshot.ref);
        return { url, path: snapshot.ref.fullPath };
    }
    
    // 刪除檔案
    static async deleteFile(path) {
        const storageRef = ref(storage, path);
        await deleteObject(storageRef);
    }
    
    // 取得資料夾內所有檔案
    static async listFiles(path) {
        const storageRef = ref(storage, path);
        const result = await listAll(storageRef);
        const files = await Promise.all(
            result.items.map(async (item) => ({
                name: item.name,
                path: item.fullPath,
                url: await getDownloadURL(item)
            }))
        );
        return files;
    }
    
    // ═══════════════════════════════════════
    // 促銷活動管理
    // ═══════════════════════════════════════
    
    // 取得目前有效的促銷
    static async getActivePromotions() {
        const now = new Date();
        const q = query(
            collection(db, 'promotions'),
            where('active', '==', true),
            where('startDate', '<=', now),
            where('endDate', '>=', now)
        );
        const snapshot = await getDocs(q);
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    }
    
    // 新增促銷
    static async addPromotion(promotion) {
        const docRef = await addDoc(collection(db, 'promotions'), {
            ...promotion,
            active: true,
            createdAt: serverTimestamp()
        });
        return docRef.id;
    }
    
    // 更新促銷
    static async updatePromotion(id, data) {
        const docRef = doc(db, 'promotions', id);
        await updateDoc(docRef, { ...data, updatedAt: serverTimestamp() });
    }
    
    // 刪除促銷
    static async deletePromotion(id) {
        const docRef = doc(db, 'promotions', id);
        await updateDoc(docRef, { active: false });
    }
    
    // ═══════════════════════════════════════
    // 合作夥伴管理
    // ═══════════════════════════════════════
    
    // 註冊合作夥伴
    static async registerPartner(email, password, info) {
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        await setDoc(doc(db, 'partners', cred.user.uid), {
            ...info,
            email,
            role: 'partner',
            active: true,
            createdAt: serverTimestamp()
        });
        return cred.user.uid;
    }
    
    // 合作夥伴登入
    static async loginPartner(email, password) {
        const cred = await signInWithEmailAndPassword(auth, email, password);
        return cred.user;
    }
    
    // 登出
    static async logout() {
        await signOut(auth);
    }
    
    // 取得合作夥伴資料
    static async getPartner(id) {
        const docRef = doc(db, 'partners', id);
        const snapshot = await getDoc(docRef);
        return snapshot.exists() ? { id: snapshot.id, ...snapshot.data() } : null;
    }
    
    // 監聽登入狀態
    static onAuthChange(callback) {
        return onAuthStateChanged(auth, callback);
    }
}

// ── LINE Notify 通知 ──
class LineNotifier {
    static async notify(message, token = null) {
        const lineToken = token || 'e66f82f67e651339a25f7d07fe441a9e';
        const formData = new FormData();
        formData.append('message', message);
        
        try {
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
    }
    
    // 新訂單通知
    static async newOrderNotify(order, partnerName = '合作夥伴') {
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
    
    // 訂單狀態更新通知
    static async orderStatusNotify(orderId, status, customerName) {
        const statusText = {
            confirmed: '✅ 訂單已確認',
            shipped: '🚚 已出貨',
            completed: '🎉 訂單已完成',
            cancelled: '❌ 訂單已取消'
        };
        
        const message = `
${statusText[status] || status}
━━━━━━━━━━━━━━
📋 訂單編號：${orderId}
👤 客戶：${customerName}
⏰ 更新時間：${new Date().toLocaleString('zh-TW')}
        `.trim();
        
        return this.notify(message);
    }
}

// 匯出
window.ExomeDB = ExomeDB;
window.LineNotifier = LineNotifier;
