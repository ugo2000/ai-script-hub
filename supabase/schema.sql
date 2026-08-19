-- ============================================================
-- Supabase SQL Schema for ai-script-hub
-- Run this in Supabase Dashboard → SQL Editor
-- ============================================================

-- 1. 用户资料表（扩展 Supabase Auth 的 profiles）
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  nickname TEXT,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'premium', 'studio')),
  premium_until TIMESTAMPTZ,
  daily_uses INT DEFAULT 0,
  last_used_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 触发器：新建用户时自动创建 profile
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, nickname)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'nickname', split_part(NEW.email, '@', 1)));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 2. 使用记录表
CREATE TABLE IF NOT EXISTS public.usage_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  genre TEXT,
  plot TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 支付记录表
CREATE TABLE IF NOT EXISTS public.payments (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  out_trade_no TEXT UNIQUE,
  trade_no TEXT,
  amount DECIMAL(10,2),
  plan TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'closed', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  paid_at TIMESTAMPTZ
);

-- ============================================================
-- Row Level Security
-- ============================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- profiles: 只有本人可读/改
CREATE POLICY "Users can view own profile" ON public.profiles
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- usage_logs: 只有本人可读写
CREATE POLICY "Users can manage own usage" ON public.usage_logs
  FOR ALL USING (auth.uid() = user_id);

-- payments: 只有本人可读写
CREATE POLICY "Users can manage own payments" ON public.payments
  FOR ALL USING (auth.uid() = user_id);

-- 允许匿名插入（支付回调时没有登录）
CREATE POLICY "Allow anonymous insert for payments" ON public.payments
  FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update for payments" ON public.payments
  FOR UPDATE USING (true);
