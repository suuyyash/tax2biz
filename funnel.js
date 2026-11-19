/**
 * Tax2Biz Onboarding & Checkout Funnel Engine
 * funnel.js
 * 
 * Handles:
 * 1. OTP Verification Modal (non-scrollable, non-closeable except Cancel)
 * 2. Plan Selection state & pricing logic
 * 3. Interactive Demo Payment processing
 * 4. Thank You & Assigned CA Dynamic Population
 */

(function () {
  'use strict';

  // State keys
  const STORAGE_KEY = 'tax2biz_lead_session';
  const DEMO_OTP = '123456';

  // Utility to get current lead state
  function getLeadData() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return {
      name: 'Rahul Sharma',
      phone: '9876543210',
      email: 'rahul.sharma@example.com',
      state: 'Maharashtra',
      planId: 'plan_standard',
      planName: 'Incorporation Only',
      planPrice: 2499,
      originalPrice: 4999,
      isVerified: false
    };
  }

  function saveLeadData(data) {
    try {
      const current = getLeadData();
      const updated = { ...current, ...data };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    } catch (e) {
      return data;
    }
  }

  /* ============================================================
     1. OTP MODAL INITIALIZATION (Used on Service/Product pages)
     ============================================================ */
  window.Tax2BizFunnel = {
    openOtpModal: function (formData) {
      if (formData) {
        saveLeadData(formData);
      }
      const modal = document.getElementById('t2b-otp-modal');
      if (!modal) return;

      const lead = getLeadData();
      const phoneDisplay = document.getElementById('t2b-otp-phone-display');
      if (phoneDisplay) {
        phoneDisplay.textContent = `+91 ${lead.phone || '98765 43210'}`;
      }

      // Lock body scroll
      document.body.classList.add('t2b-modal-open');
      modal.classList.add('active');
      modal.setAttribute('aria-hidden', 'false');

      // Reset OTP inputs
      const inputs = modal.querySelectorAll('.t2b-otp-digit');
      inputs.forEach(input => {
        input.value = '';
        input.classList.remove('has-value');
      });
      const errorMsg = document.getElementById('t2b-otp-error');
      if (errorMsg) errorMsg.style.display = 'none';

      // Focus first input
      setTimeout(() => {
        if (inputs[0]) inputs[0].focus();
      }, 100);

      // Start Resend Timer
      startOtpTimer();
    },

    closeOtpModal: function () {
      const modal = document.getElementById('t2b-otp-modal');
      if (!modal) return;
      document.body.classList.remove('t2b-modal-open');
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
    }
  };

  let otpTimerInterval = null;
  function startOtpTimer() {
    const countdownEl = document.getElementById('t2b-otp-countdown');
    const resendBtn = document.getElementById('t2b-otp-resend-btn');
    const timerText = document.getElementById('t2b-otp-timer-text');
    if (!countdownEl || !resendBtn) return;

    if (otpTimerInterval) clearInterval(otpTimerInterval);

    let timeLeft = 29;
    resendBtn.disabled = true;
    if (timerText) timerText.style.display = 'inline';

    otpTimerInterval = setInterval(() => {
      timeLeft--;
      countdownEl.textContent = `0:${timeLeft < 10 ? '0' : ''}${timeLeft}`;
      if (timeLeft <= 0) {
        clearInterval(otpTimerInterval);
        resendBtn.disabled = false;
        if (timerText) timerText.style.display = 'none';
      }
    }, 1000);
  }

  function initOtpModalInteractions() {
    const modal = document.getElementById('t2b-otp-modal');
    if (!modal) return;

    // Prevent backdrop clicks from closing the modal (strictly non-closeable by outside click)
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        e.stopPropagation();
        e.preventDefault();
        // Shake modal gently to indicate it cannot be dismissed by clicking outside
        const card = modal.querySelector('.t2b-otp-card');
        if (card) {
          card.style.transform = 'scale(1.02)';
          setTimeout(() => { card.style.transform = ''; }, 150);
        }
      }
    });

    // Prevent ESC key from closing
    document.addEventListener('keydown', function (e) {
      if (modal.classList.contains('active') && e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
      }
    });

    // Small Cancel button: the only way to return to editing form
    const cancelBtn = document.getElementById('t2b-otp-cancel-btn');
    const editBtn = document.getElementById('t2b-otp-edit-phone');
    [cancelBtn, editBtn].forEach(btn => {
      if (btn) {
        btn.addEventListener('click', function (e) {
          e.preventDefault();
          window.Tax2BizFunnel.closeOtpModal();
          const phoneInput = document.getElementById('hero-phone') || document.getElementById('modal-phone');
          if (phoneInput) phoneInput.focus();
        });
      }
    });

    // Auto-fill demo button
    const autofillBtn = document.getElementById('t2b-autofill-otp');
    if (autofillBtn) {
      autofillBtn.addEventListener('click', function () {
        fillOtpDigits(DEMO_OTP);
      });
    }

    // Digit inputs handling (Auto-focus next, backspace, paste)
    const inputs = modal.querySelectorAll('.t2b-otp-digit');
    inputs.forEach((input, index) => {
      input.addEventListener('input', function (e) {
        const val = this.value.replace(/\D/g, '');
        this.value = val ? val[val.length - 1] : '';

        if (this.value) {
          this.classList.add('has-value');
          if (index < inputs.length - 1) {
            inputs[index + 1].focus();
          }
        } else {
          this.classList.remove('has-value');
        }

        // Auto submit if all 6 digits entered
        checkAndTriggerOtpSubmit();
      });

      input.addEventListener('keydown', function (e) {
        if (e.key === 'Backspace' && !this.value && index > 0) {
          inputs[index - 1].focus();
        }
      });

      input.addEventListener('paste', function (e) {
        e.preventDefault();
        const pasteData = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
        if (pasteData) {
          fillOtpDigits(pasteData.slice(0, 6));
        }
      });
    });

    function fillOtpDigits(code) {
      const chars = code.split('');
      inputs.forEach((input, i) => {
        if (chars[i]) {
          input.value = chars[i];
          input.classList.add('has-value');
        } else {
          input.value = '';
          input.classList.remove('has-value');
        }
      });
      if (chars.length >= 6) {
        inputs[5].focus();
        checkAndTriggerOtpSubmit();
      } else if (inputs[chars.length]) {
        inputs[chars.length].focus();
      }
    }

    function checkAndTriggerOtpSubmit() {
      let code = '';
      inputs.forEach(inp => code += inp.value);
      if (code.length === 6) {
        handleOtpVerification(code);
      }
    }

    // Form submit button
    const otpForm = document.getElementById('t2b-otp-form');
    if (otpForm) {
      otpForm.addEventListener('submit', function (e) {
        e.preventDefault();
        let code = '';
        inputs.forEach(inp => code += inp.value);
        if (code.length < 6) {
          const errorMsg = document.getElementById('t2b-otp-error');
          if (errorMsg) {
            errorMsg.textContent = 'Please enter all 6 digits to verify.';
            errorMsg.style.display = 'block';
          }
          return;
        }
        handleOtpVerification(code);
      });
    }

    function handleOtpVerification(code) {
      const submitBtn = document.getElementById('t2b-otp-submit-btn');
      const errorMsg = document.getElementById('t2b-otp-error');
      if (errorMsg) errorMsg.style.display = 'none';

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="srv-spinner" aria-hidden="true"></span> Verifying Code...';
      }

      setTimeout(() => {
        // Accept demo OTP or any 6-digit number in test mode
        saveLeadData({ isVerified: true, verifiedOtp: code });

        if (submitBtn) {
          submitBtn.innerHTML = '<i class="ph-bold ph-check-circle"></i> Phone Verified! Redirecting...';
          submitBtn.style.background = '#059669';
        }

        setTimeout(() => {
          window.location.href = 'registration-plan-select.html';
        }, 500);
      }, 700);
    }
  }

  /* ============================================================
     2. PLAN SELECTION PAGE LOGIC (registration-plan-select.html)
     ============================================================ */
  function initPlanSelectionPage() {
    const plansWrap = document.querySelector('.t2b-plans-selection-section');
    if (!plansWrap) return;

    const lead = getLeadData();

    // Populate Applicant Info Card
    const nameEl = document.getElementById('lead-name-display');
    const phoneEl = document.getElementById('lead-phone-display');
    const emailEl = document.getElementById('lead-email-display');
    const stateEl = document.getElementById('lead-state-display');

    if (nameEl) nameEl.textContent = lead.name || 'Rahul Sharma';
    if (phoneEl) phoneEl.textContent = `+91 ${lead.phone || '98765 43210'}`;
    if (emailEl) emailEl.textContent = lead.email || 'rahul.sharma@example.com';
    if (stateEl) stateEl.textContent = lead.state || 'Maharashtra';

    // Plan Cards Selection
    const planCards = document.querySelectorAll('.t2b-plan-card');
    const summaryPlanName = document.getElementById('t2b-summary-plan-name');
    const summaryPlanPrice = document.getElementById('t2b-summary-plan-price');
    const proceedBtn = document.getElementById('t2b-proceed-to-pay-btn');

    let currentPlan = {
      planId: lead.planId || 'plan_standard',
      planName: lead.planName || 'Incorporation Only',
      planPrice: lead.planPrice || 2499,
      originalPrice: lead.originalPrice || 4999
    };

    function updatePlanSelection(card) {
      planCards.forEach(c => {
        c.classList.remove('selected');
        const btn = c.querySelector('.t2b-card-select-btn');
        if (btn) btn.textContent = 'Select Plan';
      });
      card.classList.add('selected');

      const planId = card.getAttribute('data-plan-id');
      const planName = card.getAttribute('data-plan-name');
      const planPrice = parseInt(card.getAttribute('data-plan-price'), 10);
      const originalPrice = parseInt(card.getAttribute('data-original-price'), 10);

      const selBtn = card.querySelector('.t2b-card-select-btn');
      if (selBtn) selBtn.textContent = 'Selected Plan ✓';

      currentPlan = { planId: planId, planName: planName, planPrice: planPrice, originalPrice: originalPrice };
      saveLeadData({
        planId: planId,
        planName: planName,
        planPrice: planPrice,
        originalPrice: originalPrice
      });

      if (summaryPlanName) summaryPlanName.textContent = planName;
      if (summaryPlanPrice) summaryPlanPrice.textContent = `₹${planPrice.toLocaleString('en-IN')}`;
    }

    // Deliverables dropdown toggle
    document.querySelectorAll('.t2b-deliverables-toggle').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        const card = this.closest('.t2b-plan-card');
        const dropdown = card.querySelector('.t2b-deliverables-dropdown');
        if (!dropdown) return;

        const isOpen = dropdown.classList.contains('open');
        if (isOpen) {
          dropdown.classList.remove('open');
          this.classList.remove('active');
          this.setAttribute('aria-expanded', 'false');
          const span = this.querySelector('span');
          if (span) span.textContent = span.textContent.replace('Hide', 'View');
        } else {
          dropdown.classList.add('open');
          this.classList.add('active');
          this.setAttribute('aria-expanded', 'true');
          const span = this.querySelector('span');
          if (span) span.textContent = span.textContent.replace('View', 'Hide');
        }
      });
    });

    planCards.forEach(card => {
      card.addEventListener('click', function () {
        updatePlanSelection(this);
      });
    });

    if (proceedBtn) {
      proceedBtn.addEventListener('click', function () {
        saveLeadData(currentPlan);
        window.location.href = 'payment-checkout.html';
      });
    }
  }

  /* ============================================================
     3. DEMO PAYMENT CHECKOUT LOGIC (payment-checkout.html)
     ============================================================ */
  function initCheckoutPaymentPage() {
    const checkoutWrap = document.querySelector('.t2b-checkout-wrap');
    if (!checkoutWrap) return;

    const lead = getLeadData();

    // Populate summary
    const summaryPlanName = document.getElementById('checkout-plan-name');
    const summaryOrgPrice = document.getElementById('checkout-orig-price');
    const summaryDiscAmount = document.getElementById('checkout-disc-amount');
    const summaryTotalAmount = document.getElementById('checkout-total-amount');
    const payBtnAmount = document.getElementById('checkout-pay-btn-amount');
    const clientNameDisplay = document.getElementById('checkout-client-name');
    const clientPhoneDisplay = document.getElementById('checkout-client-phone');

    const price = lead.planPrice || 2499;
    const origPrice = lead.originalPrice || 4999;
    const discount = origPrice - price;

    if (summaryPlanName) summaryPlanName.textContent = lead.planName || 'Private Limited Company Registration';
    if (summaryOrgPrice) summaryOrgPrice.textContent = `₹${origPrice.toLocaleString('en-IN')}`;
    if (summaryDiscAmount) summaryDiscAmount.textContent = `-₹${discount.toLocaleString('en-IN')}`;
    if (summaryTotalAmount) summaryTotalAmount.textContent = `₹${price.toLocaleString('en-IN')}`;
    if (payBtnAmount) payBtnAmount.textContent = `₹${price.toLocaleString('en-IN')}`;
    if (clientNameDisplay) clientNameDisplay.textContent = lead.name || 'Rahul Sharma';
    if (clientPhoneDisplay) clientPhoneDisplay.textContent = `+91 ${lead.phone || '98765 43210'}`;

    // Tabs switching
    const tabs = document.querySelectorAll('.t2b-pay-tab');
    const panels = document.querySelectorAll('.t2b-tab-panel');

    tabs.forEach(tab => {
      tab.addEventListener('click', function () {
        const targetId = this.getAttribute('data-target');
        tabs.forEach(t => t.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));
        this.classList.add('active');
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.classList.add('active');
      });
    });

    // UPI App buttons
    const appBtns = document.querySelectorAll('.t2b-upi-app-btn');
    appBtns.forEach(btn => {
      btn.addEventListener('click', function () {
        appBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      });
    });

    // Process Demo Payment
    const payBtn = document.getElementById('checkout-pay-now-btn');
    if (payBtn) {
      payBtn.addEventListener('click', function () {
        if (this.disabled) return;
        this.disabled = true;

        const originalText = this.innerHTML;
        this.innerHTML = '<span class="srv-spinner" aria-hidden="true"></span> Processing Secure Demo Payment...';

        setTimeout(() => {
          this.innerHTML = '<span class="srv-spinner" aria-hidden="true"></span> Authorizing with Banking Gateway...';
          setTimeout(() => {
            this.innerHTML = '<i class="ph-bold ph-check-circle"></i> Payment Approved! Generating CA Docket...';
            this.style.background = '#059669';

            const orderId = `TXB-INCORP-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`;
            saveLeadData({
              orderId: orderId,
              paymentStatus: 'PAID',
              paidAmount: price,
              paidAt: new Date().toISOString()
            });

            // Also post to backend leads endpoint if available
            fetch('/api/leads', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name: lead.name,
                phone: lead.phone,
                email: lead.email,
                state: lead.state,
                service: 'Private Limited Company Registration',
                package: lead.planName,
                amount: price,
                paymentStatus: 'PAID',
                orderId: orderId,
                source: 'checkout_demo_flow'
              })
            }).catch(() => {});

            setTimeout(() => {
              window.location.href = 'registration-success.html';
            }, 800);
          }, 900);
        }, 1000);
      });
    }
  }

  /* ============================================================
     4. THANK YOU & ASSIGNED CA PAGE (registration-success.html)
     ============================================================ */
  function initSuccessThankYouPage() {
    const successWrap = document.querySelector('.t2b-thankyou-wrap, .t2b-success-wrap');
    if (!successWrap) return;

    const lead = getLeadData();

    // Populate order info
    const orderIdEl = document.getElementById('success-order-id');
    const customerNameEl = document.getElementById('success-customer-name');
    const customerPhoneEl = document.getElementById('success-customer-phone');
    const urgentPhoneEl = document.getElementById('success-urgent-phone');
    const planNameEl = document.getElementById('success-plan-name');
    const amountPaidEl = document.getElementById('success-amount-paid');

    const orderId = lead.orderId || `TXB-INCORP-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    const clientName = lead.name || 'Rahul Sharma';
    const clientPhone = lead.phone || '98765 43210';
    const planName = lead.planName || 'Private Limited Company Registration';
    const price = lead.planPrice || 2499;
    const origPrice = lead.originalPrice || (price === 14999 ? 19999 : 4999);
    const savings = origPrice - price;

    if (orderIdEl) orderIdEl.textContent = orderId;
    if (customerNameEl) customerNameEl.textContent = clientName;
    if (customerPhoneEl) customerPhoneEl.textContent = `+91 ${clientPhone}`;
    if (urgentPhoneEl) urgentPhoneEl.textContent = `+91 ${clientPhone}`;
    if (planNameEl) planNameEl.textContent = planName;
    if (amountPaidEl) amountPaidEl.textContent = `₹${price.toLocaleString('en-IN')}`;

    const step1AmountEl = document.getElementById('success-step1-amount');
    if (step1AmountEl) step1AmountEl.textContent = `₹${price.toLocaleString('en-IN')}`;

    const docketPriceEl = document.getElementById('success-docket-price');
    if (docketPriceEl) {
      if (savings > 0) {
        docketPriceEl.textContent = `₹${price.toLocaleString('en-IN')} (Special Offer · Save ₹${savings.toLocaleString('en-IN')})`;
      } else {
        docketPriceEl.textContent = `₹${price.toLocaleString('en-IN')}`;
      }
    }

    // Download invoice simulation
    const downloadBtn = document.getElementById('t2b-download-receipt-btn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', function () {
        window.print();
      });
    }
  }

  // Auto-run on DOMContentLoaded based on current page
  document.addEventListener('DOMContentLoaded', function () {
    initOtpModalInteractions();
    initPlanSelectionPage();
    initCheckoutPaymentPage();
    initSuccessThankYouPage();
  });

})();
