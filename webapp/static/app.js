const EMBLEM = `<svg viewBox="0 0 48 48" class="emblem" aria-hidden="true" fill="none">
  <circle cx="24" cy="24" r="22.5" stroke="currentColor" stroke-width="1.25" opacity="0.5"></circle>
  <path d="M24 12c-5 0-9 3.4-9 8.4 0 4 2.2 6.6 4 8.2v3.9c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5v-3.9c1.8-1.6 4-4.2 4-8.2 0-5-4-8.4-9-8.4Z" stroke="currentColor" stroke-width="1.25"></path>
  <circle cx="19.5" cy="20.5" r="2.6" stroke="currentColor" stroke-width="1.25"></circle>
  <circle cx="28.5" cy="20.5" r="2.6" stroke="currentColor" stroke-width="1.25"></circle>
  <circle cx="19.5" cy="20.5" r="0.9" fill="currentColor"></circle>
  <circle cx="28.5" cy="20.5" r="0.9" fill="currentColor"></circle>
  <path d="M23 23.4 24 25l1-1.6" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round"></path>
</svg>`;

const REL = { core: "Core for your major", strong: "Strong match", elective: "Nice-to-have" };

const state = {
  view: "landing",
  step: 0,
  schools: [],
  majors: [],
  collegeId: "",
  majorId: "",
  query: "",
  score: 0,
  plan: null,
  openExam: null,
  error: "",
};

const app = document.getElementById("app");

function esc(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function creditsLabel(n) {
  if (n == null || n === "") return "—";
  const num = Number(n);
  if (Number.isNaN(num)) return "—";
  return Number.isInteger(num) ? String(num) : String(num);
}

function courseText(courses, award) {
  if (courses && courses.length) return courses.join(", ");
  return award || "Credit awarded";
}

async function load() {
  const [schools, majors] = await Promise.all([
    fetch("/api/schools").then((r) => r.json()),
    fetch("/api/majors").then((r) => r.json()),
  ]);
  state.schools = schools;
  state.majors = majors;
  render();
}

function render() {
  if (state.view === "landing") app.innerHTML = landing();
  else if (state.view === "input") app.innerHTML = inputFlow();
  else app.innerHTML = results();
  bind();
}

function landing() {
  return `<main class="landing">
    <div class="landing-ground"></div>
    <img class="landing-photo" alt="Sunlit university quad with classical columns"
      src="https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=1900&h=1400&fit=crop&auto=format" />
    <div class="landing-shade"></div>
    <header>
      <div class="brand">${EMBLEM}<span>Minerva</span></div>
      <span class="eyebrow-right">AP credit advisor</span>
    </header>
    <div class="hero">
      <p class="kicker fade-in">For students aiming high</p>
      <h1 class="rise-in">Minerva</h1>
      <p class="lede rise-in" style="animation-delay:.1s">Which AP classes are actually worth taking for the college and major you want? We read the official credit charts, so you don’t have to.</p>
      <div class="cta-row rise-in" style="animation-delay:.2s">
        <button class="pill" id="start">Build my AP plan <span>→</span></button>
        <span class="fine">Top 20 public universities · free</span>
      </div>
    </div>
  </main>`;
}

function inputFlow() {
  const labels = ["College", "Major"];
  const steps = labels.map((l, i) => {
    const cls = i === state.step ? "on" : i < state.step ? "done" : "off";
    const line = i < labels.length - 1
      ? `<span class="step-line ${i < state.step ? "done" : ""}"></span>`
      : "";
    return `<span class="step-num ${cls}">${String(i + 1).padStart(2, "0")}</span>${line}`;
  }).join("");

  const body = state.step === 0 ? collegeStep() : majorStep();
  const can = state.step === 0 ? !!state.collegeId : !!state.majorId;
  return `<main class="flow">
    <header>
      <button class="brand" id="home" style="color:var(--primary)">${EMBLEM.replace('class="emblem"', 'class="emblem sm"')}<span>Minerva</span></button>
      <div class="steps">${steps}</div>
    </header>
    <div class="flow-body">
      <div class="fade-in">${body}</div>
      <div class="nav-row">
        <button class="linkish" id="prev">← ${state.step === 0 ? "Home" : "College"}</button>
        <button class="pill solid" id="next" ${can ? "" : "disabled"}>${state.step === 1 ? "Show my plan" : "Continue"} <span>→</span></button>
      </div>
      ${state.error ? `<p class="error">${esc(state.error)}</p>` : ""}
    </div>
  </main>`;
}

function collegeStep() {
  const q = state.query.toLowerCase();
  const filtered = state.schools.filter((c) =>
    c.name.toLowerCase().includes(q) || c.short.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)
  );
  const cards = filtered.map((c) => {
    const active = c.code === state.collegeId ? "active" : "";
    return `<button class="choice ${active}" data-college="${esc(c.code)}">
      <span><span class="name">${esc(c.short)}</span><span class="meta">${esc(c.location || c.name)}</span></span>
      <span class="check">✓</span>
    </button>`;
  }).join("");
  return `<p class="step-kicker">Step 1 of 2</p>
    <h2>Where are you aiming?</h2>
    <p class="sub">Choose the public university you have your eye on.</p>
    <input class="search" id="search" placeholder="Search schools…" value="${esc(state.query)}" />
    <div class="grid">${cards || `<p class="empty">No schools match “${esc(state.query)}”.</p>`}</div>`;
}

