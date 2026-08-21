// Supabase Client 配置
// 替换为你自己的 anon key
const SUPABASE_URL = 'https://mqvygeoqjfylgdmklvrb.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xdnlnZW9xamZ5bGdkbWtsdnJiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODcxNzYyNjcsImV4cCI6MjEwMjc1MjI2N30.cpKcwOSKzwz50eIcz-WIq6cmbXuQeNt3Q0Ao0CEJBPg';

// DeepSeek API 配置
const DEEPSEEK_API_KEY = 'YOUR_DEEPSEEK_API_KEY_HERE';
const DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions';

// ============================================================
// Supabase 客户端初始化
// ============================================================
let supabase = null;
try {
  supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} catch(e) {
  console.warn('Supabase 未初始化，请检查 anon key');
}

// ============================================================
// 订阅计划配置
// ============================================================
const PLANS = {
  free: {
    name: '免费版',
    nameCn: '免费版',
    price: 0,
    dailyLimit: 2,
    features: ['每日2次生成', '基础5种题材', '强制热门风格', '禁止自定义人物'],
    color: '#94a3b8',
    badge: 'FREE'
  },
  premium: {
    name: 'premium',
    nameCn: '专业版',
    price: 39,
    period: '每月',
    dailyLimit: 999,
    features: ['无限次生成', '5种题材模板', '4种节奏风格', '自定义人物设定', '完整剧本输出'],
    color: '#4f46e5',
    badge: 'PRO'
  }
};

// ============================================================
// 题材模板（来自 prompts.js）
// ============================================================
const GENRES = [
  { id: 'niixi', name: '都市逆袭', desc: '草根逆袭 · 打脸装逼', icon: '🔥' },
  { id: 'yanqing', name: '甜宠言情', desc: '霸道总裁 · 高糖预警', icon: '💕' },
  { id: 'xuanyi', name: '悬疑惊悚', desc: '反转烧脑 · 惊悚刺激', icon: '😱' },
  { id: 'chuanyue', name: '穿越重生', desc: '今穿古/重生复仇', icon: '⚡' },
  { id: 'tianchong', name: '先婚后爱', desc: '契约婚姻 · 甜宠高糖', icon: '💍' }
];

const RHYTHMS = [
  { id: 'hot', name: '🔥 爆款节奏', desc: '参考当下最火短剧，每15秒一个情绪引爆点' },
  { id: 'short', name: '⚡ 快节奏', desc: '精简版，极速切换，平均8-10秒一场景' },
  { id: 'long', name: '🎬 深度剧情', desc: '丰富对白+人物关系铺垫，单集1200-1500字' }
];

// ============================================================
// DeepSeek API 调用
// ============================================================
async function generateScript(genre, plot, rhythm, characters, extra) {
  const genreTpl = GENRES.find(g => g.id === genre);
  const rhythmTpl = RHYTHMS.find(r => r.id === rhythm);

  const systemPrompt = `你是一位专业的AI短剧编剧，精通竖屏短剧的创作规律。你的任务是根据用户提供的题材要求，生成一部适合拍摄的竖屏短剧脚本。

## 短剧黄金法则
1. 竖屏思维：画面以人物半身/特写为主
2. 节奏：每15-20秒一个情绪点
3. 对白：一句台词不超过20字
4. 爽点密集：打脸、反转、告白交替
5. 结尾钩子：每集最后必须留悬念

## 输出格式（严格按此格式）
【剧名】
【类型】${genreTpl ? genreTpl.name : ''}
【集数】第1集（约3分钟，800-1000字）
【人物表】列出主要角色
【剧情概要】本集100字梗概

【分镜表】
| 镜头 | 景别 | 时长 | 画面 | 台词 | 音效 |

【完整剧本】
场景/人物/对白/动作

【下集钩子】`;

  const rhythmMap = {
    hot: '参考热门短剧爆款公式，开头5秒必须有高能钩子，每15秒一个情绪引爆点',
    short: '精简版，每句台词不超过15字，节奏极快，平均8-10秒切换一个场景',
    long: '深度剧情版，可铺垫更长人物关系，对白更丰富，单集1200-1500字'
  };

  const userPrompt = `## 题材\n${genreTpl ? genreTpl.name + '：' + genreTpl.desc : ''}\n\n## 核心梗概\n${plot}\n\n## 节奏风格\n${rhythmMap[rhythm] || rhythmMap.hot}\n\n${characters ? '## 人物设定\n' + characters : ''}\n\n${extra ? '## 特殊要求\n' + extra : ''}`;

  const response = await fetch(DEEPSEEK_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + DEEPSEEK_API_KEY
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.8,
      max_tokens: 2000
    })
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error('DeepSeek API 错误: ' + response.status);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

