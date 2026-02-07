const STORAGE_KEY = 'bbs-posts';

function getPosts() {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : [];
}

function savePosts(posts) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(posts));
}

function formatDate(timestamp) {
  const d = new Date(timestamp);
  return d.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function renderPosts() {
  const posts = getPosts();
  const container = document.getElementById('postList');
  const emptyMsg = document.getElementById('emptyMessage');

  container.innerHTML = '';

  if (posts.length === 0) {
    emptyMsg.classList.remove('hidden');
    return;
  }

  emptyMsg.classList.add('hidden');

  posts
    .slice()
    .reverse()
    .forEach((post) => {
      const el = document.createElement('article');
      el.className = 'post-item';
      el.dataset.id = post.id;
      el.innerHTML = `
        <div class="post-header">
          <span class="post-title">${escapeHtml(post.title)}</span>
          <span class="post-meta">${escapeHtml(post.author)} · ${formatDate(post.createdAt)}</span>
        </div>
        <div class="post-content">${escapeHtml(post.content)}</div>
        <div class="post-footer">
          <button type="button" class="btn btn-danger delete-btn" data-id="${post.id}">削除</button>
        </div>
      `;
      container.appendChild(el);
    });

  container.querySelectorAll('.delete-btn').forEach((btn) => {
    btn.addEventListener('click', () => deletePost(btn.dataset.id));
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function addPost(author, title, content) {
  const posts = getPosts();
  const post = {
    id: Date.now().toString(),
    author: author.trim(),
    title: title.trim(),
    content: content.trim(),
    createdAt: Date.now()
  };
  posts.push(post);
  savePosts(posts);
  renderPosts();
}

function deletePost(id) {
  if (!confirm('この投稿を削除しますか？')) return;
  const posts = getPosts().filter((p) => p.id !== id);
  savePosts(posts);
  renderPosts();
}

document.getElementById('postForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const author = document.getElementById('author').value;
  const title = document.getElementById('title').value;
  const content = document.getElementById('content').value;

  if (!author || !title || !content) return;

  addPost(author, title, content);
  document.getElementById('postForm').reset();
  document.getElementById('author').focus();
});

renderPosts();
