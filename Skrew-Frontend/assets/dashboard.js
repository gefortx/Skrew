(function () {
  'use strict';

  const form = document.getElementById('postForm');
  const feed = document.getElementById('sessionFeed');
  const countEl = document.getElementById('sessionCount');
  const toast = document.getElementById('toast');
  const navNewBtn = document.getElementById('navNewSession');

  let toastTimer = null;

  function showToast(message) {
    if (toastTimer) {
      clearTimeout(toastTimer);
      toastTimer = null;
    }
    toast.textContent = message;
    toast.classList.add('show');
    toastTimer = setTimeout(() => {
      toast.classList.remove('show');
      toastTimer = null;
    }, 2600);
  }

  function updateCount() {
    const cards = feed.querySelectorAll('[data-session]');
    countEl.textContent = String(cards.length);
  }

  function getBadgeClass(skill) {
    const map = {
      'Beginner': 'badge-beginner',
      'Intermediate': 'badge-intermediate',
      'Advanced': 'badge-advanced',
      'All Levels': 'badge-all'
    };
    return map[skill] || 'badge-all';
  }

  function getAvatarColor() {
    const colors = ['#FF6B35', '#5B8DEF', '#22A06B', '#A855F7', '#EC4899', '#14B8A6', '#F59E0B'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  function formatDate(dateStr) {
    if (!dateStr) return 'TBD';
    try {
      const d = new Date(dateStr + 'T00:00:00');
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);
      const day = d.getDay();
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const sameDay = (a, b) =>
        a.getFullYear() === b.getFullYear() &&
        a.getMonth() === b.getMonth() &&
        a.getDate() === b.getDate();
      if (sameDay(d, today)) return 'Today';
      if (sameDay(d, tomorrow)) return 'Tomorrow';
      return days[day];
    } catch (e) {
      return dateStr;
    }
  }

  function formatTime(timeStr) {
    if (!timeStr) return '';
    try {
      const [h, m] = timeStr.split(':').map(Number);
      const hour = h % 12 === 0 ? 12 : h % 12;
      const ampm = h >= 12 ? 'PM' : 'AM';
      return `${hour}:${String(m).padStart(2, '0')} ${ampm}`;
    } catch (e) {
      return timeStr;
    }
  }

  function createSessionCard(data) {
    const article = document.createElement('article');
    article.className = 'session-card';
    article.setAttribute('data-session', '');

    const initial = (data.username && data.username.charAt(0).toUpperCase()) || 'U';
    const avatarColor = getAvatarColor();

    const skillBadgeClass = getBadgeClass(data.skill);
    const dateLabel = formatDate(data.date);
    const timeLabel = formatTime(data.time);
    const notesHtml = data.notes
      ? `<p class="notes">${escapeHtml(data.notes)}</p>`
      : '';

    article.innerHTML = `
      <div class="card-head">
        <div class="poster">
          <div class="avatar" style="--accent:${avatarColor}">${initial}</div>
          <div class="poster-meta">
            <span class="poster-name">${escapeHtml(data.username)}</span>
            <span class="post-time">Just now</span>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div class="detail">
          <span class="dicon">📍</span>
          <div>
            <div class="detail-main">${escapeHtml(data.spotName)}</div>
            <div class="detail-sub">${escapeHtml(data.address)}</div>
          </div>
        </div>
        <div class="detail-row">
          <div class="detail-inline">
            <span class="dicon">📅</span>
            <span>${escapeHtml(dateLabel)}</span>
          </div>
          <div class="detail-inline">
            <span class="dicon">⏰</span>
            <span>${escapeHtml(timeLabel)}</span>
          </div>
        </div>
        <div class="detail-inline">
          <span class="dicon">🎯</span>
          <span class="badge ${skillBadgeClass}">${escapeHtml(data.skill)}</span>
        </div>
        ${notesHtml}
      </div>
      <div class="card-actions">
        <button class="btn-join" type="button">I'm In</button>
        <button class="link-btn" type="button">View on Map</button>
      </div>
    `;

    wireJoinButton(article.querySelector('.btn-join'));
    return article;
  }

  function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function wireJoinButton(btn) {
    if (!btn) return;
    btn.addEventListener('click', function () {
      const joined = btn.classList.toggle('joined');
      btn.textContent = joined ? 'Joined \u2713' : "I'm In";
    });
  }

  document.querySelectorAll('.btn-join').forEach(wireJoinButton);

  if (navNewBtn) {
    navNewBtn.addEventListener('click', function () {
      if (form) {
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        const firstField = form.querySelector('input, textarea, select');
        if (firstField) {
          setTimeout(() => firstField.focus(), 420);
        }
      }
    });
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const fd = new FormData(form);
      const data = {
        username: 'you_sk8',
        spotName: (fd.get('spotName') || '').toString().trim(),
        address: (fd.get('address') || '').toString().trim(),
        date: (fd.get('date') || '').toString().trim(),
        time: (fd.get('time') || '').toString().trim(),
        skill: (fd.get('skill') || 'Intermediate').toString(),
        notes: (fd.get('notes') || '').toString().trim()
      };

      if (!data.spotName || !data.address || !data.date || !data.time) {
        showToast('Please fill in all required fields');
        return;
      }

      const card = createSessionCard(data);
      if (feed.firstChild) {
        feed.insertBefore(card, feed.firstChild);
      } else {
        feed.appendChild(card);
      }

      updateCount();
      showToast('Session posted! \u{1F6F9}');
      form.reset();

      const defaultSkill = form.querySelector('input[name="skill"][value="Intermediate"]');
      if (defaultSkill) defaultSkill.checked = true;
    });
  }

  updateCount();
})();
