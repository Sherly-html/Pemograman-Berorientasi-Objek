/* ============================================================
   main.js — SmartShop
   Fitur:
   - Navbar hamburger toggle (mobile)
   - Toggle show/hide password
   - Filter produk (search + kategori)
   - Auto-dismiss flash messages
   - Konfirmasi sebelum delete
   - Animasi loading tombol submit
   ============================================================ */

'use strict';

/* ===== 1. NAVBAR HAMBURGER ===== */
(function initNavbar() {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
    // Animasi 3 garis → X
    const spans = toggle.querySelectorAll('span');
    if (isOpen) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity   = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.opacity   = '';
      spans[2].style.transform = '';
    }
  });

  // Tutup navbar jika klik di luar
  document.addEventListener('click', function (e) {
    if (!toggle.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
      toggle.querySelectorAll('span').forEach(s => {
        s.style.transform = '';
        s.style.opacity   = '';
      });
    }
  });
})();


/* ===== 2. TOGGLE PASSWORD VISIBILITY ===== */
function togglePass(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈';
    btn.title = 'Sembunyikan password';
  } else {
    input.type = 'password';
    btn.textContent = '👁';
    btn.title = 'Tampilkan password';
  }
}


/* ===== 3. FILTER PRODUK (Search + Kategori) ===== */
function filterProducts() {
  const keyword  = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
  const category = (document.getElementById('categoryFilter')?.value || '').toLowerCase();
  const grid     = document.getElementById('productGrid');
  const empty    = document.getElementById('emptyFilter');
  if (!grid) return;

  const cards   = grid.querySelectorAll('.product-card');
  let visCount  = 0;

  cards.forEach(function (card) {
    const name = (card.dataset.name || '').toLowerCase();
    const cat  = (card.dataset.category || '').toLowerCase();

    const matchKeyword  = keyword  === '' || name.includes(keyword);
    const matchCategory = category === '' || cat === category;

    if (matchKeyword && matchCategory) {
      card.style.display = '';
      visCount++;
    } else {
      card.style.display = 'none';
    }
  });

  // Tampilkan empty state jika tidak ada hasil
  if (empty) {
    empty.style.display = visCount === 0 ? 'block' : 'none';
  }
  if (grid) {
    grid.style.display = visCount === 0 ? 'none' : '';
  }
}

function clearFilter() {
  const si = document.getElementById('searchInput');
  const cf = document.getElementById('categoryFilter');
  if (si) si.value = '';
  if (cf) cf.value = '';
  filterProducts();
}


/* ===== 4. AUTO-DISMISS FLASH MESSAGES ===== */
(function autoDismissFlash() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    // Success & info hilang otomatis setelah 4 detik
    const isAutoClose = alert.classList.contains('alert-success') ||
                        alert.classList.contains('alert-info');
    if (isAutoClose) {
      setTimeout(function () {
        alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        alert.style.opacity    = '0';
        alert.style.transform  = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 500);
      }, 4000);
    }
  });
})();


/* ===== 5. LOADING STATE PADA TOMBOL SUBMIT ===== */
(function initFormLoading() {
  const forms = document.querySelectorAll('form');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // Jangan loading jika form punya onsubmit confirm yang dibatalkan
      const submitBtns = form.querySelectorAll('button[type="submit"]');
      submitBtns.forEach(function (btn) {
        // Skip tombol yang punya value (approve/reject) — sudah ada confirm sendiri
        if (btn.getAttribute('name') === 'action') return;
        // Skip tombol hapus
        if (btn.classList.contains('btn-danger')) return;

        setTimeout(function () {
          btn.disabled = true;
          const original = btn.textContent;
          btn.dataset.original = original;
          btn.textContent = '⏳ Memproses...';
          btn.style.opacity = '0.7';
        }, 10);
      });
    });
  });
})();


/* ===== 6. FORMAT ANGKA REAL-TIME (input harga) ===== */
(function initPriceFormat() {
  const priceInputs = document.querySelectorAll('input[name="price"]');
  priceInputs.forEach(function (input) {
    input.addEventListener('input', function () {
      // Pastikan tidak negatif
      if (parseFloat(this.value) < 0) this.value = 0;
    });
  });

  const stockInputs = document.querySelectorAll('input[name="stock"]');
  stockInputs.forEach(function (input) {
    input.addEventListener('input', function () {
      if (parseInt(this.value) < 0) this.value = 0;
    });
  });
})();


/* ===== 7. HIGHLIGHT ACTIVE PAYMENT OPTION ===== */
(function initPaymentSelect() {
  const radios = document.querySelectorAll('.payment-option input[type="radio"]');
  radios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      // Hapus highlight dari semua
      document.querySelectorAll('.payment-option').forEach(opt => {
        opt.style.borderColor  = '';
        opt.style.background   = '';
        opt.style.fontWeight   = '';
      });
      // Highlight yang dipilih
      if (this.checked) {
        const label = this.closest('.payment-option');
        if (label) {
          label.style.borderColor = '#1a73e8';
          label.style.background  = '#e8f0fe';
        }
      }
    });
  });
})();


/* ===== 8. TOOLTIP SEDERHANA ===== */
(function initTooltip() {
  document.querySelectorAll('[data-tooltip]').forEach(function (el) {
    el.style.position = 'relative';
    el.addEventListener('mouseenter', function () {
      const tip = document.createElement('div');
      tip.className = 'tooltip-box';
      tip.textContent = el.dataset.tooltip;
      tip.style.cssText = `
        position:absolute; bottom:calc(100% + 6px); left:50%;
        transform:translateX(-50%); background:#202124; color:#fff;
        padding:4px 10px; border-radius:6px; font-size:0.75rem;
        white-space:nowrap; z-index:999; pointer-events:none;
        box-shadow:0 2px 6px rgba(0,0,0,0.2);
      `;
      el.appendChild(tip);
    });
    el.addEventListener('mouseleave', function () {
      el.querySelectorAll('.tooltip-box').forEach(t => t.remove());
    });
  });
})();


/* ===== 9. SMOOTH SCROLL KE ANCHOR ===== */
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ===== 10. KONFIRMASI SEBELUM HAPUS (fallback) ===== */
document.querySelectorAll('[data-confirm]').forEach(function (el) {
  el.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm || 'Yakin ingin melanjutkan?')) {
      e.preventDefault();
      e.stopPropagation();
    }
  });
});


/* ===== 11. BACK TO TOP ===== */
(function initBackToTop() {
  const btn = document.createElement('button');
  btn.innerHTML    = '↑';
  btn.title        = 'Kembali ke atas';
  btn.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem;
    width:42px; height:42px; border-radius:50%;
    background:#1a73e8; color:#fff; border:none;
    font-size:1.1rem; font-weight:700; cursor:pointer;
    box-shadow:0 4px 12px rgba(0,0,0,0.2);
    opacity:0; transition:opacity 0.3s ease, transform 0.3s ease;
    z-index:50; display:flex; align-items:center; justify-content:center;
  `;

  document.body.appendChild(btn);

  window.addEventListener('scroll', function () {
    if (window.scrollY > 300) {
      btn.style.opacity   = '1';
      btn.style.transform = 'translateY(0)';
    } else {
      btn.style.opacity   = '0';
      btn.style.transform = 'translateY(10px)';
    }
  });

  btn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();