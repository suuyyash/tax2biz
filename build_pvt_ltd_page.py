import re

with open('index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Extract Universal Header (exact bytes)
h_start = idx_content.find('<header')
h_end = idx_content.find('</header>') + len('</header>')
universal_header = idx_content[h_start:h_end]

# Extract Universal Drawer (exact bytes between </header> and <main)
m_start = idx_content.find('<main')
universal_drawer = idx_content[h_end:m_start]

# Extract Universal Footer (exact bytes)
f_start = idx_content.find('<footer')
f_end = idx_content.find('</footer>') + len('</footer>')
universal_footer = idx_content[f_start:f_end]

# Extract Expert Modal
em_start = idx_content.find('<div class="modal-overlay" id="expert-modal"')
script_idx = idx_content.find('<script', em_start)
expert_modal = idx_content[em_start:script_idx].strip()

# Head content
head_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Private Limited Company Registration Online (SPICe+) | Tax2Biz India</title>
  <meta name="description" content="Register your Private Limited Company in 10-12 days with Tax2Biz. 100% online MCA V3 filing, ₹0 MCA government fees up to ₹15 Lakhs capital. 2 Class 3 DSC, DIN, MOA/AOA, PAN, TAN & Current Account included." />
  <meta name="keywords" content="private limited company registration, pvt ltd incorporation online, spice+ filing, company registration fees india, mca company registration, dsc din pan tan" />
  
  <!-- Open Graph / Meta -->
  <meta property="og:title" content="Private Limited Company Registration Online | Tax2Biz" />
  <meta property="og:description" content="End-to-end company incorporation handled by senior CAs & Lawyers. Transparent cost breakdown with live stamp duty calculator." />
  <meta property="og:type" content="website" />
  
  <!-- Fonts & Phosphor Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <script src="https://unpkg.com/@phosphor-icons/web@2.0.3"></script>

  <!-- Stylesheets -->
  <link rel="stylesheet" href="styles.css" />
  <link rel="stylesheet" href="services.css" />
</head>
<body class="srv-page">
"""

# Main Content
main_content = """<main id="main" role="main">

  <!-- ============================================================
       1. HERO SECTION: VALUE PROPOSITION & STICKY BOOKING CARD
       ============================================================ -->
  <section class="srv-hero-section">
    <div class="container">
      
      <!-- Breadcrumb -->
      <nav class="srv-breadcrumb" aria-label="Breadcrumb">
        <a href="index.html">Home</a>
        <i class="ph-bold ph-caret-right" aria-hidden="true"></i>
        <span>Business Registration</span>
        <i class="ph-bold ph-caret-right" aria-hidden="true"></i>
        <span aria-current="page">Private Limited Company Registration</span>
      </nav>

      <div class="srv-hero-grid">
        
        <!-- Hero Left: Value Proposition -->
        <div class="srv-hero-left">
          
          <div class="srv-trust-tag">
            <span class="srv-trust-stars">
              <i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i>
            </span>
            <span>4.9/5 (14,200+ Startups Incorporated)</span>
            <span class="srv-trust-divider">|</span>
            <span class="srv-trust-govt"><i class="ph-bold ph-shield-check"></i> MCA V3 Portal Certified</span>
          </div>

          <h1 class="srv-hero-title">
            Register Your <span class="highlight-green">Private Limited Company</span> Online in 10-12 Days
          </h1>

          <p class="srv-hero-subtitle">
            India's most trusted corporate legal platform. Handled 100% online by experienced CAs and Corporate Lawyers with <strong>₹0 MCA government filing fee</strong> for capital up to ₹15 Lakhs. Class 3 DSC, DIN, MOA/AOA, PAN, TAN &amp; zero-balance bank account included.
          </p>

          <div class="srv-hero-bullets">
            <div class="srv-bullet-item">
              <div class="srv-bullet-icon"><i class="ph-bold ph-check"></i></div>
              <span><strong>Zero MCA Gov Filing Fee</strong> under SPICe+ waiver scheme (Authorized capital &le; ₹15L)</span>
            </div>
            <div class="srv-bullet-item">
              <div class="srv-bullet-icon"><i class="ph-bold ph-check"></i></div>
              <span><strong>2x Class 3 Digital Signatures (DSC) + 2x DIN</strong> for proposed directors included</span>
            </div>
            <div class="srv-bullet-item">
              <div class="srv-bullet-icon"><i class="ph-bold ph-check"></i></div>
              <span><strong>Same-Day Name Reservation Filing</strong> via RUN / SPICe+ Part A with 2 attempts</span>
            </div>
            <div class="srv-bullet-item">
              <div class="srv-bullet-icon"><i class="ph-bold ph-check"></i></div>
              <span><strong>Dedicated Senior CA &amp; Legal Manager</strong> assigned from Day 1 to incorporation</span>
            </div>
          </div>

          <div class="srv-authority-badges">
            <div class="srv-auth-item">
              <i class="ph-bold ph-buildings"></i>
              <span>Official MCA V3 e-Filing Partner</span>
            </div>
            <div class="srv-auth-item">
              <i class="ph-bold ph-rocket-launch"></i>
              <span>Startup India Facilitator</span>
            </div>
            <div class="srv-auth-item">
              <i class="ph-bold ph-lock-key"></i>
              <span>ISO 27001 Data Security</span>
            </div>
          </div>

        </div>

        <!-- Hero Right: High-Converting Booking & Lead Capture Card -->
        <div class="srv-hero-right">
          <div class="srv-hero-form-card">
            
            <div class="srv-form-header">
              <span class="srv-form-badge">ONLINE INCORPORATION 2026</span>
              <h2 class="srv-form-title">Start Your Company</h2>
              <p class="srv-form-subtitle">Lock government fee waiver &amp; get instant transparent quotation</p>
            </div>

            <form id="srv-hero-lead-form" class="srv-form-body">
              
              <div class="srv-input-group">
                <label class="srv-label" for="srv-lead-name">Founder Full Name <span class="req">*</span></label>
                <input type="text" id="srv-lead-name" class="srv-input" placeholder="e.g. Rahul Sharma" required />
              </div>

              <div class="srv-input-row">
                <div class="srv-input-group">
                  <label class="srv-label" for="srv-lead-email">Work / Personal Email <span class="req">*</span></label>
                  <input type="email" id="srv-lead-email" class="srv-input" placeholder="rahul@example.com" required />
                </div>
                <div class="srv-input-group">
                  <label class="srv-label" for="srv-lead-phone">Mobile Number <span class="req">*</span></label>
                  <input type="tel" id="srv-lead-phone" class="srv-input" placeholder="9876543210" maxlength="10" required />
                </div>
              </div>

              <div class="srv-input-row">
                <div class="srv-input-group">
                  <label class="srv-label" for="srv-lead-state">Registered Office State <span class="req">*</span></label>
                  <select id="srv-lead-state" class="srv-select" required>
                    <option value="Delhi" selected>Delhi (Stamp Duty ~₹360)</option>
                    <option value="Maharashtra">Maharashtra (Stamp Duty ~₹1,300)</option>
                    <option value="Karnataka">Karnataka (Stamp Duty ~₹2,000)</option>
                    <option value="Tamil Nadu">Tamil Nadu (Stamp Duty ~₹1,500)</option>
                    <option value="Telangana">Telangana (Stamp Duty ~₹1,500)</option>
                    <option value="Uttar Pradesh">Uttar Pradesh (Stamp Duty ~₹1,000)</option>
                    <option value="Gujarat">Gujarat (Stamp Duty ~₹2,000)</option>
                    <option value="Haryana">Haryana (Stamp Duty ~₹600)</option>
                    <option value="West Bengal">West Bengal (Stamp Duty ~₹1,500)</option>
                    <option value="Rajasthan">Rajasthan (Stamp Duty ~₹1,500)</option>
                    <option value="Kerala">Kerala (Stamp Duty ~₹2,000)</option>
                    <option value="Andhra Pradesh">Andhra Pradesh (Stamp Duty ~₹1,500)</option>
                    <option value="Madhya Pradesh">Madhya Pradesh (Stamp Duty ~₹2,000)</option>
                    <option value="Punjab">Punjab (Stamp Duty ~₹1,500)</option>
                    <option value="Bihar">Bihar (Stamp Duty ~₹1,500)</option>
                    <option value="Odisha">Odisha (Stamp Duty ~₹1,500)</option>
                    <option value="Chandigarh">Chandigarh (Stamp Duty ~₹360)</option>
                    <option value="Goa">Goa (Stamp Duty ~₹1,000)</option>
                  </select>
                </div>
                <div class="srv-input-group">
                  <label class="srv-label" for="srv-lead-company">Proposed Company Name</label>
                  <input type="text" id="srv-lead-company" class="srv-input" placeholder="e.g. Nexa AI Solutions" />
                </div>
              </div>

              <!-- Package Selector Pills -->
              <div class="srv-input-group">
                <label class="srv-label">Select Incorporation Plan</label>
                <div class="srv-pkg-selector">
                  <div class="srv-pkg-pill" data-package="Starter">
                    <span class="srv-pkg-name">Starter</span>
                    <span class="srv-pkg-price">₹1,999</span>
                  </div>
                  <div class="srv-pkg-pill selected" data-package="Standard">
                    <span class="srv-pkg-name">Standard</span>
                    <span class="srv-pkg-price">₹6,999</span>
                  </div>
                  <div class="srv-pkg-pill" data-package="Growth">
                    <span class="srv-pkg-name">1-Yr Bundle</span>
                    <span class="srv-pkg-price">₹14,999</span>
                  </div>
                </div>
              </div>

              <!-- Dynamic Price Summary Box -->
              <div class="srv-form-price-summary">
                <div class="srv-summary-row">
                  <span>Tax2Biz Professional Fee</span>
                  <span id="hero-summary-prof">₹6,999</span>
                </div>
                <div class="srv-summary-row">
                  <span>GST (18%)</span>
                  <span id="hero-summary-gst">₹1,260</span>
                </div>
                <div class="srv-summary-row">
                  <span>Govt Stamp Duty &amp; PAN/TAN</span>
                  <span id="hero-summary-govt">₹515 (Delhi)</span>
                </div>
                <div class="srv-summary-row total">
                  <span>Net Estimated Payable</span>
                  <strong id="hero-summary-total">₹8,774</strong>
                </div>
              </div>

              <button type="submit" class="srv-form-submit-btn">
                <span>Proceed to Pay Professional Fee</span>
                <i class="ph-bold ph-arrow-right"></i>
              </button>

              <div class="srv-form-footnote">
                <i class="ph-bold ph-shield-check"></i>
                <span>256-Bit SSL Encrypted &bull; Lead recorded instantly &bull; No spam guarantee</span>
              </div>

            </form>

          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       2. TRUST & METRICS STRIP
       ============================================================ -->
  <section class="srv-stats-strip" aria-label="Key Performance Statistics">
    <div class="container">
      <div class="srv-stats-grid">
        <div class="srv-stat-item">
          <div class="srv-stat-val">50,000+</div>
          <div class="srv-stat-lbl">Companies Registered Across India</div>
        </div>
        <div class="srv-stat-item">
          <div class="srv-stat-val">10-12 Days</div>
          <div class="srv-stat-lbl">Average Incorporation Turnaround</div>
        </div>
        <div class="srv-stat-item">
          <div class="srv-stat-val">₹0 MCA Fee</div>
          <div class="srv-stat-lbl">Govt Waiver Up to ₹15 Lakhs Capital</div>
        </div>
        <div class="srv-stat-item">
          <div class="srv-stat-val">4.9 / 5.0</div>
          <div class="srv-stat-lbl">Google &amp; Trustpilot Founder Rating</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============================================================
       3. WHAT'S INCLUDED IN YOUR INCORPORATION KIT
       ============================================================ -->
  <section class="srv-section">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-package"></i> All-Inclusive Incorporation Kit
        </div>
        <h2 class="srv-section-title">Everything Needed to Legally Start &amp; Operate</h2>
        <p class="srv-section-sub">
          We handle the complete statutory paperwork so your company is legally incorporated, bank-ready, and compliant with zero delays.
        </p>
      </div>

      <div class="srv-grid-4">
        
        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-key"></i></div>
          <h3 class="srv-deliv-title">2x Class 3 DSC</h3>
          <p class="srv-deliv-desc">Encrypted Class 3 Digital Signature Certificates with physical cryptographic USB tokens for 2 directors.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-identification-card"></i></div>
          <h3 class="srv-deliv-title">2x Director DIN</h3>
          <p class="srv-deliv-desc">Official Director Identification Numbers (DIN) allotted by the Ministry of Corporate Affairs (MCA).</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-seal-check"></i></div>
          <h3 class="srv-deliv-title">Name Reservation</h3>
          <p class="srv-deliv-desc">RUN / SPICe+ Part A name approval with thorough MCA and Trademark clearance to prevent rejection.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-file-text"></i></div>
          <h3 class="srv-deliv-title">Drafted e-MOA &amp; e-AOA</h3>
          <p class="srv-deliv-desc">Statutory Memorandum &amp; Articles of Association tailored to your startup's business activities &amp; shareholding.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-certificate"></i></div>
          <h3 class="srv-deliv-title">Certificate of Incorporation</h3>
          <p class="srv-deliv-desc">Official Certificate of Incorporation (COI) containing your permanent Corporate Identity Number (CIN).</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-credit-card"></i></div>
          <h3 class="srv-deliv-title">Corporate PAN &amp; TAN</h3>
          <p class="srv-deliv-desc">Permanent Account Number (PAN) and Tax Deduction Account Number (TAN) generated automatically with the COI.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-bank"></i></div>
          <h3 class="srv-deliv-title">Zero-Balance Current A/c</h3>
          <p class="srv-deliv-desc">Assisted zero-balance current account opening with India's top banks (ICICI, HDFC, Axis, SBI) within 48 hours.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon"><i class="ph-bold ph-users-three"></i></div>
          <h3 class="srv-deliv-title">EPFO &amp; ESIC Registrations</h3>
          <p class="srv-deliv-desc">Immediate employer social security registrations via MCA AGILE-PRO-S form for seamless employee hiring.</p>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       4. TRANSPARENT COST BREAKDOWN & LIVE CALCULATOR
       ============================================================ -->
  <section class="srv-section alt-bg" id="pricing-calculator">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-calculator"></i> 100% Fee Transparency
        </div>
        <h2 class="srv-section-title">Transparent Cost Breakdown — Zero Hidden Fees</h2>
        <p class="srv-section-sub">
          Unlike aggregators who lure founders with "Free" registration only to bill ₹15,000+ at checkout, Tax2Biz provides itemized statutory breakdowns.
        </p>
      </div>

      <!-- Interactive Calculator Container -->
      <div class="srv-calc-container">
        
        <div class="srv-calc-selectors">
          <div class="srv-input-group">
            <label class="srv-label" for="calc-state-select">Select Registered Office State</label>
            <select id="calc-state-select" class="srv-select">
              <option value="Delhi" selected>Delhi (Stamp Duty ~₹360)</option>
              <option value="Maharashtra">Maharashtra (Stamp Duty ~₹1,300)</option>
              <option value="Karnataka">Karnataka (Stamp Duty ~₹2,000)</option>
              <option value="Tamil Nadu">Tamil Nadu (Stamp Duty ~₹1,500)</option>
              <option value="Telangana">Telangana (Stamp Duty ~₹1,500)</option>
              <option value="Uttar Pradesh">Uttar Pradesh (Stamp Duty ~₹1,000)</option>
              <option value="Gujarat">Gujarat (Stamp Duty ~₹2,000)</option>
              <option value="Haryana">Haryana (Stamp Duty ~₹600)</option>
              <option value="West Bengal">West Bengal (Stamp Duty ~₹1,500)</option>
              <option value="Rajasthan">Rajasthan (Stamp Duty ~₹1,500)</option>
              <option value="Kerala">Kerala (Stamp Duty ~₹2,000)</option>
              <option value="Andhra Pradesh">Andhra Pradesh (Stamp Duty ~₹1,500)</option>
              <option value="Madhya Pradesh">Madhya Pradesh (Stamp Duty ~₹2,000)</option>
              <option value="Punjab">Punjab (Stamp Duty ~₹1,500)</option>
            </select>
          </div>

          <div class="srv-input-group">
            <label class="srv-label" for="calc-capital-select">Authorized Share Capital Tier</label>
            <select id="calc-capital-select" class="srv-select">
              <option value="100000" selected>₹1,00,000 (₹0 MCA Govt Fee)</option>
              <option value="500000">₹5,00,000 (₹0 MCA Govt Fee)</option>
              <option value="1000000">₹10,00,000 (₹0 MCA Govt Fee)</option>
              <option value="1500000">₹15,00,000 (Max Zero-Govt-Fee Limit)</option>
              <option value="2500000">₹25,00,000 (MCA Slab Rate Applies)</option>
            </select>
          </div>
        </div>

        <!-- Real-time Cost Breakdown Table -->
        <table class="srv-calc-table" aria-label="Itemized Incorporation Cost Table">
          <thead>
            <tr>
              <th>Fee Component</th>
              <th>Statutory Authority</th>
              <th style="text-align: right;">Amount (INR)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <strong>MCA SPICe+ Part B Filing Fee</strong><br>
                <small style="color: #64748B;">Central Registration Centre (CRC) electronic filing fee</small>
              </td>
              <td>Ministry of Corporate Affairs</td>
              <td class="amount" id="calc-mca-fee"><span class="srv-calc-pill-zero">₹0 (Govt Fee Waiver &le; ₹15L)</span></td>
            </tr>
            <tr>
              <td>
                <strong>State Stamp Duty on e-MOA &amp; e-AOA</strong><br>
                <small style="color: #64748B;">Varies strictly by state jurisdiction (<span id="calc-state-name-label">Delhi</span>)</small>
              </td>
              <td>State Revenue Department</td>
              <td class="amount" id="calc-stamp-duty">₹360</td>
            </tr>
            <tr>
              <td>
                <strong>Corporate PAN &amp; TAN Statutory Challan</strong><br>
                <small style="color: #64748B;">Mandatory direct government tax allotment fees (₹66 + ₹65 + GST)</small>
              </td>
              <td>NSDL / Income Tax Dept</td>
              <td class="amount" id="calc-pantotal">₹155</td>
            </tr>
            <tr>
              <td>
                <strong>Tax2Biz Professional Drafting &amp; Advisory Fee</strong><br>
                <small style="color: #64748B;">Includes 2x DSC Class 3, DIN, name reservation, MOA/AOA drafting &amp; CA certification</small>
              </td>
              <td>Tax2Biz Chartered Accountants</td>
              <td class="amount" id="calc-prof-fee">₹6,999</td>
            </tr>
            <tr>
              <td>
                <strong>GST (18% on Professional Services)</strong><br>
                <small style="color: #64748B;">Standard input tax credit (ITC) eligible GST invoice provided</small>
              </td>
              <td>Government of India</td>
              <td class="amount" id="calc-gst-fee">₹1,260</td>
            </tr>
            <tr class="total-row">
              <td colspan="2">
                <strong>Total Net Investment (Statutory + Professional + GST)</strong><br>
                <small style="color: #64748B; font-weight: 400;">No hidden charges. Complete kit delivered to your inbox.</small>
              </td>
              <td class="amount" id="calc-grand-total">₹8,774</td>
            </tr>
          </tbody>
        </table>

      </div>

      <!-- 3 Structured Pricing Packages -->
      <div class="srv-pricing-grid">
        
        <!-- Tier 1: Starter -->
        <div class="srv-pricing-card">
          <h3 class="srv-card-tier">Starter Plan</h3>
          <p class="srv-card-desc">For founders who already hold valid Class 3 DSC tokens and just need professional drafting and SPICe+ filing.</p>
          <div class="srv-card-price-box">
            <div class="srv-card-amount">₹1,999</div>
            <div class="srv-card-fee-sub">+ Govt Stamp Duty &amp; 18% GST</div>
          </div>
          <ul class="srv-card-features">
            <li><i class="ph-bold ph-check"></i> SPICe+ Part A Name Reservation (2 attempts)</li>
            <li><i class="ph-bold ph-check"></i> e-MOA &amp; e-AOA Drafting</li>
            <li><i class="ph-bold ph-check"></i> SPICe+ Part B Filing &amp; CA Certification</li>
            <li><i class="ph-bold ph-check"></i> Certificate of Incorporation (COI)</li>
            <li><i class="ph-bold ph-check"></i> Corporate PAN &amp; TAN Generation</li>
            <li><i class="ph-bold ph-x" style="color: #94A3B8;"></i> <span style="color: #94A3B8;">Excludes DSC Tokens (Must provide existing)</span></li>
          </ul>
          <button type="button" class="srv-card-cta outline" data-package="Starter">
            Select Starter Plan
          </button>
        </div>

        <!-- Tier 2: Standard (Featured) -->
        <div class="srv-pricing-card featured">
          <div class="srv-card-ribbon">MOST POPULAR &bull; ALL INCLUSIVE</div>
          <h3 class="srv-card-tier">Standard All-Inclusive</h3>
          <p class="srv-card-desc">The complete incorporation kit for 2 directors. Zero hassle, everything included from DSC to bank account.</p>
          <div class="srv-card-price-box">
            <div class="srv-card-amount">₹6,999</div>
            <div class="srv-card-fee-sub">+ State Stamp Duty &amp; 18% GST</div>
          </div>
          <ul class="srv-card-features">
            <li><i class="ph-bold ph-check"></i> <strong>2x Class 3 Digital Signatures (DSC) with USB Tokens</strong></li>
            <li><i class="ph-bold ph-check"></i> <strong>2x Director Identification Numbers (DIN)</strong></li>
            <li><i class="ph-bold ph-check"></i> RUN / SPICe+ Part A Name Approval</li>
            <li><i class="ph-bold ph-check"></i> Custom e-MOA (INC-33) &amp; e-AOA (INC-34)</li>
            <li><i class="ph-bold ph-check"></i> Certificate of Incorporation (COI) + CIN</li>
            <li><i class="ph-bold ph-check"></i> Corporate PAN &amp; TAN Allotment</li>
            <li><i class="ph-bold ph-check"></i> Zero-Balance Current Bank Account Setup</li>
            <li><i class="ph-bold ph-check"></i> EPFO &amp; ESIC Employer Registrations</li>
          </ul>
          <button type="button" class="srv-card-cta primary" data-package="Standard">
            Select Standard Plan &rarr;
          </button>
        </div>

        <!-- Tier 3: Growth / Complete 1st Year Compliance -->
        <div class="srv-pricing-card">
          <h3 class="srv-card-tier">Startup Growth Bundle</h3>
          <p class="srv-card-desc">Complete incorporation plus 1st year mandatory ROC compliances, auditor appointment, and GST registration.</p>
          <div class="srv-card-price-box">
            <div class="srv-card-amount">₹14,999</div>
            <div class="srv-card-fee-sub">+ State Stamp Duty &amp; 18% GST</div>
          </div>
          <ul class="srv-card-features">
            <li><i class="ph-bold ph-check"></i> <strong>Everything in Standard All-Inclusive Plan</strong></li>
            <li><i class="ph-bold ph-check"></i> <strong>First Auditor Appointment (Form ADT-1)</strong></li>
            <li><i class="ph-bold ph-check"></i> <strong>Commencement of Business (Form INC-20A)</strong></li>
            <li><i class="ph-bold ph-check"></i> <strong>GST Registration Certificate (GSTIN)</strong></li>
            <li><i class="ph-bold ph-check"></i> Udyam / MSME Registration Certificate</li>
            <li><i class="ph-bold ph-check"></i> Physical Share Certificates &amp; Stamp Stamping</li>
            <li><i class="ph-bold ph-check"></i> 1-Year Dedicated CA Compliance Support</li>
          </ul>
          <button type="button" class="srv-card-cta outline" data-package="Growth">
            Select Growth Bundle
          </button>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       5. INCORPORATION PROCESS ROADMAP (TIMELINE)
       ============================================================ -->
  <section class="srv-section">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-clock-counter-clockwise"></i> Seamless 10-12 Day Timeline
        </div>
        <h2 class="srv-section-title">Step-by-Step Incorporation Process</h2>
        <p class="srv-section-sub">
          We handle each regulatory milestone with the Ministry of Corporate Affairs so you can stay focused on building your product and team.
        </p>
      </div>

      <div class="srv-process-grid">
        
        <div class="srv-process-step">
          <span class="srv-step-number-tag">STEP 1</span>
          <h3 class="srv-step-heading">DSC &amp; Document Review</h3>
          <p class="srv-step-desc">We verify KYC documents for all directors and issue Class 3 Digital Signature Certificates (DSC) with hardware tokens.</p>
          <div class="srv-step-timeline"><i class="ph-bold ph-clock"></i> Day 1 - 2</div>
        </div>

        <div class="srv-process-step">
          <span class="srv-step-number-tag">STEP 2</span>
          <h3 class="srv-step-heading">Name Reservation (RUN)</h3>
          <p class="srv-step-desc">We perform phonetic trademark checks and file your preferred business names via SPICe+ Part A for Central Registration Centre approval.</p>
          <div class="srv-step-timeline"><i class="ph-bold ph-clock"></i> Day 2 - 3</div>
        </div>

        <div class="srv-process-step">
          <span class="srv-step-number-tag">STEP 3</span>
          <h3 class="srv-step-heading">SPICe+ Part B &amp; Drafting</h3>
          <p class="srv-step-desc">We draft tailored e-MOA &amp; e-AOA, obtain digital subscriber signatures, and file the consolidated SPICe+ Part B with MCA CRC.</p>
          <div class="srv-step-timeline"><i class="ph-bold ph-clock"></i> Day 4 - 7</div>
        </div>

        <div class="srv-process-step">
          <span class="srv-step-number-tag">STEP 4</span>
          <h3 class="srv-step-heading">COI, PAN, TAN &amp; Bank</h3>
          <p class="srv-step-desc">ROC approves your filing, issuing the Certificate of Incorporation (COI), PAN, TAN, DINs, and opening your zero-balance current account.</p>
          <div class="srv-step-timeline"><i class="ph-bold ph-clock"></i> Day 8 - 12</div>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       6. ELIGIBILITY & MINIMUM STATUTORY REQUIREMENTS
       ============================================================ -->
  <section class="srv-section alt-bg">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-check-circle"></i> Eligibility Criteria
        </div>
        <h2 class="srv-section-title">Minimum Requirements to Incorporate</h2>
        <p class="srv-section-sub">
          Ensure your founding team meets the basic statutory conditions stipulated under the Indian Companies Act, 2013.
        </p>
      </div>

      <div class="srv-grid-4">
        
        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon" style="background: #ECFDF5; color: #059669;"><i class="ph-bold ph-users"></i></div>
          <h3 class="srv-deliv-title">Minimum 2 Directors</h3>
          <p class="srv-deliv-desc">Must have at least 2 directors (maximum 15). At least one director must be an Indian resident living in India for &ge; 182 days.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon" style="background: #ECFDF5; color: #059669;"><i class="ph-bold ph-user-circle"></i></div>
          <h3 class="srv-deliv-title">Minimum 2 Shareholders</h3>
          <p class="srv-deliv-desc">Must have at least 2 shareholders (maximum 200). Directors and shareholders can be the exact same two individuals.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon" style="background: #ECFDF5; color: #059669;"><i class="ph-bold ph-map-pin"></i></div>
          <h3 class="srv-deliv-title">Registered Office Address</h3>
          <p class="srv-deliv-desc">A valid postal address in India. Can be a commercial office, coworking desk, or even a founder's residential address.</p>
        </div>

        <div class="srv-deliverable-card">
          <div class="srv-deliv-icon" style="background: #ECFDF5; color: #059669;"><i class="ph-bold ph-currency-inr"></i></div>
          <h3 class="srv-deliv-title">No Minimum Capital</h3>
          <p class="srv-deliv-desc">There is zero mandatory paid-up capital requirement. You can legally incorporate your company with as little as ₹1,000.</p>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       7. DOCUMENTS REQUIRED CHECKLIST (TABBED)
       ============================================================ -->
  <section class="srv-section">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-files"></i> Document Checklist
        </div>
        <h2 class="srv-section-title">Documents Required for Incorporation</h2>
        <p class="srv-section-sub">
          All documents are submitted electronically as clear scanned copies. No physical hard copies need to be mailed.
        </p>
      </div>

      <!-- Tab Buttons -->
      <div class="srv-tabs-nav" role="tablist">
        <button type="button" class="srv-tab-btn active" data-tab="tab-indian-directors" role="tab" aria-selected="true">
          For Indian Directors / Shareholders
        </button>
        <button type="button" class="srv-tab-btn" data-tab="tab-foreign-directors" role="tab" aria-selected="false">
          For Foreign Directors / NRIs
        </button>
        <button type="button" class="srv-tab-btn" data-tab="tab-office-address" role="tab" aria-selected="false">
          For Registered Office Address
        </button>
      </div>

      <!-- Tab Content Panes -->
      <div class="srv-tabs-content">
        
        <!-- Tab 1: Indian Directors -->
        <div class="srv-tab-pane active" id="tab-indian-directors" role="tabpanel">
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">PAN Card (Mandatory)</div>
              <p class="srv-doc-desc">Self-attested clear scanned copy of PAN card. Name and Date of Birth must match official ITD records.</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Identity Proof (Any One)</div>
              <p class="srv-doc-desc">Self-attested copy of Aadhaar Card, Passport, Voter ID, or Valid Driving License.</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Address Proof (Less than 2 Months Old)</div>
              <p class="srv-doc-desc">Bank Account Statement with latest transactions, Electricity Bill, or Telephone/Mobile Bill with applicant's full address.</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Passport-Size Photograph</div>
              <p class="srv-doc-desc">Clear digital portrait photo of each director against a white or light background.</p>
            </div>
          </div>
        </div>

        <!-- Tab 2: Foreign Directors -->
        <div class="srv-tab-pane" id="tab-foreign-directors" role="tabpanel">
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Valid Passport (Mandatory)</div>
              <p class="srv-doc-desc">Clear scan of valid passport. Must be notarized and apostilled (or consularized by Indian Embassy in home country).</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Residential Address Proof</div>
              <p class="srv-doc-desc">Driving license, residence card, bank statement or utility bill &lt; 2 months old, notarized and apostilled.</p>
            </div>
          </div>
        </div>

        <!-- Tab 3: Registered Office -->
        <div class="srv-tab-pane" id="tab-office-address" role="tabpanel">
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Latest Utility Bill (&lt; 2 Months Old)</div>
              <p class="srv-doc-desc">Electricity Bill, Water Bill, or Gas Bill for the registered property. Must clearly state the complete address.</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">No Objection Certificate (NOC)</div>
              <p class="srv-doc-desc">Written NOC from the property owner consenting to use the premises as the registered office of the company (We provide draft format).</p>
            </div>
          </div>
          <div class="srv-doc-item">
            <i class="ph-fill ph-check-circle"></i>
            <div>
              <div class="srv-doc-title">Rent Agreement / Property Deed</div>
              <p class="srv-doc-desc">Notarized rent agreement in the name of the director/company, or ownership deed if property is owned.</p>
            </div>
          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       8. MANDATORY POST-INCORPORATION COMPLIANCES
       ============================================================ -->
  <section class="srv-section alt-bg">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-shield-warning"></i> Crucial Legal Alerts
        </div>
        <h2 class="srv-section-title">Mandatory Post-Incorporation Compliances</h2>
        <p class="srv-section-sub">
          Getting incorporated is only step one. Avoid heavy MCA penalties and company strike-off by observing statutory post-registration deadlines.
        </p>
      </div>

      <div class="srv-compliance-grid">
        
        <div class="srv-compliance-card">
          <span class="srv-comp-tag">CRITICAL &bull; WITHIN 180 DAYS</span>
          <h3 class="srv-comp-title">Form INC-20A (Commencement of Business)</h3>
          <p class="srv-comp-desc">
            Mandatory MCA filing declaring that shareholders have deposited initial capital in the company bank account. Non-filing incurs a penalty of ₹50,000 on the company + ₹1,000/day on directors, and prevents future business operations.
          </p>
        </div>

        <div class="srv-compliance-card">
          <span class="srv-comp-tag">MANDATORY &bull; WITHIN 30 DAYS</span>
          <h3 class="srv-comp-title">Form ADT-1 (First Auditor Appointment)</h3>
          <p class="srv-comp-desc">
            The Board of Directors must appoint the company's first Statutory Chartered Accountant (Auditor) within 30 days of incorporation to oversee books of accounts.
          </p>
        </div>

        <div class="srv-compliance-card">
          <span class="srv-comp-tag">STATUTORY &bull; WITHIN 60 DAYS</span>
          <h3 class="srv-comp-title">Issue of Share Certificates</h3>
          <p class="srv-comp-desc">
            Physical share certificates must be drafted, stamped with appropriate state stamp duty, and delivered to all founding subscribers within 60 days of incorporation.
          </p>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       9. ENTITY COMPARISON: PVT LTD VS LLP VS OPC
       ============================================================ -->
  <section class="srv-section">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-chart-pie"></i> Business Structure Comparison
        </div>
        <h2 class="srv-section-title">Pvt Ltd vs LLP vs OPC vs Sole Proprietorship</h2>
        <p class="srv-section-sub">
          Understand why a Private Limited Company remains the gold standard for raising investment, limiting personal liability, and scaling.
        </p>
      </div>

      <div class="srv-compare-table-wrap">
        <table class="srv-compare-table">
          <thead>
            <tr>
              <th>Feature</th>
              <th class="highlight-col">Private Limited Company</th>
              <th>Limited Liability Partnership (LLP)</th>
              <th>One Person Company (OPC)</th>
              <th>Sole Proprietorship</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Personal Liability</strong></td>
              <td class="highlight-col"><strong>Limited to share capital</strong></td>
              <td>Limited to agreed contribution</td>
              <td>Limited to share capital</td>
              <td><span style="color: #DC2626; font-weight: 600;">Unlimited personal risk</span></td>
            </tr>
            <tr>
              <td><strong>VC &amp; Angel Investment</strong></td>
              <td class="highlight-col"><strong>Highest (Only entity VCs fund)</strong></td>
              <td>Difficult (Cannot issue equity)</td>
              <td>Low (Cannot issue ESOPs/equity)</td>
              <td>None</td>
            </tr>
            <tr>
              <td><strong>Income Tax Rate</strong></td>
              <td class="highlight-col"><strong>22% + surcharge / cess</strong></td>
              <td>30% + surcharge / cess</td>
              <td>22% + surcharge / cess</td>
              <td>Individual slab rates</td>
            </tr>
            <tr>
              <td><strong>Minimum Members</strong></td>
              <td class="highlight-col">2 Directors / 2 Shareholders</td>
              <td>2 Designated Partners</td>
              <td>1 Director / 1 Shareholder</td>
              <td>1 Owner</td>
            </tr>
            <tr>
              <td><strong>ESOPs for Employees</strong></td>
              <td class="highlight-col"><strong>Supported seamlessly</strong></td>
              <td>Not possible</td>
              <td>Not possible</td>
              <td>Not possible</td>
            </tr>
            <tr>
              <td><strong>Corporate Credibility</strong></td>
              <td class="highlight-col"><strong>Highest pan-India &amp; global</strong></td>
              <td>Moderate to High</td>
              <td>Moderate</td>
              <td>Low</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </section>

  <!-- ============================================================
       10. FREQUENTLY ASKED QUESTIONS (ACCORDION)
       ============================================================ -->
  <section class="srv-section alt-bg">
    <div class="container">
      
      <div class="srv-section-header">
        <div class="srv-section-eyebrow">
          <i class="ph-bold ph-question"></i> Got Questions?
        </div>
        <h2 class="srv-section-title">Frequently Asked Questions</h2>
        <p class="srv-section-sub">
          Expert answers to common queries about Private Limited Company registration in India.
        </p>
      </div>

      <div class="srv-faq-list">
        
        <div class="srv-faq-item active">
          <button type="button" class="srv-faq-question">
            <span>Can I register a Private Limited company from my residential address?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer" style="max-height: 200px;">
            <p>Yes, absolutely. The Ministry of Corporate Affairs (MCA) permits residential addresses (including rented apartments or owned family homes) to be registered as the official corporate office. You only need a recent electricity/utility bill and a signed No Objection Certificate (NOC) from the owner.</p>
          </div>
        </div>

        <div class="srv-faq-item">
          <button type="button" class="srv-faq-question">
            <span>What is the MCA Zero Government Fee scheme for SPICe+?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer">
            <p>Under the Government of India's ease-of-doing-business initiative, the MCA has waived the SPICe+ Part B incorporation filing fee for companies with an authorized share capital of up to ₹15 Lakhs. You only pay for state stamp duty on MOA/AOA, statutory PAN/TAN challan (₹155), and digital signature tokens (DSC).</p>
          </div>
        </div>

        <div class="srv-faq-item">
          <button type="button" class="srv-faq-question">
            <span>Can a salaried person become a director in a Private Limited company?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer">
            <p>Legally under the Companies Act, any individual over 18 years can become a director. However, you should review your existing employment contract for non-compete or dual-employment clauses. You can also hold equity purely as a shareholder without taking an executive directorship if your employment restricts directorships.</p>
          </div>
        </div>

        <div class="srv-faq-item">
          <button type="button" class="srv-faq-question">
            <span>What is the minimum capital required to incorporate?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer">
            <p>There is no mandatory minimum paid-up capital requirement under the amended Companies Act. While companies typically set their authorized capital at ₹1,00,000 or ₹10,00,000 to keep initial government fees zero, you can start operations with any paid-up capital amount you choose.</p>
          </div>
        </div>

        <div class="srv-faq-item">
          <button type="button" class="srv-faq-question">
            <span>How long does the entire incorporation take from start to finish?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer">
            <p>On average, the process takes 10 to 12 working days: 1-2 days for digital signature (DSC) issuance, 2-3 days for name approval via SPICe+ Part A, and 4-7 days for MCA Central Registration Centre (CRC) processing of SPICe+ Part B and issuance of the Certificate of Incorporation.</p>
          </div>
        </div>

        <div class="srv-faq-item">
          <button type="button" class="srv-faq-question">
            <span>Can NRIs or foreign nationals be directors in an Indian Pvt Ltd company?</span>
            <i class="ph-bold ph-caret-down"></i>
          </button>
          <div class="srv-faq-answer">
            <p>Yes! Foreign nationals and Non-Resident Indians (NRIs) can be appointed as directors and hold 100% foreign equity under the automatic FDI route for most sectors. The only mandatory statutory condition is that at least one co-director must be an Indian citizen residing in India.</p>
          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- ============================================================
       11. BOTTOM CTA ANCHOR BANNER
       ============================================================ -->
  <section class="srv-section">
    <div class="container">
      <div class="srv-cta-banner">
        <div class="srv-cta-content">
          <h2>Ready to Build Your Company?</h2>
          <p>
            Join 50,000+ founders who started their business journey with Tax2Biz. Fast, transparent, and supervised by experienced Chartered Accountants.
          </p>
        </div>
        <div class="srv-cta-actions">
          <a href="#srv-hero-lead-form" class="btn btn-primary" onclick="document.querySelector('.srv-hero-form-card').scrollIntoView({behavior:'smooth', block:'center'}); return false;">
            Start Incorporation Now <i class="ph-bold ph-arrow-right"></i>
          </a>
          <button type="button" class="btn btn-outline-white hire-expert-trigger">
            Talk to Senior CA <i class="ph-bold ph-phone"></i>
          </button>
        </div>
      </div>
    </div>
  </section>

</main>
"""

# Professional Fees Checkout Modal
checkout_modal = """
<!-- ============================================================
     PROFESSIONAL FEES CHECKOUT & PAYMENT MODAL
     ============================================================ -->
<div class="srv-modal-overlay" id="srv-checkout-modal" role="dialog" aria-modal="true" aria-labelledby="srv-modal-title">
  <div class="srv-modal-dialog">
    
    <div class="srv-modal-header">
      <h3 class="srv-modal-title" id="srv-modal-title">Complete Incorporation Booking</h3>
      <button type="button" class="srv-modal-close" id="srv-modal-close-btn" aria-label="Close modal">
        <i class="ph-bold ph-x"></i>
      </button>
    </div>

    <!-- Payment Initial View -->
    <div class="srv-modal-body" id="modal-pay-view">
      
      <!-- Order Summary Card -->
      <div class="srv-order-summary-box">
        <div class="srv-order-hdr">
          <span id="modal-pkg-name">Standard All-Inclusive</span>
          <span class="srv-calc-pill-zero">Instant Booking</span>
        </div>
        <div class="srv-order-row">
          <span>Client: <strong id="modal-client-name">Founder</strong> (<span id="modal-client-phone">Phone</span>)</span>
          <span>State: <strong id="modal-client-state">Delhi</strong></span>
        </div>
        <div class="srv-order-row">
          <span>Tax2Biz Professional Fee</span>
          <span id="modal-fee-prof">₹6,999</span>
        </div>
        <div class="srv-order-row">
          <span>GST (18%)</span>
          <span id="modal-fee-gst">₹1,260</span>
        </div>
        <div class="srv-order-row">
          <span>Est. State Stamp Duty &amp; PAN/TAN</span>
          <span id="modal-fee-govt">₹515</span>
        </div>
        <div class="srv-order-row total">
          <span>Total Payable Professional Fee</span>
          <strong id="modal-fee-total">₹8,774</strong>
        </div>
      </div>

      <!-- Payment Method Tabs -->
      <div class="srv-pay-tabs">
        <button type="button" class="srv-pay-tab active" data-method="upi">
          <i class="ph-bold ph-qr-code"></i> UPI / QR Code
        </button>
        <button type="button" class="srv-pay-tab" data-method="card">
          <i class="ph-bold ph-credit-card"></i> Cards &amp; Net Banking
        </button>
      </div>

      <!-- UPI Simulation Section -->
      <div id="modal-upi-section" class="srv-upi-box">
        <div class="srv-qr-sim">
          <!-- Realistic SVG Simulated QR Code -->
          <svg width="150" height="150" viewBox="0 0 150 150" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="150" height="150" fill="white"/>
            <!-- Corner Finder 1 -->
            <rect x="10" y="10" width="36" height="36" fill="black"/>
            <rect x="16" y="16" width="24" height="24" fill="white"/>
            <rect x="22" y="22" width="12" height="12" fill="#059669"/>
            <!-- Corner Finder 2 -->
            <rect x="104" y="10" width="36" height="36" fill="black"/>
            <rect x="110" y="16" width="24" height="24" fill="white"/>
            <rect x="116" y="22" width="12" height="12" fill="#059669"/>
            <!-- Corner Finder 3 -->
            <rect x="10" y="104" width="36" height="36" fill="black"/>
            <rect x="16" y="110" width="24" height="24" fill="white"/>
            <rect x="22" y="116" width="12" height="12" fill="#059669"/>
            <!-- Decorative Data Pixels -->
            <rect x="54" y="15" width="8" height="8" fill="black"/>
            <rect x="68" y="15" width="8" height="8" fill="black"/>
            <rect x="82" y="25" width="8" height="8" fill="black"/>
            <rect x="54" y="45" width="8" height="8" fill="black"/>
            <rect x="68" y="55" width="12" height="12" fill="#059669"/>
            <rect x="90" y="55" width="8" height="8" fill="black"/>
            <rect x="15" y="60" width="8" height="8" fill="black"/>
            <rect x="35" y="70" width="8" height="8" fill="black"/>
            <rect x="55" y="80" width="10" height="10" fill="black"/>
            <rect x="75" y="80" width="8" height="8" fill="black"/>
            <rect x="95" y="80" width="8" height="8" fill="black"/>
            <rect x="115" y="65" width="10" height="10" fill="black"/>
            <rect x="115" y="90" width="8" height="8" fill="black"/>
            <rect x="60" y="110" width="8" height="8" fill="black"/>
            <rect x="75" y="125" width="12" height="12" fill="#059669"/>
            <rect x="100" y="115" width="10" height="10" fill="black"/>
            <rect x="125" y="115" width="8" height="8" fill="black"/>
            <rect x="115" y="130" width="8" height="8" fill="black"/>
          </svg>
        </div>
        <div class="srv-upi-id-pill">
          <i class="ph-fill ph-check-circle" style="color: #059669;"></i>
          <span>pay.tax2biz@icici &bull; Amount: <span id="modal-upi-amount">₹8,774</span></span>
        </div>
        <p style="font-size: 0.8rem; color: #64748B; margin: 0;">Scan with GPay, PhonePe, Paytm, or any UPI App to lock fees</p>
      </div>

      <!-- Card / Net Banking Simulation Section -->
      <div id="modal-card-section" style="display: none; padding: 16px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px; margin-bottom: 20px;">
        <div style="font-size: 0.85rem; color: #334155; margin-bottom: 10px; font-weight: 600;">Supported Payment Channels</div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; font-size: 0.85rem; color: #64748B;">
          <span>&bull; HDFC Bank</span>
          <span>&bull; ICICI Bank</span>
          <span>&bull; State Bank of India</span>
          <span>&bull; Axis Bank</span>
          <span>&bull; Visa / Mastercard / RuPay</span>
        </div>
      </div>

      <button type="button" class="srv-pay-action-btn" id="srv-modal-pay-btn">
        <i class="ph-bold ph-shield-check"></i>
        <span>Complete &amp; Verify Payment</span>
      </button>

      <button type="button" class="srv-pay-secondary-btn" id="modal-pay-later-btn">
        Pay Later &bull; Request Senior CA Call First (Lead Saved)
      </button>

    </div>

    <!-- Payment Success Confirmation View -->
    <div class="srv-modal-body" id="modal-success-view" style="display: none;">
      <div class="srv-success-view">
        <div class="srv-success-icon"><i class="ph-bold ph-check"></i></div>
        <h3 class="srv-success-title">Booking Confirmed!</h3>
        <p class="srv-success-sub">
          Your incorporation payment has been recorded and your lead file has been activated.
        </p>

        <div class="srv-receipt-card">
          <div style="font-size: 0.82rem; color: #64748B; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Order Reference ID</div>
          <div style="font-size: 1.25rem; font-weight: 800; color: #059669; margin-bottom: 12px;" id="modal-receipt-orderid">T2B-PVT-849201</div>
          
          <div style="font-size: 0.88rem; color: #334155; line-height: 1.5;">
            <strong>Assigned Legal Manager:</strong> CA Rahul Sharma, Senior Corporate Associate<br>
            <strong>Confirmation Email:</strong> Sent to <span id="modal-receipt-email">founder@example.com</span><br>
            <strong>Next Step:</strong> Our team will reach out within 30 minutes to collect initial director KYC documents.
          </div>
        </div>

        <button type="button" class="btn btn-primary" onclick="document.getElementById('srv-checkout-modal').classList.remove('active'); document.body.style.overflow='';" style="width: 100%;">
          Go to Dashboard / Complete Documentation &rarr;
        </button>
      </div>
    </div>

  </div>
</div>
"""

# Scripts block
scripts_block = f"""
  <!-- Universal Expert Consultation Modal -->
  {expert_modal}

  <!-- Scripts -->
  <script src="script.js"></script>
  <script src="service-template.js"></script>
</body>
</html>
"""

full_page_html = head_content + universal_header + universal_drawer + main_content + universal_footer + checkout_modal + scripts_block

with open('private-limited-company-registration.html', 'w', encoding='utf-8') as f:
    f.write(full_page_html)

print('Generated private-limited-company-registration.html successfully!')
print('Total file length:', len(full_page_html))
