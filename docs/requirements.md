# HISAB: Requirements Document (v0.1)

> Owner: Founder (Nikhil) | Product Owner/PM chat | Status: Draft for Developer
> Rule: Is document me koi rate/tax slab/number hardcode nahi hai. Saare rates "VERIFY" hain aur official source se aayenge (Section 8).
> Frontend stack decision: React + TypeScript + Vite. Next.js is not part of this project.

---

## 1. Product Summary

India ke liye all-in-one finance calculator website. Sab calculators ek jagah, **no login, no popup, no "app download karo"**. Abhi MVP, future me bada business.

**Trust aur accuracy sabse bada asset hai.** Galat number = brand khatam.

### 1.1 Target User (final)
- Age 25 to 40, salaried ya naye investors
- Pehle share market / SIP / mutual fund samajhna chahte hain, phir EMI, tax
- Zyada tar mobile pe, Google se aayenge
- Tone: simple English + simple Hinglish

### 1.2 Edge (kya alag hai)
- Sab ek jagah, fast, clean
- Dark premium + neon look, mobile-first
- Category-wise inflation (special feature)
- Har rate ke saath "last updated" + source (trust)
- Future: goal-based combos (e.g. bachche ki education = inflation + SIP)

---

## 2. Final Decisions (change nahi honge)

| Area | Decision |
|---|---|
| Frontend | React + TypeScript + Vite (client-rendered single-page app); **not Next.js** |
| Backend | Python FastAPI, stateless |
| Database | Abhi nahi |    
| Login | Abhi nahi |
| Calculation, formulas, rates | **Sirf backend me**. Frontend inputs leta hai aur results dikhata hai; backend authoritative hai |
| Architecture | Plugin: 1 calculator = 1 Python file. Naya calculator add karna aasan |
| Rates | Alag config me: value, effective_from, source_url, last_verified |
| URL | Har calculator ka alag URL (SEO) |
| Hosting | Vite frontend ke liye static hosting (e.g. Vercel) + FastAPI backend (e.g. Render); deployment ke waqt plan/cost verify karo |
| Language | English + simple Hinglish |
| Mutual Fund | Pehle simple, baad me real fund data (AMFI) |
| Income Tax | Full (salaried + capital gains + business), current + pichla FY. **Sabse last** |
| Abhi nahi | T&C, ads, affiliate, admin panel, Hindi, login, premium |

### 2.1 Frontend Implementation Direction

- Frontend React + TypeScript app Vite se develop aur build hogi. Existing app `frontend/` me hai; usi codebase aur established component/page patterns ko extend karo.
- **Next.js use nahi karna**: Next.js routing, server components, API routes, ya Next-specific rendering conventions introduce na karo.
- Frontend browser me render hoti hai (SPA). URL changes, back/forward navigation, aur direct URL refresh kaam karne chahiye. Static host ko app routes ke liye `index.html` fallback dena hoga.
- Product URLs Section 3 ke mutabik hon. Har route se sahi page resolve ho, including unknown URL ka 404 page.
- Backend base URL environment variable `VITE_API_BASE_URL` se configure hoga. Vite ke `VITE_` variables browser bundle me public hote hain; unme secrets/credentials kabhi nahi rakhein.
- Calculator list, input schema, validation result, calculations, rates aur calculation result backend API se aayenge. Frontend form state, immediate input feedback, formatting, loading/error states aur presentation sambhalega; formula ya rate ka duplicate source of truth nahi banega.
- Reusable calculator UI shared components se bane. Calculator ko custom UI chahiye ho toh uske liye custom page ho sakta hai, lekin calculation backend hi karega.
- Frontend change ke baad `cd frontend; npm run lint` aur `cd frontend; npm run build` pass hone chahiye.

---

## 3. Website Structure (Pages)

| Page | URL pattern | Kaam |
|---|---|---|
| Home | `/` | Center me intro text, right side me calculators ki list |
| Calculator page | `/calculators/<calculator-slug>` | Ek calculator ka poora kaam |
| Category page | `/category/<category-slug>` | Us category ke saare calculators |
| Search results | Search bar se (home + header me) | Calculator dhoondhna |
| About / Methodology | `/about`, `/methodology` | Trust: formulas ka simple explanation, rates ke sources |
| 404 | - | Friendly page + calculators ki list |

Slug examples (final naming Developer + SEO ke saath tay hoga): `sip-calculator`, `emi-calculator`, `ppf-calculator`.

---

## 4. Home Page (jaisa founder ne bataya)

### 4.1 Layout (desktop)

