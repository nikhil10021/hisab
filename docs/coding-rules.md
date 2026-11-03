# HISAB: CODING RULES (v1.1)

Ye rules non-negotiable hain. Rule todna pade toh pehle bata, phir kar.

## A. GOLDEN RULES
1. NO CALCULATION IN FRONTEND. Plus, minus, percent, "returns = total - invested" bhi nahi. Backend jo bheje, frontend wahi dikhaye.
2. NO HARDCODE IN FRONTEND. Rates, limits, defaults, min/max, calculator ki list, input labels, units, categories: sab backend API se.
3. NO DUPLICATION. Logic do jagah nahi. Do baar likhna pade toh shared helper.
4. ONE CALCULATOR = ONE FILE (backend). Naya calculator = ek file + tests. Frontend/router/menu me kuch change nahi.
5. ACCURACY > SPEED. Galat paisa dikhane se behtar hai kuch na dikhana.

## B. ARCHITECTURE (upar se neeche, kabhi ulta nahi)
Backend:  router (HTTP only) -> service/registry -> calculator (math) -> core helpers + config
Frontend: page (route) -> feature component -> ui component -> api client
- Router me business logic nahi. Sirf request lo, validate karo, response do.
- Calculator me FastAPI/HTTP ka import nahi. Pure Python class, bina server ke testable.
- Calculator me user data/DB/session ka concept nahi. Backend stateless.

## C. FOLDER STRUCTURE ( CAN CHANGE IN FUTURE )
backend/
  app/
    main.py                  # app create, middleware, routers mount. Bas.
    api/v1/                  # calculators.py, health.py (versioned)
    core/
      base.py                # BaseCalculator
      registry.py            # auto-discovery
      fields.py              # reusable input fields (money, rate_percent, years...)
      result.py              # output builders (summary_card, pie, area, table)
      finance_math.py        # shared formulas (compound growth, annuity, PMT...)
      money.py               # Decimal + rounding policy
      errors.py              # custom exceptions
      config_loader.py       # rates/tax config loader + validator
      settings.py            # env based settings
    calculators/             # 1 file = 1 calculator
      investment/ savings/ loans/ tax/ inflation/ planning/
    config/                  # rates/*.json, tax/*.json (versioned by FY)
    content/                 # seo text, faqs per calculator
  tests/
    unit/ golden/ api/       # golden = Product Owner ke verified examples
frontend/                    # React + TypeScript + Vite (NOT Next.js)
  src/
    pages/                   # route-level pages
    components/ui/           # dumb reusable (Button, Card, Slider)
    components/calculator/   # DynamicForm, ResultSummary, ChartRenderer, DataTable
    components/layout/       # Navbar, Footer, SearchCmdK, ThemeToggle
    features/                # special pages (income-tax, xirr, inflation): UI only
    lib/api/                 # ek hi API client + generated types
    lib/format/              # sirf display formatting (INR lakh/crore, dates)
    styles/ theme/           # design tokens
  scripts/                   # build-time: prerender, sitemap/robots generate
docs/                        # decisions/ (ADR), add-calculator.md, rates-update.md
.github/workflows/           # CI
Naya folder banane se pehle puch. Structure apne aap mat badal.

## D. BACKEND RULES
Calculator design
- Har calculator BaseCalculator se inherit kare: slug, name, category, icon, description,
  seo (title, description, faqs), is_live, InputModel, calculate().
- is_live sirf tab true jab uske unit + golden tests pass hon. Registry menu/list/sitemap
  me sirf is_live calculators dikhaye.
- Sab inputs Pydantic model me. Min/max/default/unit/step/label/help text Field me
  (frontend form yahin se banega).
- Reusable fields core/fields.py me. Same field 12 jagah copy nahi.
- Output hamesha standard shape: summary[], charts[], table[], notes[]. Builders core/result.py me.
- Calculation pure function: same input = same output. Koi side effect nahi.

Money aur math
- Paisa float me nahi. Decimal (ya integer paise). Float sirf scipy/numpy ke andar (XIRR),
  output Decimal me convert.
- API response me money values string ("1234567.89"), number nahi.
- Rounding policy ek jagah (core/money.py). Intermediate steps me round nahi, sirf final output pe.
- Har formula ke upar docstring: formula, assumptions, compounding frequency, source/reference.
- Shared math (CAGR, PMT, FV, annuity, compounding) finance_math.py me.
- Edge cases: 0 rate, 0 tenure, negative, bahut bada number, XIRR convergence fail, divide by zero.

