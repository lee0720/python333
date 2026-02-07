/**
 * キリスト・プログラム — 聖書に基づく悩み相談
 * 悩みを入力すると、聖書の引用とともに解決のヒントを返します。
 */

const STORAGE_KEY = 'christ-app-api-key';

// デモ用：悩みのキーワードに対応する聖書の引用（書名 章:節）
const BIBLE_VERSES = [
  { keywords: ['不安', '心配', '恐れ', '怖い'], ref: 'マタイによる福音書 6:34', text: 'だから、明日のことまで思い悩むな。明日のことは明日自らが思い悩む。その日の苦労は、その日だけで十分である。' },
  { keywords: ['疲れ', '疲れた', '重荷', '休み'], ref: 'マタイによる福音書 11:28', text: '疲れた者、重荷を負う者は、だれでもわたしのもとに来なさい。休ませてあげよう。' },
  { keywords: ['希望', '絶望', '先が見えない'], ref: 'ローマの信徒への手紙 15:13', text: '希望の源である神が、信仰によって得られるあらゆる喜びと平和であなたがたを満たし、聖霊の力によって希望に満ちあふれさせてくださるように。' },
  { keywords: ['愛', '愛する', '嫌い', '憎い'], ref: 'コリントの信徒への手紙一 13:4-7', text: '愛は忍耐強い。愛は情け深い。ねたまない。愛は自慢せず、高ぶらない。礼を失せず、自分の利益を求めず、いらだたず、恨みを抱かない。不正を喜ばず、真実を喜ぶ。すべてを忍び、すべてを信じ、すべてを望み、すべてに耐える。' },
  { keywords: ['人間関係', '仲間', '友達', '孤独', 'ひとり'], ref: '伝道の書 4:9-10', text: '二人は一人にまさる。二人が一緒に労苦すれば、その報いは良い。倒れれば、友がその人を起こす。ひとりで倒れて起こす者のない者は不幸である。' },
  { keywords: ['弱さ', '弱い', '力'], ref: 'コリントの信徒への手紙二 12:9', text: '「わたしの恵みはあなたに十分である。力は弱さの中でこそ十分に発揮されるからである。」' },
  { keywords: ['赦し', '許し', '許せない', '恨み'], ref: 'コロサイの信徒への手紙 3:13', text: '互いに忍び合い、責めるべきことがあっても、赦し合いなさい。主があなたがたを赦してくださったように、あなたがたも同じようにしなさい。' },
  { keywords: ['平和', '平安', '心の安らぎ'], ref: 'ヨハネによる福音書 14:27', text: '平和をあなたがたに残し、わたしの平和をあなたがたに与える。わたしはこれを、世が与えるように与えるのではない。心を騒がせるな。おびえるな。' },
  { keywords: ['将来', '未来', '明日'], ref: 'エレミヤ書 29:11', text: 'わたしはあなたたちのために立てた計画をよく心に留めている、と主は言われる。それは平和の計画であって、災いの計画ではない。将来と希望を与えるものである。' },
  { keywords: ['試練', '苦しみ', '困難', 'つらい'], ref: 'ヤコブの手紙 1:2-4', text: 'わたしの兄弟たち、いろいろな試練に出会うときは、この上ない喜びと思いなさい。信仰が試されることで忍耐が生じると、あなたがたは知っています。忍耐を完全に働かせなさい。そうすれば、あなたがたは何も欠けたところのない、成長を遂げた、完全な人となります。' },
  { keywords: ['祈り', '祈る', '願い'], ref: 'マタイによる福音書 7:7', text: '求めなさい。そうすれば、与えられる。探しなさい。そうすれば、見つかる。門をたたきなさい。そうすれば、開かれる。' },
  { keywords: ['感謝', 'ありがとう'], ref: 'テサロニケの信徒への手紙一 5:18', text: 'どんなことにも感謝しなさい。これこそ、キリスト・イエスにおいて、神があなたがたに望んでおられることである。' },
  { keywords: ['勇気', '勇気が出ない', '臆病'], ref: 'ヨシュア記 1:9', text: 'わたしはあなたに命じたではないか。強く、また雄々しくあれ。恐れてはならない。おののいてはならない。あなたの神、主があなたの行く所どこにでも、あなたと共にいるからである。' },
  { keywords: ['導き', '道', '迷う', '決められない'], ref: '箴言 3:5-6', text: '心を尽くして主に依り頼め。自分の悟りにたよるな。あなたの行く所どこにおいても、主を認めよ。そうすれば、主はあなたの道をまっすぐにされる。' },
  { keywords: ['賛美', '喜び', '喜ぶ'], ref: '詩編 34:2', text: 'わたしは主を常に賛美する。わたしの口は主を賛美してやまない。' },
];

// デフォルトの引用（該当なし時）
const DEFAULT_VERSE = { ref: '詩編 46:2', text: '神はわたしたちの避け所、わたしたちの砦。苦難のとき、必ずそこにいまして助けてくださる。' };

