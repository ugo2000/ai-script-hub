// 剧工厂 · 支付宝当面付 Worker（Cloudflare）
// 作用：前端扫码 → Worker 调支付宝生成订单二维码 → 用户付款 → 支付宝异步回调本 Worker → 验签 → 自动把 Supabase 会员升级为 premium
//
// 部署方式 A（控制台，最简单）：
//   Cloudflare 控制台 → Workers & Pages → 创建 Worker → 粘贴本文件 → 保存
//   再在 Settings → Variables 里添加下面 6 个 secret（值不要带引号）
//
// 部署方式 B（wrangler）：
//   wrangler deploy   （secret 用：wrangler secret put ALIPAY_APP_ID 等）
//
// 需要的 Secret（env 变量）：
//   ALIPAY_APP_ID         你的支付宝 APPID（当面付应用），如 2021006170643597
//   ALIPAY_APP_PRIVATE_KEY 应用私钥（PKCS8 PEM，含 -----BEGIN/END----- 和换行）
//   ALIPAY_PUBLIC_KEY     支付宝公钥（SPKI PEM，注意是“支付宝公钥”不是你上传的应用公钥）
//   ALIPAY_NOTIFY_URL     本 Worker 的 /notify 完整地址，如 https://pay.jugongchang.icu/notify
//   SUPABASE_URL          https://mqvygeoqjfylgdmklvrb.supabase.co
//   SUPABASE_SERVICE_ROLE  Supabase 的 service_role key（仅服务端用，切勿暴露到前端）

const GATEWAY = 'https://openapi.alipay.com/gateway.do';

function b64ToBin(b64){ const s=atob(b64); const u=new Uint8Array(s.length); for(let i=0;i<s.length;i++) u[i]=s.charCodeAt(i); return u.buffer; }
function pemToBin(pem){ const b=pem.replace(/-----[^-]+-----/g,'').replace(/\s+/g,''); return b64ToBin(b); }
function bufToB64(buf){ let s=''; const u=new Uint8Array(buf); for(let i=0;i<u.length;i++) s+=String.fromCharCode(u[i]); return btoa(s); }

// RSA2 签名：对排序后的参数串用应用私钥签名
async function sign(params, privatePem){
  const keys=Object.keys(params).filter(k=>k!=='sign'&&k!=='sign_type'&&params[k]!==''&&params[k]!=null).sort();
  const str=keys.map(k=>`${k}=${params[k]}`).join('&');
  const key=await crypto.subtle.importKey('pkcs8', pemToBin(privatePem), {name:'RSASSA-PKCS1-V1_5',hash:'sha-256'}, false, ['sign']);
  const sig=await crypto.subtle.sign({name:'RSASSA-PKCS1-V1_5'}, key, new TextEncoder().encode(str));
  return bufToB64(sig);
}

// 验签：用支付宝公钥验证回调签名
async function verify(params, publicPem){
  const keys=Object.keys(params).filter(k=>k!=='sign'&&k!=='sign_type'&&params[k]!==''&&params[k]!=null).sort();
  const str=keys.map(k=>`${k}=${params[k]}`).join('&');
  const key=await crypto.subtle.importKey('spki', pemToBin(publicPem), {name:'RSASSA-PKCS1-V1_5',hash:'sha-256'}, false, ['verify']);
  return crypto.subtle.verify({name:'RSASSA-PKCS1-V1_5'}, key, b64ToBin(params.sign), new TextEncoder().encode(str));
}

function beijingTime(){ return new Date(Date.now()+8*3600*1000).toISOString().slice(0,19).replace('T',' '); }

async function alipayGateway(env, method, biz){
  const params={
    app_id: env.ALIPAY_APP_ID,
    method, format:'JSON', charset:'utf-8', sign_type:'RSA2',
    timestamp: beijingTime(), version:'1.0',
    notify_url: env.ALIPAY_NOTIFY_URL,
    biz_content: JSON.stringify(biz)
  };
  params.sign = await sign(params, env.ALIPAY_APP_PRIVATE_KEY);
  const body = new URLSearchParams(params).toString();
  const r = await fetch(GATEWAY, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body});
  return r.json();
}

function json(o, status=200){
  return new Response(JSON.stringify(o), {status, headers:{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'}});
}

// 前端调用：POST /create  { uid, email, plan }
async function handleCreate(req, env){
  let body; try{ body = await req.json(); }catch{ return json({error:'bad request'},400); }
  const out_trade_no = 'JF' + Date.now() + Math.floor(Math.random()*1000);
  const passback = encodeURIComponent(JSON.stringify({ uid: body.uid||'', plan: 'premium' }));
  const biz = {
    out_trade_no,
    total_amount: '39.00',
    subject: '剧工厂专业版会员(月)',
    body: 'AI短剧脚本生成器-专业版',
    product_code: 'FACE_TO_FACE_PAYMENT',
    passback_params: passback
  };
  const resp = await alipayGateway(env, 'alipay.trade.precreate', biz);
  const node = resp.alipay_trade_precreate_response;
  if(node && node.code==='10000' && node.qr_code){
    return json({ qr: node.qr_code, out_trade_no });
  }
  return json({ error: (node && (node.sub_msg || node.msg)) || 'alipay error' }, 500);
}

// 支付宝异步回调：POST /notify  (form-urlencoded)
async function handleNotify(req, env){
  const text = await req.text();
  const params = Object.fromEntries(new URLSearchParams(text));
  let ok=false;
  try{ ok = await verify(params, env.ALIPAY_PUBLIC_KEY); }catch(e){ ok=false; }
  if(!ok) return new Response('failure', {status:200});

  const status = params.trade_status;
  if(status==='TRADE_SUCCESS' || status==='TRADE_FINISHED'){
    try{
      const pb = JSON.parse(decodeURIComponent(params.passback_params || '{}'));
      const uid = pb.uid;
      if(uid){
        await fetch(`${env.SUPABASE_URL}/rest/v1/profiles?id=eq.${uid}`, {
          method:'PATCH',
          headers:{
            'apikey': env.SUPABASE_SERVICE_ROLE,
            'Authorization': `Bearer ${env.SUPABASE_SERVICE_ROLE}`,
            'Content-Type':'application/json',
            'Prefer':'return=minimal'
          },
          body: JSON.stringify({ plan:'premium' })
        });
      }
    }catch(e){ /* 记日志即可 */ }
  }
  // 必须返回 success，否则支付宝会重复回调
  return new Response('success', {status:200});
}

export default {
  async fetch(request, env){
    const url = new URL(request.url);
    if(request.method==='OPTIONS'){
      return new Response(null,{status:204,headers:{'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'*'}});
    }
    if(url.pathname==='/create' && request.method==='POST') return handleCreate(request, env);
    if(url.pathname==='/notify' && request.method==='POST') return handleNotify(request, env);
    return new Response('not found', {status:404});
  }
};
