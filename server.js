const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const {
  GENRE_TEMPLATES,
  EXTRA_PROMPTS,
  SYSTEM_PROMPT,
  USER_PROMPT_TEMPLATE
} = require('./prompts');

// DeepSeek API proxy
const DEEPSEEK_API = process.env.DEEPSEEK_API || 'https://api.deepseek.com/v1/chat/completions';
const API_KEY = process.env.DEEPSEEK_KEY || '';

app.post('/api/generate', async (req, res) => {
  const { genre = 'niixi', plot, extra = 'hot', characters = '', special = '' } = req.body;

  if (!plot) {
    return res.status(400).json({ error: '请提供核心梗概' });
  }

  const genreTmpl = GENRE_TEMPLATES[genre];
  const extraPrompt = EXTRA_PROMPTS[extra] || EXTRA_PROMPTS['hot'];

  const userPrompt = USER_PROMPT_TEMPLATE
    .replace('{genre}', genreTmpl ? genreTmpl.name : '自定义')
    .replace('{plot}', plot)
    .replace('{extra}', extraPrompt)
    .replace('{characters}', characters || '由AI根据题材自动生成')
    .replace('{special}', special || '无');

  const genreStructure = genreTmpl ? genreTmpl.structure : '';

  try {
    const response = await fetch(DEEPSEEK_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT + '\n\n' + genreStructure },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.8,
        max_tokens: 4096,
        stream: false
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      return res.status(response.status).json({ error: `API请求失败: ${errText}` });
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || '';

    // 估算 token 消耗
    const inputTokens = data.usage?.prompt_tokens || 0;
    const outputTokens = data.usage?.completion_tokens || 0;

    res.json({
      success: true,
      data: {
        script: content,
        usage: {
          input_tokens: inputTokens,
          output_tokens: outputTokens,
          estimated_cost: ((outputTokens / 1000000) * 6) + ((inputTokens / 1000000) * 2)
        }
      }
    });
  } catch (error) {
    res.status(500).json({ error: `生成失败: ${error.message}` });
  }
});

// 获取流派列表
app.get('/api/genres', (req, res) => {
  const genres = Object.entries(GENRE_TEMPLATES).map(([key, val]) => ({
    id: key,
    name: val.name,
    desc: val.desc
  }));
  res.json({ genres });
});

const PORT = process.env.PORT || 3722;
app.listen(PORT, () => {
  console.log(`🎬 AI 短剧脚本生成器运行在 http://localhost:${PORT}`);
  console.log(`   打开 http://localhost:${PORT} 开始创作`);
});
