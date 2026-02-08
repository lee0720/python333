const STORAGE_KEY = 'kakeibo-entries';

const expenseCategories = ['食費', '日用品', '交通費', '光熱費', '住居費', '通信費', '娯楽', '医療', 'その他'];
const incomeCategories = ['給与', '副業', '賞与', 'その他'];

let entries = loadEntries();

function loadEntries() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

function saveEntries() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function getToday() {
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function formatYen(n) {
  return '¥' + Number(n).toLocaleString();
}

function getMonthOptions() {
  const months = new Set(entries.map(e => e.date.slice(0, 7)));
  return Array.from(months).sort().reverse();
}

function renderMonthFilter() {
  const select = document.getElementById('filterMonth');
  const current = select.value;
  select.innerHTML = '<option value="">全期間</option>';
  getMonthOptions().forEach(ym => {
    const [y, m] = ym.split('-');
    const label = y + '年' + m + '月';
    const opt = document.createElement('option');
    opt.value = ym;
    opt.textContent = label;
    if (ym === current) opt.selected = true;
    select.appendChild(opt);
  });
}

function updateSummary() {
  const now = new Date();
  const ym = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
  const thisMonth = entries.filter(e => e.date.startsWith(ym));
  const income = thisMonth.filter(e => e.type === 'income').reduce((s, e) => s + e.amount, 0);
  const expense = thisMonth.filter(e => e.type === 'expense').reduce((s, e) => s + e.amount, 0);
  const totalIncome = entries.filter(e => e.type === 'income').reduce((s, e) => s + e.amount, 0);
  const totalExpense = entries.filter(e => e.type === 'expense').reduce((s, e) => s + e.amount, 0);
  const balance = totalIncome - totalExpense;

  document.getElementById('monthlyIncome').textContent = formatYen(income);
  document.getElementById('monthlyExpense').textContent = formatYen(expense);
  const balanceEl = document.getElementById('balanceAmount');
  balanceEl.textContent = formatYen(balance);
  balanceEl.classList.toggle('negative', balance < 0);
}

function switchCategoryByType(type) {
  const expenseOpt = document.getElementById('expenseCategories');
  const incomeOpt = document.getElementById('incomeCategories');
  const categorySelect = document.getElementById('category');
  if (type === 'income') {
    expenseOpt.style.display = 'none';
    incomeOpt.style.display = '';
    categorySelect.value = incomeCategories[0];
  } else {
    expenseOpt.style.display = '';
    incomeOpt.style.display = 'none';
    categorySelect.value = expenseCategories[0];
  }
}

function getFilteredEntries() {
  const month = document.getElementById('filterMonth').value;
  const type = document.getElementById('filterType').value;
  let list = [...entries];
  if (month) list = list.filter(e => e.date.startsWith(month));
  if (type) list = list.filter(e => e.type === type);
  return list.sort((a, b) => b.date.localeCompare(a.date) || (b.id - a.id));
}

function renderList() {
  const listEl = document.getElementById('entryList');
  const list = getFilteredEntries();
  if (list.length === 0) {
    listEl.innerHTML = '<li class="empty-state">取引がありません</li>';
    return;
  }
  listEl.innerHTML = list.map(e => {
    const amountClass = e.type === 'income' ? 'income' : 'expense';
    const sign = e.type === 'income' ? '+' : '-';
    return `
      <li class="entry-item" data-id="${e.id}">
        <div class="entry-left">
          <div class="entry-date">${e.date}</div>
          <div class="entry-category">${e.category}</div>
          ${e.memo ? `<div class="entry-memo">${escapeHtml(e.memo)}</div>` : ''}
        </div>
        <span class="entry-amount ${amountClass}">${sign}${formatYen(e.amount)}</span>
        <button type="button" class="entry-delete" aria-label="削除">×</button>
      </li>
    `;
  }).join('');

  listEl.querySelectorAll('.entry-delete').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = Number(btn.closest('.entry-item').dataset.id);
      entries = entries.filter(e => e.id !== id);
      saveEntries();
      updateSummary();
      renderMonthFilter();
      renderList();
    });
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function initForm() {
  document.getElementById('date').value = getToday();
  document.getElementById('typeExpense').checked = true;
  switchCategoryByType('expense');

  document.querySelectorAll('input[name="type"]').forEach(radio => {
    radio.addEventListener('change', () => switchCategoryByType(radio.value));
  });

  document.getElementById('entryForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const type = document.querySelector('input[name="type"]:checked').value;
    const date = document.getElementById('date').value;
    const category = document.getElementById('category').value;
    const amount = Math.abs(Number(document.getElementById('amount').value) || 0);
    const memo = document.getElementById('memo').value.trim();
    if (!amount) return;
    const id = entries.length ? Math.max(...entries.map(e => e.id)) + 1 : 1;
    entries.push({ id, type, date, category, amount, memo });
    saveEntries();
    updateSummary();
    renderMonthFilter();
    renderList();
    document.getElementById('amount').value = '';
    document.getElementById('memo').value = '';
  });

  document.getElementById('filterMonth').addEventListener('change', renderList);
  document.getElementById('filterType').addEventListener('change', renderList);
}

function init() {
  renderMonthFilter();
  updateSummary();
  renderList();
  initForm();
}

init();