function majorStep() {
  const cards = state.majors.map((m, i) => {
    const active = m.id === state.majorId ? "active" : "";
    return `<button class="choice major ${active}" data-major="${esc(m.id)}">
      <span class="idx">${String(i + 1).padStart(2, "0")}</span>
      <span><span class="name">${esc(m.name)}</span><span class="meta">${esc(m.blurb)}</span></span>
    </button>`;
  }).join("");
  return `<p class="step-kicker">Step 2 of 2</p>
    <h2>What might you study?</h2>
    <p class="sub">Pick the intended major. You can change it later — nothing here is binding.</p>
    <div class="grid majors">${cards}</div>`;
}

function results() {
  const plan = state.plan;
  if (!plan) return `<main class="results"><p>Loading…</p></main>`;
  const scoreBit = state.score ? ` if you score ${state.score}` : "";
  const shownCredits = plan.exams.reduce((n, e) => n + Number(state.score ? (e.tiers.at(-1)?.credits || 0) : (e.credits || 0)), 0);
  const items = plan.exams.map((e, i) => {
    const open = state.openExam === e.ap_exam;
    const shown = state.score ? e.tiers[e.tiers.length - 1] : e.tiers[0];
    const more = !state.score && e.tiers.length > 1 && (e.max_credits || 0) > (e.credits || 0)
      ? ` · up to ${creditsLabel(e.max_credits)} at score ${e.tiers.at(-1).score}`
      : "";
    const courses = courseText(shown.courses, shown.award_raw);
    const label = state.score ? `At score ${shown.score}` : `Score ${e.min_score}+`;
    const tiers = e.tiers.map((t) => {
      const line = courseText(t.courses, t.award_raw);
      const cr = t.credits == null ? "" : ` · ${creditsLabel(t.credits)} credits`;
      return `<li>Score ${t.score}: ${esc(line)}${cr}</li>`;
    }).join("");
    const why = state.score
      ? `At ${esc(plan.short)}, a score of ${shown.score} on AP ${esc(e.ap_exam)} is published as ${esc(courses)}${shown.credits != null ? ` (${creditsLabel(shown.credits)} credits)` : ""}.`
      : `The lowest score ${esc(plan.short)} publishes for AP ${esc(e.ap_exam)} is ${e.min_score}, which awards ${esc(courseText(e.courses, e.award_raw))}${e.credits != null ? ` (${creditsLabel(e.credits)} credits)` : ""}. Higher scores are listed when the chart gives more.`;
    return `<li class="rise-in" style="animation-delay:${Math.min(i * 0.05, 0.5)}s">
      <button class="row" data-exam="${esc(e.ap_exam)}">
        <span class="rank">${String(i + 1).padStart(2, "0")}</span>
        <span>
          <span class="exam-line">
            <span class="exam-name">AP ${esc(e.ap_exam)}</span>
            <span class="badge ${esc(e.relevance)}">${esc(REL[e.relevance] || e.relevance)}</span>
          </span>
          <span class="award">${esc(label)} → ${esc(courses)}${esc(more)}</span>
        </span>
        <span class="side">
          <span class="credits"><b>${creditsLabel(shown.credits)}</b><small>credits</small></span>
          <span class="chev">${open ? "›" : "›"}</span>
        </span>
      </button>
      ${open ? `<div class="detail fade-in">
        <div class="panel">
          <h3>Published awards</h3>
          <ul>${tiers}</ul>
          <p class="foot">Taken from ${esc(plan.school_name)}’s AP chart. Not a generic estimate.</p>
        </div>
        <div class="panel">
          <h3>Why it’s here</h3>
          <p class="why">${why} ${e.relevance === "core" ? `It is one of the first exams Minerva matches to ${esc(plan.major_name)}.` : e.relevance === "strong" ? `It is a close match for ${esc(plan.major_name)} at this school.` : `It still earns credit here, with a looser tie to ${esc(plan.major_name)}.`}</p>
          ${plan.source_url ? `<a class="source-link" href="${esc(plan.source_url)}" target="_blank" rel="noopener">Official ${esc(plan.short)} chart ↗</a>` : ""}
        </div>
      </div>` : ""}
    </li>`;
  }).join("");

  const chips = [0, 3, 4, 5].map((n) => {
    const label = n ? String(n) : "Any";
    return `<button class="chip ${state.score === n ? "on" : ""}" data-score="${n}">${label}</button>`;
  }).join("");

  return `<main class="results">
    <header>
      <button class="brand" id="home" style="color:var(--primary)">${EMBLEM.replace('class="emblem"', 'class="emblem sm"')}<span>Minerva</span></button>
      <div class="header-actions">
        <button class="linkish print-btn" id="print">Print / PDF</button>
        <button class="ghost" id="edit">Edit choices</button>
      </div>
    </header>
    <div class="summary fade-in">
      <p class="label">Your AP plan</p>
      <h1>${esc(plan.major_name)} at ${esc(plan.short)}</h1>
      <p class="desc">${plan.exams.length} AP exams worth taking${esc(scoreBit)} — about <strong>${creditsLabel(shownCredits)} credit hours</strong> at the score shown, using ${esc(plan.school_name)}’s published chart.</p>
      <div class="score-row"><span>Expected score</span>${chips}</div>
    </div>
    <ol class="plan">${items}<li class="cap"></li></ol>
    <div class="trust">
      <p>Every course and credit on this page comes from ${esc(plan.school_name)}’s published AP chart. Policies change by year and program, so confirm on the official source before you register.</p>
      ${plan.source_url ? `<a class="pill solid" href="${esc(plan.source_url)}" target="_blank" rel="noopener">View ${esc(plan.short)} source ↗</a>` : ""}
    </div>
  </main>`;
}

