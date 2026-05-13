/* ============================================================
   SISTEM MANAJEMEN MASJID — main.js
   ============================================================ */

"use strict";

/* ── 1. NAVBAR SCROLL EFFECT ──────────────────────────────── */
(function initNavbar() {
  const navbar = document.getElementById('mainNavbar');
  if (!navbar) return;

  function onScroll() {
    if (window.scrollY > 30) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // jalankan sekali saat load
})();


/* ── 2. ADMIN SIDEBAR TOGGLE (Mobile) ─────────────────────── */
(function initSidebar() {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar   = document.getElementById('adminSidebar');
  const overlay   = document.getElementById('sidebarOverlay');

  if (!toggleBtn || !sidebar || !overlay) return;

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
    document.body.style.overflow = '';
  }

  toggleBtn.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  // Klik overlay → tutup sidebar
  overlay.addEventListener('click', closeSidebar);

  // Tekan Escape → tutup sidebar
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
      closeSidebar();
    }
  });

  // Otomatis tutup sidebar saat resize ke desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 992) {
      closeSidebar();
    }
  });
})();


/* ── 3. AUTO-DISMISS FLASH MESSAGES ───────────────────────── */
(function initFlash() {
  // Flash di public page
  const flashContainer = document.querySelector('.flash-container');
  if (flashContainer) {
    const alerts = flashContainer.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
      setTimeout(function () {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }, 4500);
    });
  }

  // Flash di admin panel
  const adminAlerts = document.querySelectorAll('.admin-main .alert');
  adminAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4500);
  });
})();


/* ── 4. SMOOTH SCROLL untuk anchor link ───────────────────── */
(function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const navH   = parseInt(
        getComputedStyle(document.documentElement)
          .getPropertyValue('--navbar-h')
      ) || 70;
      const top = target.getBoundingClientRect().top + window.scrollY - navH - 16;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });
})();


/* ── 5. ANIMATION ON SCROLL ───────────────────────────────── */
(function initScrollAnimation() {
  // Cek dukungan IntersectionObserver
  if (!('IntersectionObserver' in window)) return;

  // Tambahkan class animate-ready ke elemen yang ingin dianimasi
  const targets = document.querySelectorAll(
    '.content-card, .kajian-card, .kajian-card-full, ' +
    '.pengumuman-card, .pengumuman-card-full, ' +
    '.stat-card, .admin-stat-card, .program-card, ' +
    '.rekening-card, .ayat-card'
  );

  targets.forEach(function (el) {
    el.style.opacity    = '0';
    el.style.transform  = 'translateY(16px)';
    el.style.transition = 'opacity .4s ease, transform .4s ease';
  });

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity   = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(function (el) { observer.observe(el); });
})();


/* ── 6. CONFIRM HAPUS (double-check) ──────────────────────── */
(function initDeleteConfirm() {
  // Sudah pakai onsubmit="return confirm(...)" di template
  // Ini sebagai fallback & enhancement untuk tombol hapus
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const msg = this.dataset.confirm || 'Yakin ingin menghapus?';
      if (!window.confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });
})();


/* ── 7. ACTIVE NAV LINK HIGHLIGHT ─────────────────────────── */
(function initActiveNav() {
  // Sudah dihandle Jinja di template, ini hanya fallback JS
  const path  = window.location.pathname;
  const links = document.querySelectorAll('.sidebar-link');
  links.forEach(function (link) {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });
})();


/* ── 8. FORM VALIDATION FEEDBACK ──────────────────────────── */
(function initFormFeedback() {
  const forms = document.querySelectorAll('form[novalidate]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
        // Focus ke field pertama yang invalid
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) {
          firstInvalid.focus();
          firstInvalid.classList.add('is-invalid');
        }
      }
      form.classList.add('was-validated');
    });

    // Hapus is-invalid saat user mulai ketik
    form.querySelectorAll('input, textarea, select').forEach(function (field) {
      field.addEventListener('input', function () {
        this.classList.remove('is-invalid');
      });
    });
  });
})();


/* ── 9. PROGRAM PROGRESS BAR ANIMATION ────────────────────── */
(function initProgressBar() {
  if (!('IntersectionObserver' in window)) return;

  const bars = document.querySelectorAll('.program-progress');
  if (!bars.length) return;

  // Simpan width asli, set ke 0 dulu
  bars.forEach(function (bar) {
    bar._targetWidth = bar.style.width || '0%';
    bar.style.width  = '0%';
  });

  const obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        const bar = entry.target;
        setTimeout(function () {
          bar.style.width = bar._targetWidth;
        }, 200);
        obs.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });

  bars.forEach(function (bar) { obs.observe(bar); });
})();


/* ── 10. TOOLTIP BOOTSTRAP (opsional) ─────────────────────── */
(function initTooltips() {
  if (typeof bootstrap === 'undefined') return;
  const tooltips = document.querySelectorAll('[title]');
  tooltips.forEach(function (el) {
    // Hanya aktifkan tooltip pada tombol aksi kecil
    if (el.classList.contains('btn-xs') || el.classList.contains('btn-share')) {
      new bootstrap.Tooltip(el, { trigger: 'hover', placement: 'top' });
    }
  });
})();


/* ── 11. TABLE RESPONSIVE HELPER ──────────────────────────── */
(function initTableHelper() {
  // Pastikan semua tabel punya wrapper responsive
  document.querySelectorAll('table:not(.table-responsive table)').forEach(function (table) {
    if (!table.closest('.table-responsive')) {
      const wrapper       = document.createElement('div');
      wrapper.className   = 'table-responsive';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });
})();