```
+----------------------------------------------------------------+
| HEADER: Logo | Search bar | (menu)                             |
+--------------------------------------------+-------------------+
|                                            |  CALCULATORS      |
|            CENTER                          |  (right panel)    |
|   Proper text / hero content               |                   |
|   (abhi placeholder, baad me decide)       |  [Investment]     |
|                                            |    SIP            |
|   - Headline                               |    Step-up SIP    |
|   - 2-3 line explanation                   |    Lumpsum ...    |
|   - Trust line (updated rates, no login)   |  [Savings] ...    |
|                                            |  [Loans] ...      |
|                                            |  [Tax] ...        |
|                                            |  [Inflation] ...  |
+--------------------------------------------+-------------------+
| FOOTER: About | Methodology | Last rates update date           |
+----------------------------------------------------------------+
```

### 4.2 Rules
- **Center:** abhi sirf proper text area. Content baad me decide hoga. Developer isko aise banaye ki text/content aasani se change ho sake.
- **Right side:** saare calculators category-wise list me.
- **Right side list me calculator pe click** -> user **naye page** pe jaata hai (`/calculators/<slug>`). Calculation wahi hoti hai, home pe nahi.
- List automatic bane (backend se calculators ki list aaye), manually frontend me na likhni pade.
- **50+ calculators tak scale kare:** categories collapsible (open/close), search bar se filter.

### 4.3 Mobile (mobile-first, bahut important)
- Right side panel mobile pe side me nahi aa sakta. **Mobile pe:** header ke neeche search bar, phir category-wise calculators ki list/grid **pehle** dikhe, uske neeche center text.
- Reason: mobile user ko calculator jaldi chahiye, text padhne nahi aaya.
- Ye layout decision Developer se confirm: tablet pe kaise behave kare.

---

## 5. Calculator Page (har calculator ke liye same template)

### 5.1 Layout
1. Title + 1 line simple explanation
2. **Inputs** (sliders + number box dono). Indian format (lakh/crore) live dikhe
3. **Result cards** (bade numbers): invested amount, returns, total value, etc. (calculator ke hisab se)
4. **Chart** (donut/line/bar, calculator ke hisab se)
5. **Year-by-year table** (collapsible)
6. "Rates/assumptions" box: kaun sa rate use hua, source, last updated date
7. Short "ye kaise calculate hota hai" explanation
8. Disclaimer line: "Ye sirf estimate hai, financial advice nahi"
9. Related calculators ke links (internal linking, SEO)

### 5.2 Behaviour
- User input badle -> result **turant** update ho (chhota delay/debounce, Developer decide kare)
- Calculation **backend API** se, frontend me koi formula nahi
- Loading state dikhe, error aaye toh friendly message (technical error nahi)
- Invalid input pe inline message ("Amount 500 se 10 crore ke beech daalo")
- Koi popup nahi, koi login nahi
- Result share karne ke liye URL me inputs (optional, Phase 2)

### 5.3 Indian Number Format
- 1,00,000 style commas
- Bade numbers ke saath shabd: "12.5 Lakh", "1.2 Crore"
- Input box me typing ke time bhi format dikhe

---

## 6. Categories (scalable)

| Category | MVP calculators | Future |
|---|---|---|
| Investment | SIP, Step-up SIP, Lumpsum, Mutual Fund, XIRR | CAGR, SWP, FD |
| Govt Savings | PPF, EPF, RD | NPS, Sukanya Samriddhi |
| Loans | EMI | Loan prepayment |
| Tax | GST, Income Tax | HRA, Salary in-hand, Gratuity |
| Inflation | Category-wise Inflation | - |
| Planning | (abhi khali) | Retirement planner, Goal planner, Goal combos |

Rule: naya calculator = sirf backend me ek file + category tag. Frontend me menu, home list, search, category page **apne aap** update ho.

---

## 7. Backend Requirements

### 7.1 General
- FastAPI, stateless, koi DB nahi, koi login nahi
- Har calculator ek alag Python file (plugin)
- Server start pe saare plugins automatic discover hon
- Free tier (Render) pe sleep ho sakta hai, cold start ka effect user ko kam dikhe (loading message). **Developer se confirm: cold start ka solution**

### 7.2 Har calculator plugin ko ye batana hoga
- Naam, slug, category, short description, SEO title/description
- Inputs ki definition: naam, type, unit, min, max, default, step, help text (taaki frontend form **automatic** bana sake)
- Calculation function
- Output ki structure: result cards, chart data, table data
- Kaun se rates use hote hain (rates config se)
- Test cases

### 7.3 API (high level, details Developer decide karega)
- Saare calculators ki list (category ke saath)
- Ek calculator ki definition (inputs ka form)
- Calculate (inputs bhejo, result lo)
- Rates ki list (value, effective_from, source_url, last_verified)
- Health check