const chatMessages = document.getElementById('chatMessages');
const welcome = document.getElementById('welcome');
const userInput = document.getElementById('userInput');
const btnSend = document.getElementById('btnSend');
const btnSettings = document.getElementById('btnSettings');
const settingsModal = document.getElementById('settingsModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const apiKeyInput = document.getElementById('apiKeyInput');
const btnCloseSettings = document.getElementById('btnCloseSettings');
const btnSaveSettings = document.getElementById('btnSaveSettings');

let apiKey = localStorage.getItem(STORAGE_KEY) || '';

function hideWelcome() {
  welcome.style.display = 'none';
}

function appendMessage(role, content, verse = null) {
  hideWelcome();
  const msg = document.createElement('div');
  msg.className = `msg ${role}`;
  const avatar = role === 'user' ? '🙏' : '✝';
  let body = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-body">
      <p class="msg-text">${escapeHtml(content)}</p>
      ${verse ? `<div class="verse-block"><span class="verse-ref">${escapeHtml(verse.ref)}</span><p class="verse-text">${escapeHtml(verse.text)}</p></div>` : ''}
    </div>
  `;
  msg.innerHTML = body;
  chatMessages.appendChild(msg);
  msg.scrollIntoView({ behavior: 'smooth' });
  return msg;
}

function appendLoadingMessage() {
  hideWelcome();
  const msg = document.createElement('div');
  msg.className = 'msg assistant msg-loading';
  msg.innerHTML = `
    <div class="msg-avatar">✝</div>
    <div class="msg-body">
      <p class="msg-text">聖書をひも解いています…</p>
    </div>
  `;
  chatMessages.appendChild(msg);
  msg.scrollIntoView({ behavior: 'smooth' });
  return msg;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function findVerse(text) {
  const lower = text.toLowerCase().replace(/\s/g, '');
  for (const v of BIBLE_VERSES) {
    if (v.keywords.some(kw => text.includes(kw) || lower.includes(kw))) {
      return v;
    }
  }
  return DEFAULT_VERSE;
}

async function callOpenAI(messages) {
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `あなたは聖書に基づいて悩みに寄り添う、温かく知恵のある相談役です。
ユーザーの悩みや質問に対して、必ず聖書の引用（書名と章・節）を交えながら、日本語で短く励ましと解決のヒントを伝えてください。
引用は「書名 章:節」の形式で明記し、その直後に聖句の内容を要約または引用してください。
説教調にせず、親しみやすく、具体的な一歩がわかるように答えてください。`,
        },
        ...messages,
      ],
      max_tokens: 600,
      temperature: 0.7,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `API エラー: ${res.status}`);
  }
  const data = await res.json();
  return data.choices[0].message.content.trim();
}

function getDemoResponse(userText) {
  const verse = findVerse(userText);
  const shortAdvice = 'そのようなとき、聖書は私たちに神に頼り、一日一日を大切に生きるよう勧めています。祈りと聖書の言葉に触れる時間を持つと、心が軽くなることがあります。';
  return { text: shortAdvice, verse };
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  userInput.value = '';
  appendMessage('user', text);

  const loadingEl = appendLoadingMessage();

  try {
    if (apiKey) {
      const history = getHistory();
      const newMessages = [...history, { role: 'user', content: text }];
      const reply = await callOpenAI(newMessages);
      loadingEl.remove();
      appendMessage('assistant', reply, null);
    } else {
      await new Promise(r => setTimeout(r, 800 + Math.random() * 400));
      const { text: advice, verse } = getDemoResponse(text);
      loadingEl.remove();
      appendMessage('assistant', advice, verse);
    }
  } catch (err) {
    loadingEl.remove();
    appendMessage('assistant', `申し訳ありません。エラーが発生しました：${err.message}。APIキーを確認するか、そのままもう一度送信するとデモ応答でお答えします。`, null);
  }
}

function getHistory() {
  const msgs = chatMessages.querySelectorAll('.msg');
  const arr = [];
  msgs.forEach(m => {
    if (m.classList.contains('user')) {
      const t = m.querySelector('.msg-text');
      if (t) arr.push({ role: 'user', content: t.textContent.trim() });
    } else if (m.classList.contains('assistant') && !m.classList.contains('msg-loading')) {
      const t = m.querySelector('.msg-text');
      if (t) arr.push({ role: 'assistant', content: t.textContent.trim() });
    }
  });
  return arr.slice(-10);
}

btnSend.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

btnSettings.addEventListener('click', () => {
  settingsModal.setAttribute('aria-hidden', 'false');
  apiKeyInput.value = apiKey;
});
modalBackdrop.addEventListener('click', () => settingsModal.setAttribute('aria-hidden', 'true'));
btnCloseSettings.addEventListener('click', () => settingsModal.setAttribute('aria-hidden', 'true'));
btnSaveSettings.addEventListener('click', () => {
  apiKey = apiKeyInput.value.trim();
  localStorage.setItem(STORAGE_KEY, apiKey);
  settingsModal.setAttribute('aria-hidden', 'true');
});