function bind() {
  document.getElementById("start")?.addEventListener("click", () => {
    state.view = "input";
    state.step = 0;
    state.error = "";
    render();
  });
  document.getElementById("home")?.addEventListener("click", reset);
  document.getElementById("prev")?.addEventListener("click", () => {
    if (state.step === 0) reset();
    else { state.step = 0; render(); }
  });
  document.getElementById("next")?.addEventListener("click", async () => {
    if (state.step === 0) {
      if (!state.collegeId) return;
      state.step = 1;
      render();
      return;
    }
    if (!state.majorId) return;
    await fetchPlan();
  });
  document.getElementById("search")?.addEventListener("input", (e) => {
    state.query = e.target.value;
    const el = document.getElementById("search");
    const pos = el.selectionStart;
    render();
    const again = document.getElementById("search");
    if (again) {
      again.focus();
      again.setSelectionRange(pos, pos);
    }
  });
  document.querySelectorAll("[data-college]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.collegeId = btn.dataset.college;
      render();
    });
  });
  document.querySelectorAll("[data-major]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.majorId = btn.dataset.major;
      render();
    });
  });
  document.getElementById("edit")?.addEventListener("click", () => {
    state.view = "input";
    state.step = 0;
    render();
  });
  document.getElementById("print")?.addEventListener("click", () => window.print());
  document.querySelectorAll("[data-exam]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const exam = btn.dataset.exam;
      state.openExam = state.openExam === exam ? null : exam;
      render();
    });
  });
  document.querySelectorAll("[data-score]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      state.score = Number(btn.dataset.score);
      await fetchPlan();
    });
  });
}

function reset() {
  state.view = "landing";
  state.step = 0;
  state.collegeId = "";
  state.majorId = "";
  state.score = 0;
  state.query = "";
  state.plan = null;
  state.openExam = null;
  state.error = "";
  render();
}

async function fetchPlan() {
  state.error = "";
  const params = new URLSearchParams({ school: state.collegeId, major: state.majorId });
  if (state.score) params.set("score", String(state.score));
  const res = await fetch(`/api/plan?${params}`);
  const data = await res.json();
  if (!res.ok) {
    state.error = data.error || "Could not build a plan.";
    state.view = "input";
    render();
    return;
  }
  const major = state.majors.find((m) => m.id === state.majorId);
  data.major_name = major ? major.name : state.majorId;
  state.plan = data;
  state.view = "results";
  state.openExam = null;
  render();
}

load().catch((err) => {
  app.innerHTML = `<p class="error" style="padding:2rem">${esc(err.message || err)}</p>`;
});