### 7.4 Rates Config (alag file/folder)
Har rate ke saath ye 4 cheezein (final):
- value
- effective_from
- source_url
- last_verified

Extra rules:
- Rate code ke andar hardcode **nahi**
- Frontend ko rates ka "last updated" date backend se milega
- Agar koi rate purana (stale) ho jaye (e.g. 90+ din se verify nahi), internal warning (admin panel abhi nahi, toh log/report). **Developer se confirm: kaise**

### 7.5 Validation aur Safety
- Saare inputs backend pe validate (min/max, negative, zero, bahut bade numbers)
- Rate limiting (basic) taaki free server misuse na ho. **Developer se confirm**
- CORS sirf apni frontend site ke liye
- Koi personal data store/log nahi

### 7.6 Accuracy Rules
- Paise/decimal ka rounding rule ek hi jagah tay ho, sab calculators me same
- Har calculator ke test cases official/trusted calculators se verify
- Calculator tab hi "live" ho jab uske test cases pass hon

---

## 8. Rates & Official Sources (Verification Plan)

> **Koi bhi number yaad se mat daalo.** Neeche sirf "kaun decide karta hai" aur "kaha se verify karna hai". Actual values live official source se aayengi.

| Rate / Rule | Kaun decide karta hai | Official source (verify) | Kitni baar badalta hai |
|---|---|---|---|
| PPF interest rate | Finance Ministry | Finance Ministry / India Post / NSI notification | Quarterly (VERIFY) |
| RD interest rate (Post Office) | Finance Ministry | India Post / NSI | Quarterly (VERIFY) |
| EPF interest rate | EPFO (CBT) + Finance Ministry approval | EPFO website | Saal me ek baar (VERIFY) |
| GST slabs / rules | GST Council | GST portal / CBIC | Council meetings ke baad |
| Income Tax slabs, deductions, capital gains rules | Finance Ministry (Budget / Finance Act) | Income Tax Dept (incometax.gov.in) | Har Budget ke baad |
| Inflation (CPI categories) | MOSPI | MOSPI CPI releases | Monthly |
| Mutual fund data (future) | AMFI | AMFI | Daily (NAV) |
| Bank RD/EMI rates | Banks khud | **Product me nahi.** User khud rate daalega | - |

**Open item:** Category inflation me "education" aur "automobile" ke liye clean official CPI series nahi hoti. Ye verify karna hai ki kaun si category MOSPI se aa sakti hai aur kaun si user-editable default + clear label ("estimate") ke saath jayegi. Bina source ka number dikhana allowed nahi.

---

## 9. Calculator Specs: MVP Priority Order

Audience (25-40, share market/SIP pehle) ke hisab se:

### Phase 1: Core Investment + Loan (pehle perfect)
1. SIP
2. Step-up SIP
3. Lumpsum
4. EMI

### Phase 2: Trust + Differentiator
5. Inflation (category-wise) (special feature)
6. XIRR
7. Mutual Fund (simple version)

### Phase 3: Govt Savings (rates verify ke saath)
8. PPF
9. EPF
10. RD

### Phase 4: Tax
11. GST
12. Income Tax (sabse last, full)

> Detailed spec (inputs min/max/default, outputs, charts, edge cases, formula rules) har calculator ka **alag se, ek-ek karke** banega. Ye document sirf structure aur requirements ke liye hai.

### 9.1 Har calculator spec ka template (aage use hoga)
- Purpose (user kya jaanna chahta hai)
- Inputs: naam, unit, min, max, default, step
- Outputs: result cards, chart, table
- Formula rules: compounding frequency, limits, rounding
- Edge cases
- Rates used (config se)
- 5-10 test cases (official/trusted calculators se verify)
- Hinglish help text

---

## 10. UI / UX Direction

- **Look:** dark premium background, neon accent (ek hi primary neon colour + ek secondary, zyada rang nahi)
- **Mobile-first:** pehle mobile design, phir desktop
- **Fast:** kam images, light page, fast load (Core Web Vitals SEO ke liye important)
- **Readable:** neon text sirf accent ke liye, main text high contrast (accessibility)
- **No popup, no cookie-banner-jaisi cheezein** jab tak legally zaroori na ho
- **Tone:** simple English + Hinglish. Jargon aaye toh 1 line me samjhao (e.g. "XIRR = alag-alag date pe paisa daalne par asli return")
- **Sliders + typed input dono**, sliders thumb-friendly
- **Chart:** simple aur clear, zyada fancy nahi
- **User confusion check:** har page pe user ko 3 sawal ka jawab 5 second me milna chahiye: ye kya hai? mujhe kya daalna hai? result kya hai?

