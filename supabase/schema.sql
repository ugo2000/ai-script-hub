-- 剧工厂 · Supabase 数据库结构
-- 在 Supabase 控制台 → SQL Editor 中粘贴全部内容并运行 (Run)

-- ============ profiles 表（用户资料 + 套餐 + 每日次数） ============
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  nickname text,
  plan text not null default 'free' check (plan in ('free','premium','studio')),
  daily_uses integer not null default 0,
  last_used_date date default current_date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============ usage_logs 表（每次生成记录，用于累计统计） ============
create table if not exists public.usage_logs (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  genre text,
  plot text,
  created_at timestamptz not null default now()
);

-- ============ 索引 ============
create index if not exists idx_usage_logs_user on public.usage_logs(user_id);
create index if not exists idx_profiles_plan on public.profiles(plan);

-- ============ 行级安全 (RLS) ============
alter table public.profiles enable row level security;
alter table public.usage_logs enable row level security;

-- 用户只能看/改自己的资料
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own" on public.profiles
  for insert with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

-- 用户只能看/写自己的生成记录
drop policy if exists "usage_select_own" on public.usage_logs;
create policy "usage_select_own" on public.usage_logs
  for select using (auth.uid() = user_id);

drop policy if exists "usage_insert_own" on public.usage_logs;
create policy "usage_insert_own" on public.usage_logs
  for insert with check (auth.uid() = user_id);

-- ============ 新用户自动建资料 ============
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, nickname)
  values (new.id, coalesce(new.raw_user_meta_data->>'nickname', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