// ============================================================
// Supabase 认证
// ============================================================
async function signUp(email, password, nickname) {
  if (!supabase) throw new Error('Supabase 未配置');
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { nickname } }
  });
  if (error) throw error;
  return data;
}

async function signIn(email, password) {
  if (!supabase) throw new Error('Supabase 未配置');
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

async function signOut() {
  if (!supabase) throw new Error('Supabase 未配置');
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}

async function getSession() {
  if (!supabase) return null;
  const { data } = await supabase.auth.getSession();
  return data.session;
}

async function onAuthStateChange(callback) {
  if (!supabase) return () => {};
  return supabase.auth.onAuthStateChange((event, session) => callback(event, session));
}

// ============================================================
// 用户数据
// ============================================================
async function getProfile(userId) {
  if (!supabase || !userId) return null;
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();
  if (error && error.code !== 'PGRST116') throw error;
  return data;
}

async function updateProfile(userId, updates) {
  if (!supabase || !userId) throw new Error('未登录');
  const { data, error } = await supabase
    .from('profiles')
    .update({ ...updates, updated_at: new Date().toISOString() })
    .eq('id', userId)
    .select()
    .single();
  if (error) throw error;
  return data;
}

async function logUsage(userId, genre, plot) {
  if (!supabase || !userId) return;
  await supabase.from('usage_logs').insert({ user_id: userId, genre, plot });
}

async function checkAndIncrementUsage(userId) {
  if (!supabase || !userId) return { allowed: true, remaining: 999 };

  const profile = await getProfile(userId);
  if (!profile) return { allowed: true, remaining: 999 };

  const plan = profile.plan || 'free';
  const cfg = PLANS[plan] || PLANS.free;
  const today = new Date().toISOString().split('T')[0];

  // 重置每日计数
  if (profile.last_used_date !== today) {
    await supabase.from('profiles')
      .update({ daily_uses: 0, last_used_date: today })
      .eq('id', userId);
    return { allowed: true, remaining: cfg.dailyLimit - 1, plan };
  }

  const remaining = Math.max(0, cfg.dailyLimit - profile.daily_uses);
  if (remaining <= 0) {
    return { allowed: false, remaining: 0, plan };
  }

  // 计数+1
  await supabase.from('profiles')
    .update({ daily_uses: profile.daily_uses + 1 })
    .eq('id', userId);

  return { allowed: true, remaining: remaining - 1, plan };
}

// ============================================================
// 支付（简化版：跳转支付宝）
// ============================================================
function goToPayment(plan) {
  const outTradeNo = 'JGC_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  const amount = PLANS[plan].price;

  // 将交易号存入 localStorage，等支付回调后更新
  localStorage.setItem('pending_payment', JSON.stringify({
    out_trade_no: outTradeNo,
    plan: plan,
    amount: amount,
    user_id: (supabase?.auth?.getSession() || { data: { session: null } })?.data?.session?.user?.id || ''
  }));

  // 跳转到支付页面（需要后端生成支付宝链接）
  // 目前先用 alert，后续接入后端后完善
  alert(`即将跳转支付页面...\n\n商品：${PLANS[plan].nameCn}\n金额：¥${amount}/月\n订单号：${outTradeNo}\n\n（支付系统接入中，请稍候）`);

  // TODO: 后续接入 Supabase Edge Functions + Alipay
  // window.location.href = `/pay.html?plan=${plan}&trade_no=${outTradeNo}`;
}

// ============================================================
// 导出（供 index.html 调用）
// ============================================================
window.App = {
  supabase,
  PLANS,
  GENRES,
  RHYTHMS,
  signUp,
  signIn,
  signOut,
  getSession,
  onAuthStateChange,
  getProfile,
  updateProfile,
  checkAndIncrementUsage,
  logUsage,
  generateScript,
  goToPayment
};