---

## 11. SEO Requirements (product side)

- Har calculator ka unique URL, title, meta description, H1
- Page me readable text content (sirf form nahi), explanation + formula + FAQ
- Vite app client-rendered hai; **Next.js/SSR assume nahi karna**. Har route par title/description jaise metadata update hon.
- `sitemap.xml` aur `robots.txt` static hosting ke saath serve hon, aur calculator routes ke liye host fallback sahi configure ho.
- Agar client-rendering se search indexing/readable content ki zaroorat poori nahi hoti, evaluate Vite-compatible pre-rendering/static generation for public calculator pages; iske liye Next.js migration required nahi hai.
- Proper internal linking (related calculators)
- Structured data (FAQ etc.) Phase 2
- Detailed SEO plan **Business & Marketing chat** ka kaam hai

---

## 12. Trust Features (MVP me hi)

- Har result page pe: "Rates last updated: <date>" + source link
- Methodology page: kaun sa formula, kaun si assumption
- Disclaimer: estimate hai, advice nahi
- Koi specific stock/fund ki recommendation **nahi** (SEBI risk)
- Galti mile toh report karne ka simple tareeka (email link, abhi form nahi)

---

## 13. Roadmap

| Phase | Kya |
|---|---|
| MVP-1 | Project setup, plugin system, rates config, home page, calculator template, SIP + Step-up + Lumpsum + EMI |
| MVP-2 | Inflation (category-wise), XIRR, Mutual Fund (simple), search, category pages |
| MVP-3 | PPF, EPF, RD, GST, methodology page |
| MVP-4 | Income Tax (full, current + pichla FY) |
| Later | Naye calculators (FD, SWP, CAGR, NPS, Sukanya, Gratuity, HRA, Retirement, Goal planner, Salary in-hand, Loan prepayment) |
| Later | Goal-based combos |
| Later | Real MF data (AMFI) |
| Later | T&C, ads, affiliate, admin panel, Hindi, login, premium |

---

## 14. Rate Update Checklist (recurring)

| Kab | Kya verify |
|---|---|
| Har quarter shuru hone se pehle | PPF, RD rates (Finance Ministry / India Post notification) |
| Saal me jab EPFO declare kare | EPF rate |
| Union Budget ke baad | Income Tax slabs, deductions, capital gains rules |
| GST Council meeting ke baad | GST slabs/changes |
| Har mahine (MOSPI release ke baad) | Inflation data (agar use ho raha ho) |
| Har release se pehle | Us calculator ke saare test cases dobara chalao |

Har verify ke baad: `last_verified` date update, source link save.

---

## 15. Test Strategy (product side)

- Har calculator ke 5-10 test cases, official/trusted calculators se verify
- Edge cases: 0, minimum, maximum, bahut chhota/bada tenure, decimal inputs
- Mobile pe har calculator manually check
- Indian number format check
- Calculator tab "live" jab test cases pass

---

## 16. Developer ke liye Open Questions (confirm karne hain)

1. Render free tier cold start: user ko kaise handle karen?
2. Tablet layout (home page right panel)
3. Plugin auto-discovery ka final structure
4. Rate limiting kaise
5. Stale rates ki warning kaise (admin panel ke bina)
6. Home page content (center text) ko easily editable kaise rakhen
7. Kya Vite-compatible pre-rendering/static generation SEO ke liye zaroori hai

---

## 17. Business & Marketing Chat ko Batana

- Target user: 25-40, salaried/naye investors, share market + SIP pehle
- Special feature: category-wise inflation, trust (updated rates + source)
- SEO ke liye har calculator ka alag URL + readable content
- Monetization abhi nahi; baad me ads/affiliate (Business chat plan banaye)
- SEBI risk: specific fund/stock recommendation nahi

---

## 18. Definition of Done (MVP)

- [ ] Plugin system chal raha hai, naya calculator ek file se add hota hai
- [ ] Frontend React + TypeScript + Vite se build hota hai; Next.js dependency/convention nahi hai
- [ ] Home page: center text + right side category-wise list, click pe naya page
- [ ] Mobile layout theek
- [ ] Calculator aur category URLs direct open/refresh, browser back/forward, aur 404 handling ke saath kaam karte hain
- [ ] Frontend lint aur production build pass; static-host SPA fallback configured
- [ ] Rates config me 4 fields ke saath
- [ ] 12 calculators ke test cases pass
- [ ] Har page pe "last updated" + disclaimer
- [ ] Free tier pe deploy   