Config aur rates
- Rate/slab/limit code me nahi. config/*.json me.
- Har rate ke saath: value, effective_from, source_url, last_verified.
- Config startup pe Pydantic se validate. Galat/missing ho toh server start hi na ho (fail fast).
- Tax: FY wise alag file (fy_2025_26.json, ...). Calculator FY parameter le, "current" hardcode nahi.
- Rates calculator ke response ke andar jayenge (value + source + last_verified).
  Alag rates endpoint nahi.

API
- Sab /api/v1/ ke andar. Endpoints sirf:
  GET /calculators, GET /calculators/{slug}, POST /calculators/{slug}, GET /health.
- Error ek standard format me: {code, message, details}. Stack trace kabhi user ko nahi.
- Validation errors human-friendly.
- Production me /docs, /redoc, /openapi.json band.
- CORS sirf apne frontend domain ke liye (env se).
- Rate limiting on. Request size limit on.
- Secrets sirf env me. .env.example repo me, .env nahi.
- Cache headers: metadata/list endpoints cacheable.

Python code quality
- Python 3.12+, type hints har jagah, mypy strict, ruff (lint+format).
- Function chhota (ek kaam). Class me SRP.
- Magic number nahi. Named constant ya config.
- Print nahi, logging. Input values me personal data ho toh log nahi.

## E. FRONTEND RULES
Allowed (sirf presentation)
- Layout, animation, charts render, theme, responsive.
- Display formatting: INR lakh/crore, %, date. Sirf lib/format/ me.
- Static UI text (button/nav labels) ek constants/i18n file me.
- Design tokens tailwind theme me. Component me hex code nahi.
Not allowed
- Finance math, rate, limit, default, min/max, calculator list, input label hardcode.
- Backend response ko modify/recalculate karna.
Structure
- Ek generic CalculatorPage + DynamicForm + ChartRenderer + DataTable + ResultSummary.
  Naya calculator = zero frontend code (jab tak special UI na chahiye).
- Special UI (XIRR dates, Income Tax regimes, Inflation categories) features/ me, sirf UI.
- ChartRenderer chart "type" se decide kare. Naya chart type = ek jagah add.
- Components dumb: props lo, UI do. Data fetching ek jagah (hooks + api client).
- Components me fetch() seedha nahi.
- Types backend OpenAPI se generate (openapi-typescript), local/CI script se. Prod ke
  /openapi.json se nahi (wo band hoga). Haath se type nahi likhna.
- TypeScript strict, "any" ban. ESLint + Prettier.
- Slider change pe debounce (300ms), AbortController se request cancel,
  loading/error/empty states har jagah.
- Accessibility: label, keyboard, contrast, aria. Mobile-first, 360px pe test.
- reduced-motion respect. Charts/animation lazy load.
Vite specifics
- Next.js ka koi convention/dependency nahi.
- Backend URL env se: VITE_API_BASE_URL. VITE_ variables public hote hain, secrets kabhi nahi.
- React Router. Direct URL refresh, back/forward, unknown URL ka 404 page kaam kare.
  Static host pe index.html fallback configure.
- Frontend change ke baad: cd frontend; npm run lint aur npm run build pass.
SEO
- Vite-compatible build-time prerender: calculator pages ka title, description, FAQ, content
  static HTML me ho.
- Metadata backend ke calculator.seo se aaye. sitemap.xml aur robots.txt build script
  (frontend/scripts) se registry se generate.
- Canonical URL, OpenGraph, structured data (FAQ schema).
- Build ke time backend cold start ho sakta hai: retry + wake step.
- Source maps production me off.

## F. ROUTES
API:
  GET  /api/v1/calculators              list + metadata (menu/home/sitemap)
  GET  /api/v1/calculators/{slug}       input schema + seo
  POST /api/v1/calculators/{slug}       calculate
  GET  /api/v1/health
Frontend (kebab-case, lowercase, English):
  /                                home
  /calculators/{slug}              e.g. /calculators/sip-calculator
  /category/{category-slug}        e.g. /category/investment
  /about, /methodology, /terms, /privacy    (terms/privacy placeholders)
  404 page
Slug ek baar tay hua toh badalna nahi (SEO). Badalna pade toh 301 redirect.
Future routes (login, user): /api/v1/user/* aur /account/*. Calculator routes ko nahi chhuenge.

## G. NAMING CONVENTIONS (lock)
Python: files/functions/vars snake_case | classes PascalCase | constants UPPER_SNAKE
  slug = "<name>-calculator" (sip-calculator, step-up-sip-calculator)
  file = sip.py / step_up_sip.py | class = SipCalculator / StepUpSipCalculator
  input = SipInput / StepUpSipInput
TypeScript: components PascalCase.tsx | hooks useXxx | utils camelCase | folders kebab-case | types PascalCase
API JSON: camelCase (Pydantic alias_generator). Python andar snake_case.
Config keys: snake_case. Files: fy_2025_26.json.
Booleans: is_/has_/can_ prefix. Functions verb se (calculate_emi, load_rates).
Kharab naam: data, temp, obj, val, x, helper, utils2, final_final.
Naam se pata chale kya hai aur unit kya hai (rate_percent, tenure_months).
Units naam ya docstring me clear: percent vs decimal, months vs years, rupees vs paise.

## H. TESTING
- Har calculator ke liye unit tests + golden tests (Product Owner ke verified examples, source link ke saath).
- Core math par 100% coverage target.
- Edge case tests (0, max, invalid).
- API tests: schema, validation, error format.
- Frontend: unit (formatters), component, 1-2 end-to-end