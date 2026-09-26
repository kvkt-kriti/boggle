async function loadOptions() {
  const [schools, majors] = await Promise.all([
    fetch("/api/schools").then((r) => r.json()),
    fetch("/api/majors").then((r) => r.json()),
  ]);

  const schoolSel = document.getElementById("school");
  schoolSel.innerHTML = '<option value="">Choose a college</option>';
  const top = schools.filter((s) => s.top20);
  const extra = schools.filter((s) => !s.top20);
  const addGroup = (label, items) => {
    if (!items.length) return;
    const group = document.createElement("optgroup");
    group.label = label;
    for (const s of items) {
      const opt = document.createElement("option");
      opt.value = s.code;
      opt.textContent = s.name;
      group.appendChild(opt);
    }
    schoolSel.appendChild(group);
  };
  addGroup("Top 20 public universities", top);
  addGroup("Also in Minerva", extra);

  const majorSel = document.getElementById("major");
  majorSel.innerHTML = '<option value="">Choose a major</option>';
  for (const m of majors) {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = m.name;
    majorSel.appendChild(opt);
  }
}

function showError(msg) {
  const el = document.getElementById("error");
  el.hidden = !msg;
  el.textContent = msg || "";
}

function renderResults(data) {
  const section = document.getElementById("results");
  const list = document.getElementById("results-list");
  const title = document.getElementById("results-title");
  const sub = document.getElementById("results-sub");
  const source = document.getElementById("results-source");

  title.textContent = `AP classes for ${data.school_name}`;
  const scoreBit = data.score ? ` at score ${data.score}` : "";
  sub.textContent = data.recommendations.length
    ? `${data.recommendations.length} exams that earn useful credit${scoreBit}.`
    : "No matching AP credit found for that combination yet.";

  list.innerHTML = "";
  data.recommendations.forEach((rec, i) => {
    const li = document.createElement("li");
    const courses = rec.courses?.length
      ? rec.courses.join(", ")
      : rec.award_raw || "Credit awarded";
    const credits =
      rec.credits == null ? "—" : Number(rec.credits).toString().replace(/\.0$/, "");
    li.innerHTML = `
      <div class="rank">${String(i + 1).padStart(2, "0")}</div>
      <div>
        <h3>${rec.ap_exam}</h3>
        <p>Score ${rec.min_score}+ → ${courses}</p>
      </div>
      <div class="credits">${credits}<small>credits</small></div>
    `;
    list.appendChild(li);
  });

  source.innerHTML = data.source_url
    ? `Source: <a href="${data.source_url}" target="_blank" rel="noopener">${data.source_url}</a>`
    : "";
  section.hidden = false;
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.getElementById("advisor-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  showError("");
  const school = document.getElementById("school").value;
  const major = document.getElementById("major").value;
  const score = document.getElementById("score").value;
  if (!school || !major) {
    showError("Choose both a college and a major.");
    return;
  }
  const btn = document.getElementById("go");
  btn.disabled = true;
  try {
    const params = new URLSearchParams({ school, major });
    if (score) params.set("score", score);
    const res = await fetch(`/api/recommend?${params}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    renderResults(data);
  } catch (err) {
    showError(err.message || String(err));
  } finally {
    btn.disabled = false;
  }
});

loadOptions().catch((err) => showError(err.message || String(err)));
