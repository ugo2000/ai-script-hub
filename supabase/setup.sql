-- 剧工厂 · Supabase 一键安装
-- 在 Supabase 控制台 → SQL Editor 中，粘贴本文件全部内容，点击 Run 即可。
-- 只需运行一次。会创建：用户表、使用记录表、以及调用 DeepSeek 的云端函数。

-- ============ 1. 启用 HTTP 扩展（用于云端函数联网调用 DeepSeek） ============
create extension if not exists http;

-- ============ 2. profiles 表（资料 + 套餐 + 每日次数） ============
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  nickname text,
  plan text not null default 'free' check (plan in ('free','premium','studio')),
  daily_uses integer not null default 0,
  last_used_date date default current_date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============ 3. usage_logs 表（每次生成记录，用于累计统计） ============
create table if not exists public.usage_logs (
  id bigserial primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  genre text,
  plot text,
  created_at timestamptz not null default now()
);

create index if not exists idx_usage_logs_user on public.usage_logs(user_id);
create index if not exists idx_profiles_plan on public.profiles(plan);

-- ============ 4. 行级安全 (RLS) ============
alter table public.profiles enable row level security;
alter table public.usage_logs enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles for select using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own" on public.profiles for insert with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles for update using (auth.uid() = id);

drop policy if exists "usage_select_own" on public.usage_logs;
create policy "usage_select_own" on public.usage_logs for select using (auth.uid() = user_id);

drop policy if exists "usage_insert_own" on public.usage_logs;
create policy "usage_insert_own" on public.usage_logs for insert with check (auth.uid() = user_id);

-- ============ 5. 新用户自动建资料 ============
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

-- ============ 6. 云端 AI 函数（前端调用，DeepSeek key 仅存于数据库） ============
-- 注意：把下面 v_api_key 的值换成你自己的 DeepSeek key（以 sk- 开头）
create or replace function public.generate_script(
  p_genre text,
  p_plot text,
  p_rhythm text,
  p_characters text,
  p_special text
)
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  v_api_key text := 'sk-a8a09e59ec61461cb333c75aca946c90';
  v_rhythm_map jsonb := '{
    "hot":"参考当下最火短剧爆款公式，开头5秒必须有高能钩子，每15秒一个情绪引爆点",
    "short":"精简快节奏，每句台词不超15字，平均8-10秒切换一场景",
    "long":"深度剧情版，对白丰富，铺垫人物关系，单集1200-1500字"
  }';
  v_rhythm text;
  v_system text;
  v_user text;
  v_body json;
  v_req http_request;
  v_res http_response;
  v_content text;
begin
  v_rhythm := coalesce(v_rhythm_map->>p_rhythm, v_rhythm_map->>'hot');

  v_system := '你是一位专业AI短剧编剧，精通竖屏短剧创作。'
    || '规则：1)竖屏思维，人物半身/特写为主 2)每15-20秒一个情绪点 3)台词一句不超20字 '
    || '4)爽点密集：打脸/反转/告白交替 5)每集结尾留悬念。'
    || '输出格式：' || chr(10)
    || '【剧名】' || chr(10)
    || '【类型】' || coalesce(p_genre,'都市逆袭') || chr(10)
    || '【集数】第1集（约3分钟，800-1000字）' || chr(10)
    || '【人物表】' || chr(10)
    || '【剧情概要】100字' || chr(10)
    || '【分镜表】|镜头|景别|时长|画面|台词|音效|' || chr(10)
    || '【完整剧本】' || chr(10)
    || '【下集钩子】';

  v_user := '## 题材' || chr(10) || coalesce(p_genre,'都市逆袭')
    || chr(10) || '## 核心梗概' || chr(10) || coalesce(p_plot,'')
    || chr(10) || '## 节奏风格' || chr(10) || v_rhythm
    || case when p_characters is not null and p_characters <> '' then chr(10) || '## 人物设定' || chr(10) || p_characters else '' end
    || case when p_special is not null and p_special <> '' then chr(10) || '## 特殊要求' || chr(10) || p_special else '' end;

  v_body := json_build_object(
    'model','deepseek-chat',
    'messages', json_build_array(
      json_build_object('role','system','content', v_system),
      json_build_object('role','user','content', v_user)
    ),
    'temperature', 0.8,
    'max_tokens', 2000
  );

  v_req := http_request(
    'https://api.deepseek.com/chat/completions',
    'POST',
    array[
      http_header('Content-Type','application/json'),
      http_header('Authorization','Bearer ' || v_api_key)
    ]::http_header[],
    'application/json',
    v_body::text
  );

  v_res := http(v_req);

  if v_res.status <> 200 then
    raise exception 'DeepSeek 返回错误 (状态 %): %', v_res.status, v_res.content;
  end if;

  v_content := (v_res.content::json)->'choices'->0->'message'->>'content';
  return v_content;
end;
$$;

-- 允许已登录用户调用该函数
grant execute on function public.generate_script(text,text,text,text,text) to authenticated;
