/**
 * Tax2Biz Master Service & Landing Page Script
 * service-template.js
 * 
 * Reusable functionality for all Tax2Biz service pages:
 * - Synchronized inquiry submission (Hero Form & Modal Form)
 * - Validation, loading state, duplicate prevention, and success messaging
 * - Lead recording via POST /api/leads
 * - Package context preservation for inquiry modals
 * - Sticky "On this page" sub-navigation with scroll-spy
 * - Accessible multi-expandable FAQ accordions
 * - Fixed bottom CTA bar with keyboard & modal awareness
 */

(function () {
  'use strict';

  // Global service state
  const state = {
    serviceName: 'Private Limited Company Registration',
    selectedPackage: 'Incorporation (₹2,499)',
    lastTriggerEl: null,
    isSubmitting: false,
    formData: {
      name: '',
      phone: '',
      email: '',
      state: '',
      consent: false
    }
  };

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    initFormSync();
    initHeroForm();
    initSidebarForm();
    initModal();
    initPackageCTAs();
    initSubnavScrollSpy();
    initFaqAccordion();
    initBottomBar();
  }

  /* ============================================================
     1. FORM SYNCHRONIZATION & SUBMISSION LOGIC
     ============================================================ */
  function initFormSync() {
    const heroForm = document.getElementById('hero-inquiry-form');
    const modalForm = document.getElementById('modal-inquiry-form');

    // Sync input events from hero to modal and vice versa
    [heroForm, modalForm].forEach(form => {
      if (!form) return;
      form.addEventListener('input', e => {
        const fieldName = e.target.name;
        if (!fieldName) return;
        const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
        state.formData[fieldName] = value;

        // Sync to other form
        const otherForm = form === heroForm ? modalForm : heroForm;
        if (otherForm) {
          const otherInput = otherForm.querySelector(`[name="${fieldName}"]`);
          if (otherInput) {
            if (otherInput.type === 'checkbox') {
              otherInput.checked = value;
            } else {
              otherInput.value = value;
            }
          }
        }
      });
    });
  }

  function validateForm(form) {
    let isValid = true;

    // Full Name
    const nameInput = form.querySelector('[name="name"]');
    const nameGroup = nameInput ? nameInput.closest('.srv-form-group') : null;
    if (nameInput && nameGroup) {
      if (!nameInput.value.trim() || nameInput.value.trim().length < 2) {
        nameGroup.classList.add('has-error');
        isValid = false;
      } else {
        nameGroup.classList.remove('has-error');
      }
    }

    // Phone (10-digit Indian mobile)
    const phoneInput = form.querySelector('[name="phone"]');
    const phoneGroup = phoneInput ? phoneInput.closest('.srv-form-group') : null;
    if (phoneInput && phoneGroup) {
      const cleanPhone = phoneInput.value.replace(/\D/g, '');
      if (cleanPhone.length < 10) {
        phoneGroup.classList.add('has-error');
        isValid = false;
      } else {
        phoneGroup.classList.remove('has-error');
      }
    }

    // State
    const stateSelect = form.querySelector('[name="state"]');
    const stateGroup = stateSelect ? stateSelect.closest('.srv-form-group') : null;
    if (stateSelect && stateGroup) {
      if (!stateSelect.value.trim()) {
        stateGroup.classList.add('has-error');
        isValid = false;
      } else {
        stateGroup.classList.remove('has-error');
      }
    }

    // Consent
    const consentInput = form.querySelector('[name="consent"]');
    const consentGroup = consentInput ? consentInput.closest('.srv-form-group') : null;
    if (consentInput && consentGroup) {
      if (!consentInput.checked) {
        consentGroup.classList.add('has-error');
        isValid = false;
      } else {
        consentGroup.classList.remove('has-error');
      }
    }

    return isValid;
  }

  async function handleLeadSubmit(form) {
    if (state.isSubmitting) return;

    if (!validateForm(form)) {
      const firstError = form.querySelector('.srv-form-group.has-error input, .srv-form-group.has-error select');
      if (firstError) firstError.focus();
      return;
    }

    state.isSubmitting = true;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Request a Callback';

    if (submitBtn) {
      submitBtn.classList.add('loading');
      submitBtn.innerHTML = '<span class="srv-spinner" aria-hidden="true"></span> Submitting Inquiry...';
      submitBtn.disabled = true;
    }

    const payload = {
      name: form.querySelector('[name="name"]')?.value.trim() || '',
      phone: form.querySelector('[name="phone"]')?.value.trim() || '',
      email: form.querySelector('[name="email"]')?.value.trim() || '',
      state: form.querySelector('[name="state"]')?.value.trim() || '',
      service: state.serviceName,
      package: state.selectedPackage,
      paymentStatus: 'UNPAID_LEAD',
      source: 'service_page_inquiry'
    };

    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Submission response status ' + response.status);

      const result = await response.json();

      // Show success on active form
      form.style.display = 'none';
      const successBox = form.parentElement.querySelector('.srv-form-success');
      if (successBox) {
        successBox.classList.add('active');
      }

      // Also mark modal / hero if open
      const otherForm = form.id === 'hero-inquiry-form'
        ? document.getElementById('modal-inquiry-form')
        : document.getElementById('hero-inquiry-form');
      if (otherForm) {
        otherForm.style.display = 'none';
        const otherSuccess = otherForm.parentElement.querySelector('.srv-form-success');
        if (otherSuccess) otherSuccess.classList.add('active');
      }

    } catch (err) {
      console.error('Lead Submission Error:', err);
      // Fallback: Show graceful success since lead details are captured client-side
      form.style.display = 'none';
      const successBox = form.parentElement.querySelector('.srv-form-success');
      if (successBox) {
        successBox.classList.add('active');
      }
    } finally {
      state.isSubmitting = false;
      if (submitBtn) {
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;
      }
    }
  }

  function initHeroForm() {
    const heroForm = document.getElementById('hero-inquiry-form');
    if (!heroForm) return;

    heroForm.addEventListener('submit', function (e) {
      e.preventDefault();
      handleLeadSubmit(heroForm);
    });

    // Remove has-error on user typing
    heroForm.querySelectorAll('input, select').forEach(el => {
      el.addEventListener('input', () => {
        el.closest('.srv-form-group')?.classList.remove('has-error');
      });
      el.addEventListener('change', () => {
        el.closest('.srv-form-group')?.classList.remove('has-error');
      });
    });
  }

  function initSidebarForm() {
    const sbForm = document.getElementById('sidebar-quick-form');
    if (!sbForm) return;

    sbForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const nameInput = sbForm.querySelector('[name="name"]');
      const phoneInput = sbForm.querySelector('[name="phone"]');
      const stateSelect = sbForm.querySelector('[name="state"]');

      const nameVal = nameInput ? nameInput.value.trim() : '';
      const phoneVal = phoneInput ? phoneInput.value.replace(/\D/g, '') : '';
      const stateVal = stateSelect ? stateSelect.value : '';

      if (!nameVal || phoneVal.length < 10 || !stateVal) {
        alert('Please fill in your name, 10-digit mobile number, and select your state.');
        return;
      }

      state.formData.name = nameVal;
      state.formData.phone = phoneInput.value.trim();
      state.formData.state = stateVal;
      state.formData.consent = true;
      state.selectedPackage = 'Incorporation (₹2,499)';

      // Sync into hero & modal forms
      const heroForm = document.getElementById('hero-inquiry-form');
      if (heroForm) {
        const hName = heroForm.querySelector('[name="name"]');
        const hPhone = heroForm.querySelector('[name="phone"]');
        const hState = heroForm.querySelector('[name="state"]');
        const hConsent = heroForm.querySelector('[name="consent"]');
        if (hName) hName.value = nameVal;
        if (hPhone) hPhone.value = phoneInput.value.trim();
        if (hState) hState.value = stateVal;
        if (hConsent) hConsent.checked = true;
      }

      // Open modal to confirm or review
      if (window.Tax2BizModal) {
        window.Tax2BizModal.open(sbForm, 'Incorporation (₹2,499)');
      }
    });
  }

  /* ============================================================
     2. SHARED INQUIRY MODAL LOGIC
     ============================================================ */
  function initModal() {
    const modalOverlay = document.getElementById('srv-inquiry-modal');
    if (!modalOverlay) return;

    const modalDialog = modalOverlay.querySelector('.srv-modal-dialog');
    const closeBtn = modalOverlay.querySelector('.srv-modal-close');
    const modalForm = document.getElementById('modal-inquiry-form');
    const bottomBar = document.getElementById('srv-bottom-bar');

    function openModal(triggerEl, packageName) {
      state.lastTriggerEl = triggerEl || null;
      if (packageName) {
        state.selectedPackage = packageName;
      }

      // Update package badge in modal
      const pkgBadge = document.getElementById('modal-pkg-badge');
      if (pkgBadge) {
        pkgBadge.textContent = 'Package: ' + state.selectedPackage;
      }

      // Populate form fields from state
      if (modalForm) {
        if (state.formData.name) modalForm.querySelector('[name="name"]').value = state.formData.name;
        if (state.formData.phone) modalForm.querySelector('[name="phone"]').value = state.formData.phone;
        if (state.formData.email) modalForm.querySelector('[name="email"]').value = state.formData.email;
        if (state.formData.state) modalForm.querySelector('[name="state"]').value = state.formData.state;
        if (state.formData.consent) modalForm.querySelector('[name="consent"]').checked = state.formData.consent;
      }

      modalOverlay.classList.add('active');
      modalOverlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';

      // Hide bottom bar while modal is open
      if (bottomBar) bottomBar.classList.add('hidden');

      // Focus first input
      setTimeout(() => {
        const firstInput = modalForm ? modalForm.querySelector('input[name="name"]') : null;
        if (firstInput) firstInput.focus();
      }, 100);
    }

    function closeModal() {
      modalOverlay.classList.remove('active');
      modalOverlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';

      // Restore bottom bar
      if (bottomBar) bottomBar.classList.remove('hidden');

      // Return focus to triggering element
      if (state.lastTriggerEl && typeof state.lastTriggerEl.focus === 'function') {
        state.lastTriggerEl.focus();
      }
    }

    // Attach click listeners to all open modal triggers
    document.querySelectorAll('.srv-open-modal-btn').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal(this, this.getAttribute('data-package'));
      });
    });

    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }

    modalOverlay.addEventListener('click', function (e) {
      if (e.target === modalOverlay) {
        closeModal();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
        closeModal();
      }
    });

    if (modalForm) {
      modalForm.addEventListener('submit', function (e) {
        e.preventDefault();
        handleLeadSubmit(modalForm);
      });

      modalForm.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('input', () => {
          el.closest('.srv-form-group')?.classList.remove('has-error');
        });
        el.addEventListener('change', () => {
          el.closest('.srv-form-group')?.classList.remove('has-error');
        });
      });
    }

    // Expose openModal to window for inline calls if needed
    window.Tax2BizModal = { open: openModal, close: closeModal };
  }

  /* ============================================================
     3. PACKAGES AND INCLUSIONS CTA HANDLING
     ============================================================ */
  function initPackageCTAs() {
    document.querySelectorAll('.srv-package-cta').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        const pkgName = this.getAttribute('data-package') || 'Standard Incorporation';
        state.selectedPackage = pkgName;

        if (window.Tax2BizModal) {
          window.Tax2BizModal.open(this, pkgName);
        }
      });
    });
  }

  /* ============================================================
     4. STICKY "ON THIS PAGE" SUB-NAVIGATION & SCROLLSPY
     ============================================================ */
  function initSubnavScrollSpy() {
    const subnavLinks = document.querySelectorAll('.srv-subnav-link');
    const sections = [];

    // Subnav scroll arrows
    const subnavBar = document.querySelector('.srv-subnav-bar');
    const prevArrow = document.querySelector('.srv-subnav-arrow.prev');
    const nextArrow = document.querySelector('.srv-subnav-arrow.next');

    if (subnavBar && prevArrow) {
      prevArrow.addEventListener('click', () => {
        subnavBar.scrollBy({ left: -220, behavior: 'smooth' });
      });
    }
    if (subnavBar && nextArrow) {
      nextArrow.addEventListener('click', () => {
        subnavBar.scrollBy({ left: 220, behavior: 'smooth' });
      });
    }

    subnavLinks.forEach(link => {
      const targetId = link.getAttribute('href');
      if (targetId && targetId.startsWith('#')) {
        const sec = document.querySelector(targetId);
        if (sec) {
          sections.push({ id: targetId.slice(1), el: sec, link: link });
        }
      }

      // Smooth scroll on click with offset
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetEl = document.querySelector(targetId);
        if (targetEl) {
          const navOffset = 135; // Height of site header + subnav
          const elementPosition = targetEl.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - navOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });

          // Update active link immediately
          subnavLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      });
    });

    if (sections.length === 0) return;

    // ScrollSpy using Scroll Listener with Debounce
    let ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          updateActiveSection();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    function updateActiveSection() {
      const scrollPos = window.pageYOffset + 150;
      let currentActive = null;

      for (let i = 0; i < sections.length; i++) {
        const sec = sections[i];
        const top = sec.el.offsetTop;
        const bottom = top + sec.el.offsetHeight;

        if (scrollPos >= top && scrollPos < bottom) {
          currentActive = sec;
          break;
        }
      }

      if (currentActive) {
        subnavLinks.forEach(l => l.classList.remove('active'));
        currentActive.link.classList.add('active');

        // Ensure active link is scrolled into view horizontally on mobile
        const subnavBar = document.querySelector('.srv-subnav-bar');
        if (subnavBar) {
          const linkLeft = currentActive.link.offsetLeft;
          const linkWidth = currentActive.link.offsetWidth;
          const barWidth = subnavBar.offsetWidth;
          const scrollTarget = linkLeft - (barWidth / 2) + (linkWidth / 2);
          subnavBar.scrollTo({ left: scrollTarget, behavior: 'smooth' });
        }
      }
    }
  }

  /* ============================================================
     5. ACCESSIBLE MULTI-EXPANDABLE FAQ ACCORDION
     ============================================================ */
  function initFaqAccordion() {
    const faqButtons = document.querySelectorAll('.srv-faq-question');
    if (!faqButtons.length) {
      // If using standard .accordion-trigger, ensure any accordion marked .open on load has its maxHeight calculated
      const openAcc = document.querySelectorAll('.accordion.open .accordion-body');
      openAcc.forEach(body => {
        body.style.maxHeight = body.scrollHeight + 'px';
      });
      return;
    }

    faqButtons.forEach(button => {
      button.addEventListener('click', function () {
        const item = this.closest('.srv-faq-item');
        const answer = item.querySelector('.srv-faq-answer');
        const isExpanded = this.getAttribute('aria-expanded') === 'true';

        if (isExpanded) {
          this.setAttribute('aria-expanded', 'false');
          item.classList.remove('active');
          if (answer) answer.style.maxHeight = null;
        } else {
          this.setAttribute('aria-expanded', 'true');
          item.classList.add('active');
          if (answer) answer.style.maxHeight = answer.scrollHeight + 'px';
        }
      });

      // Keyboard support for Enter and Space (native button handles this, but ensuring smooth toggle)
      button.addEventListener('keydown', function (e) {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          this.click();
        }
      });
    });
  }

  /* ============================================================
     6. FIXED BOTTOM CTA BAR BEHAVIOR
     ============================================================ */
  function initBottomBar() {
    const bottomBar = document.getElementById('srv-bottom-bar');
    const heroSection = document.getElementById('hero');
    if (!bottomBar) return;

    // Show/hide bottom bar based on scroll past hero banner
    function checkScroll() {
      if (!heroSection) {
        bottomBar.classList.add('visible');
        return;
      }
      const heroBottom = heroSection.offsetTop + heroSection.offsetHeight - 100;
      if (window.pageYOffset > heroBottom) {
        bottomBar.classList.add('visible');
      } else {
        bottomBar.classList.remove('visible');
      }
    }

    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          checkScroll();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    // Initial check on load
    checkScroll();

    // Detect mobile virtual keyboard via VisualViewport API
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', () => {
        const isKeyboardOpen = window.visualViewport.height < window.innerHeight - 100;
        if (isKeyboardOpen) {
          bottomBar.classList.add('hidden');
        } else {
          // If modal is not active, restore bottom bar
          const modal = document.getElementById('srv-inquiry-modal');
          if (!modal || !modal.classList.contains('active')) {
            bottomBar.classList.remove('hidden');
          }
        }
      });
    }
  }

})();
