/**
 * Tax2Biz — Main JavaScript
 * Handles: sticky header, nav mega-menus, mobile drawer, service tabs,
 *          lifecycle interactive, FAQ accordion, smooth-scroll, scroll-reveal.
 */

(function () {
  'use strict';

  /* ── Helpers ─────────────────────────────────────── */
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  /* ── Sticky header shadow ─────────────────────────── */
  const header = $('.header');
  const onScroll = () => {
    header.classList.toggle('scrolled', window.scrollY > 12);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── Mobile Drawer ────────────────────────────────── */
  const toggle = $('.mobile-toggle');
  const drawer = $('.mobile-drawer');
  const toggleIcon = toggle && toggle.querySelector('i');

  if (toggle && drawer) {
    toggle.addEventListener('click', () => {
      const isOpen = drawer.classList.toggle('open');
      if (toggleIcon) {
        toggleIcon.className = isOpen ? 'ph ph-x' : 'ph ph-list';
      }
      document.body.style.overflow = isOpen ? 'hidden' : '';
      toggle.setAttribute('aria-expanded', isOpen);
    });

    // Close button inside drawer
    const drawerClose = $('.drawer-close');
    if (drawerClose) {
      drawerClose.addEventListener('click', () => {
        drawer.classList.remove('open');
        if (toggleIcon) toggleIcon.className = 'ph ph-list';
        document.body.style.overflow = '';
        toggle.setAttribute('aria-expanded', 'false');
      });
    }

    // Close on outside tap (overlay area)
    document.addEventListener('click', (e) => {
      if (
        drawer.classList.contains('open') &&
        !drawer.contains(e.target) &&
        !toggle.contains(e.target)
      ) {
        drawer.classList.remove('open');
        if (toggleIcon) toggleIcon.className = 'ph ph-list';
        document.body.style.overflow = '';
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Auto-close on viewport resize to desktop width
    window.addEventListener('resize', () => {
      if (window.innerWidth > 1140 && drawer.classList.contains('open')) {
        drawer.classList.remove('open');
        if (toggleIcon) toggleIcon.className = 'ph ph-list';
        document.body.style.overflow = '';
        toggle.setAttribute('aria-expanded', 'false');
      }
    }, { passive: true });
  }

  /* ── Drawer Sub-Accordion ─────────────────────────── */
  $$('.drawer-trigger').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const sub = btn.nextElementSibling;
      if (!sub) return; // For links like Pricing that don't have a sub-menu
      const isOpen = sub.classList.toggle('open');
      btn.classList.toggle('open', isOpen);
      btn.setAttribute('aria-expanded', isOpen);
    });
  });

  /* ── Hero Service Tabs ──────────────────────────────── */
  const hstTabs = $$('.hst-tab');
  hstTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      hstTabs.forEach((t) => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      const target = tab.dataset.hst;
      $$('.hst-panel').forEach((p) => {
        p.hidden = true;
        p.classList.remove('active');
      });
      const panel = $('#hst-panel-' + target);
      if (panel) {
        panel.hidden = false;
        panel.classList.add('active');
      }
    });
  });


  /* ── FAQ Accordion ────────────────────────────────── */
  $$('.accordion-trigger').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const accordion = trigger.closest('.accordion');
      if (!accordion) return;
      const body = accordion.querySelector('.accordion-body');
      if (!body) return;
      const isOpen = accordion.classList.contains('open');

      // Close all others
      $$('.accordion.open').forEach((a) => {
        if (a !== accordion) {
          a.classList.remove('open');
          const t = a.querySelector('.accordion-trigger');
          if (t) t.setAttribute('aria-expanded', 'false');
          const b = a.querySelector('.accordion-body');
          if (b) b.style.maxHeight = null;
        }
      });

      // Toggle current
      if (isOpen) {
        accordion.classList.remove('open');
        trigger.setAttribute('aria-expanded', 'false');
        body.style.maxHeight = null;
      } else {
        accordion.classList.add('open');
        trigger.setAttribute('aria-expanded', 'true');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    });
  });

  /* ── Scroll Reveal (Intersection Observer) ────────── */
  const reveals = $$('[data-reveal]');
  if (reveals.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('revealed'));
  }

  /* ── Smooth Anchor Scroll (Universal) ─────────────── */
  $$('a[href^="#"], a[href*="index.html#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const rawHref = anchor.getAttribute('href');
      const hashIndex = rawHref.indexOf('#');
      if (hashIndex === -1) return;
      const id = rawHref.substring(hashIndex);
      if (id === '#' || !id) return;

      const currentFile = window.location.pathname.split('/').pop() || 'index.html';
      const isHome = currentFile === 'index.html' || currentFile === '' || currentFile === '/';

      if (isHome || rawHref.startsWith('#')) {
        const target = $(id);
        if (!target) return;
        e.preventDefault();
        const offset = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h') || '76', 10);
        const top = target.getBoundingClientRect().top + window.scrollY - offset - 16;
        window.scrollTo({ top, behavior: 'smooth' });

        if (history.pushState) {
          history.pushState(null, null, id);
        }

        // Close mobile drawer if open
        if (drawer && drawer.classList.contains('open')) {
          drawer.classList.remove('open');
          if (toggleIcon) toggleIcon.className = 'ph ph-list';
          document.body.style.overflow = '';
        }
      }
    });
  });

  /* ── Keyboard: close mega-menus with Escape ──────── */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (drawer && drawer.classList.contains('open')) {
        drawer.classList.remove('open');
        if (toggleIcon) toggleIcon.className = 'ph ph-list';
        document.body.style.overflow = '';
      }
    }
  });

  /* ── Expert Modal Popup ────────────────────────────── */
  const expertBtns = $$('.hire-expert-trigger, #hire-expert-btn');
  const expertModal = $('#expert-modal');
  const modalClose = $('#modal-close-btn');

  if (expertModal) {
    const openModal = () => {
      expertModal.classList.add('active');
      document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
      expertModal.classList.remove('active');
      document.body.style.overflow = '';
    };

    expertBtns.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
      });
    });

    if (modalClose) {
      modalClose.addEventListener('click', closeModal);
    }

    // Close on outside click
    expertModal.addEventListener('click', (e) => {
      if (e.target === expertModal) {
        closeModal();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && expertModal.classList.contains('active')) {
        closeModal();
      }
    });

    // Prevent form submission for demo
    const expertForm = $('#expert-form');
    if (expertForm) {
      expertForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Thank you! An expert will contact you shortly.');
        closeModal();
      });
    }
  }

  /* ── How It Works Vertical Flow Observer ─────────── */
  const vSteps = $$('.v-step-card');
  const vProgress = $('.v-flow-line-progress');
  if (vSteps.length && 'IntersectionObserver' in window) {
    const vObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('active');
            const activeIdx = vSteps.indexOf(entry.target);
            if (vProgress && activeIdx >= 0) {
              const pct = Math.round(((activeIdx + 1) / vSteps.length) * 100);
              vProgress.style.height = pct + '%';
            }
          }
        });
      },
      { threshold: 0.3 }
    );
    vSteps.forEach((step) => vObserver.observe(step));
  }

})();

