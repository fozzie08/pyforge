/* PyForge app: routing, views and the problem workspace. */
(function () {
  "use strict";

  var CONTENT = window.PYFORGE_CONTENT;
  var MODULES = CONTENT.modules;
  var PROBLEMS = CONTENT.problems;
  var esc = MD.escapeHtml;
  var app = document.getElementById("app");

  // Hard stops for code that never finishes. The judge also enforces a
  // per-test limit (2 s by default) and reports slower tests as TLE.
  var RUN_TIMEOUT_MS = 15000;
  var SUBMIT_TIMEOUT_MS = 30000;
  var SCRIPT_TIMEOUT_MS = 8000;
  var CASE_GRACE_MS = 1500; // slack on top of the per-test limit before the worker is stopped

  // -------------------------------------------------------------------------
  // Content indexes
  // -------------------------------------------------------------------------

  var LESSONS = {};
  var LESSON_ORDER = [];
  var EXERCISE_ORDER = [];
  MODULES.forEach(function (m) {
    m.lessons.forEach(function (l, i) {
      l.module = m;
      l.index = i;
      LESSONS[l.id] = l;
      LESSON_ORDER.push(l);
      l.exercises.forEach(function (id) { EXERCISE_ORDER.push(id); });
    });
  });
  var CHALLENGE_ORDER = Object.keys(PROBLEMS).filter(function (id) { return PROBLEMS[id].kind === "challenge"; })
    .sort(function (a, b) { return PROBLEMS[a].number - PROBLEMS[b].number; });
  var MODULE_BY_ID = {};
  MODULES.forEach(function (m) { MODULE_BY_ID[m.id] = m; });

  // -------------------------------------------------------------------------
  // Progress storage (this browser only)
  // -------------------------------------------------------------------------

  var Store = (function () {
    var KEY = "pyforge:v1";
    function blank() {
      return { solved: {}, code: {}, subs: {}, visited: {}, activity: {}, revealed: {}, cases: {}, layout: {}, theme: null };
    }
    var store = { d: blank() };
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) store.d = Object.assign(blank(), JSON.parse(raw));
    } catch (e) { /* storage unavailable: progress lasts for this visit only */ }
    var timer = null;
    store.flush = function () {
      clearTimeout(timer);
      try { localStorage.setItem(KEY, JSON.stringify(store.d)); } catch (e) { /* ignore */ }
    };
    store.save = function () { clearTimeout(timer); timer = setTimeout(store.flush, 300); };
    store.reset = function () { var theme = store.d.theme; store.d = blank(); store.d.theme = theme; store.flush(); };
    store.replace = function (data) { store.d = Object.assign(blank(), data); store.flush(); };
    window.addEventListener("beforeunload", store.flush);
    return store;
  })();

  function isSolved(id) { return !!Store.d.solved[id]; }
  function problemStatus(id) {
    if (isSolved(id)) return "solved";
    return (Store.d.subs[id] || []).length ? "attempted" : "todo";
  }
  function lessonStats(l) {
    var done = l.exercises.filter(isSolved).length;
    return { done: done, total: l.exercises.length, complete: done === l.exercises.length };
  }
  function lessonStatus(l) {
    var s = lessonStats(l);
    if (s.complete) return "solved";
    return Store.d.visited[l.id] || s.done ? "attempted" : "todo";
  }
  function moduleStats(m) {
    var lessonsDone = m.lessons.filter(function (l) { return lessonStats(l).complete; }).length;
    var chSolved = m.challenges.filter(isSolved).length;
    return { lessonsDone: lessonsDone, lessons: m.lessons.length, chSolved: chSolved, challenges: m.challenges.length,
      complete: lessonsDone === m.lessons.length && chSolved === m.challenges.length };
  }
  function totals() {
    var t = { lessons: LESSON_ORDER.length, lessonsDone: 0, exercises: EXERCISE_ORDER.length, exercisesDone: 0,
      challenges: CHALLENGE_ORDER.length, challengesDone: 0, byDiff: { Easy: [0, 0], Medium: [0, 0], Hard: [0, 0] } };
    LESSON_ORDER.forEach(function (l) { if (lessonStats(l).complete) t.lessonsDone++; });
    EXERCISE_ORDER.forEach(function (id) { if (isSolved(id)) t.exercisesDone++; });
    CHALLENGE_ORDER.forEach(function (id) {
      var d = PROBLEMS[id].difficulty;
      t.byDiff[d][1]++;
      if (isSolved(id)) { t.challengesDone++; t.byDiff[d][0]++; }
    });
    return t;
  }

  function nextStep() {
    for (var i = 0; i < MODULES.length; i++) {
      var m = MODULES[i];
      for (var j = 0; j < m.lessons.length; j++) {
        var l = m.lessons[j];
        if (!Store.d.visited[l.id]) return { kind: "lesson", lesson: l, module: m };
        var ex = l.exercises.filter(function (id) { return !isSolved(id); })[0];
        if (ex) return { kind: "exercise", problem: PROBLEMS[ex], lesson: l, module: m };
      }
      var ch = m.challenges.filter(function (id) { return !isSolved(id); })[0];
      if (ch) return { kind: "challenge", problem: PROBLEMS[ch], module: m };
    }
    return null;
  }

  function dayKey(date) {
    var d = date || new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function streak() {
    var count = 0;
    var d = new Date();
    if (!Store.d.activity[dayKey(d)]) d.setDate(d.getDate() - 1);
    while (Store.d.activity[dayKey(d)]) { count++; d.setDate(d.getDate() - 1); }
    return count;
  }

  // -------------------------------------------------------------------------
  // Small helpers
  // -------------------------------------------------------------------------

  var ICON = {
    solved: '<svg viewBox="0 0 20 20" aria-label="Solved"><circle cx="10" cy="10" r="8.5" fill="currentColor"/><path d="M6 10.4l2.6 2.6L14.2 7.4" fill="none" stroke="var(--surface)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    attempted: '<svg viewBox="0 0 20 20" aria-label="Attempted"><circle cx="10" cy="10" r="7.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 2.5a7.5 7.5 0 0 1 0 15z" fill="currentColor"/></svg>',
    todo: '<svg viewBox="0 0 20 20" aria-label="Not started"><circle cx="10" cy="10" r="7.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    lock: '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    play: '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" fill="currentColor"/></svg>',
    left: '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M10 3L5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    right: '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  function statusIcon(status) {
    return '<span class="status-icon st-' + status + '">' + ICON[status] + "</span>";
  }
  function diffLabel(d) { return '<span class="diff diff-' + d + '">' + d + "</span>"; }
  function pad2(n) { return String(n).padStart(2, "0"); }
  function timeAgo(ts) {
    var s = (Date.now() - ts) / 1000;
    if (s < 60) return "just now";
    if (s < 3600) return Math.floor(s / 60) + " min ago";
    if (s < 86400) return Math.floor(s / 3600) + " h ago";
    var days = Math.floor(s / 86400);
    return days === 1 ? "yesterday" : days + " days ago";
  }
  function problemTitle(p) { return p.kind === "challenge" ? p.number + ". " + p.title : p.title; }
  function isMac() { return /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent); }
  var MOD = isMac() ? "⌘" : "Ctrl";

  var toastTimer = null;
  function toast(msg) {
    var el = document.getElementById("toast");
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.hidden = true; }, 2800);
  }

  function debounce(fn, ms) {
    var t = null;
    return function () {
      var args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, args); }, ms);
    };
  }

  function makeEditor(host, value, extra) {
    var tabToSpaces = function (cm) {
      if (cm.somethingSelected()) { cm.indentSelection("add"); return; }
      var col = cm.getCursor().ch;
      cm.replaceSelection(" ".repeat(4 - (col % 4)), "end");
    };
    var keys = {
      Tab: tabToSpaces,
      "Shift-Tab": function (cm) { cm.indentSelection("subtract"); },
      "Cmd-/": "toggleComment",
      "Ctrl-/": "toggleComment",
    };
    Object.assign(keys, (extra && extra.keys) || {});
    return CodeMirror(host, Object.assign({
      value: value,
      mode: { name: "python", version: 3, singleLineStringErrors: false },
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      matchBrackets: true,
      autoCloseBrackets: true,
      extraKeys: keys,
    }, (extra && extra.options) || {}));
  }

  // -------------------------------------------------------------------------
  // Python runtime
  // -------------------------------------------------------------------------

  var runner = new PyRunner(window.PYFORGE_HARNESS);
  var pill = document.getElementById("runtime-pill");
  var PILL_TEXT = { idle: "Python idle", loading: "Starting Python…", ready: "Python ready", busy: "Running…", error: "Python unavailable" };
  runner.onState(function (state, detail) {
    pill.dataset.state = state;
    pill.querySelector(".label").textContent = PILL_TEXT[state] || state;
    pill.title = detail || "Python runs in your browser using Pyodide";
  });

  // -------------------------------------------------------------------------
  // Theme
  // -------------------------------------------------------------------------

  function applyTheme() {
    if (Store.d.theme) document.documentElement.setAttribute("data-theme", Store.d.theme);
    else document.documentElement.removeAttribute("data-theme");
  }
  applyTheme();
  document.getElementById("theme-toggle").addEventListener("click", function () {
    var current = Store.d.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    Store.d.theme = current === "dark" ? "light" : "dark";
    Store.save();
    applyTheme();
  });

  // -------------------------------------------------------------------------
  // Router
  // -------------------------------------------------------------------------

  var currentView = null;

  function route() {
    if (currentView && currentView.destroy) currentView.destroy();
    currentView = null;
    app.classList.remove("app-fixed");
    var hash = location.hash.replace(/^#\/?/, "");
    var parts = hash.split("/");
    var navKey = "learn";
    if (parts[0] === "lesson" && parts[1]) {
      currentView = viewLesson(decodeURIComponent(parts[1]));
    } else if (parts[0] === "problem" && parts[1]) {
      var p = PROBLEMS[decodeURIComponent(parts[1])];
      navKey = p && p.kind === "exercise" ? "learn" : "problems";
      currentView = viewProblem(decodeURIComponent(parts[1]));
    } else if (parts[0] === "problems") {
      navKey = "problems";
      currentView = viewProblems();
    } else if (parts[0] === "progress") {
      navKey = "progress";
      currentView = viewProgress();
    } else {
      currentView = viewLearn();
    }
    document.querySelectorAll(".nav a").forEach(function (a) {
      a.classList.toggle("active", a.dataset.nav === navKey);
    });
    app.scrollTop = 0;
  }
  window.addEventListener("hashchange", route);

  function notFound(what) {
    app.innerHTML = '<div class="page"><h1>Not found</h1><p class="muted">That ' + what +
      ' doesn\'t exist. It may have been renamed.</p><p><a class="btn" href="#/">Back to the learning path</a></p></div>';
    return null;
  }

  // -------------------------------------------------------------------------
  // Learn (home)
  // -------------------------------------------------------------------------

  function viewLearn() {
    var t = totals();
    var next = nextStep();
    var nextHtml;
    if (!next) {
      nextHtml = '<span class="eyebrow">All done</span><h2>You finished every lesson and challenge.</h2>' +
        '<p class="muted">Revisit the Hard problems, or try solving earlier ones a different way.</p>' +
        '<a class="btn btn-primary" href="#/problems">Browse problems</a>';
    } else if (next.kind === "lesson") {
      nextHtml = '<span class="eyebrow">Up next · Module ' + next.module.number + "</span><h2>" + esc(next.lesson.title) + "</h2>" +
        '<p class="muted" style="margin:0">' + esc(next.lesson.summary) + "</p>" +
        '<a class="btn btn-primary" href="#/lesson/' + next.lesson.id + '">Start lesson</a>';
    } else if (next.kind === "exercise") {
      nextHtml = '<span class="eyebrow">Up next · Practice</span><h2>' + esc(next.problem.title) + "</h2>" +
        '<p class="muted" style="margin:0">An exercise from “' + esc(next.lesson.title) + "”.</p>" +
        '<a class="btn btn-primary" href="#/problem/' + next.problem.id + '">Solve exercise</a>';
    } else {
      nextHtml = '<span class="eyebrow">Up next · ' + esc(next.module.challenge_title) + "</span><h2>" + esc(problemTitle(next.problem)) + "</h2>" +
        '<p class="muted" style="margin:0">' + diffLabel(next.problem.difficulty) + " · combines " + esc(next.problem.tags.slice(0, 3).join(", ")) + "</p>" +
        '<a class="btn btn-primary" href="#/problem/' + next.problem.id + '">Take the challenge</a>';
    }

    var html = '<div class="page">' +
      '<section class="welcome"><div class="welcome-main">' +
      '<span class="eyebrow">Python practice · runs in your browser</span>' +
      "<h1>Learn a technique, try it yourself, then prove it.</h1>" +
      "<p>Every lesson walks through a skill with examples you can run and edit, then hands you exercises to solve. " +
      "Each module ends with a checkpoint: LeetCode-style problems that combine everything so far, judged against hidden tests.</p>" +
      '<div class="stat-row">' +
      '<div class="stat"><b>' + t.lessonsDone + "/" + t.lessons + "</b><span>lessons complete</span></div>" +
      '<div class="stat"><b>' + t.exercisesDone + "/" + t.exercises + "</b><span>exercises solved</span></div>" +
      '<div class="stat"><b>' + t.challengesDone + "/" + t.challenges + "</b><span>challenges solved</span></div>" +
      "</div></div>" +
      '<aside class="continue-card">' + nextHtml + "</aside></section>" +
      '<div class="path">' + MODULES.map(renderModule).join("") + "</div></div>";
    app.innerHTML = html;
    return null;
  }

  function renderModule(m) {
    var s = moduleStats(m);
    var lessons = m.lessons.map(function (l) {
      var ls = lessonStats(l);
      var dots = l.exercises.map(function (id) { return "<i" + (isSolved(id) ? ' class="on"' : "") + "></i>"; }).join("");
      return '<li><a class="lesson-row" href="#/lesson/' + l.id + '">' + statusIcon(lessonStatus(l)) +
        '<span><span class="title">' + esc(l.title) + '</span><span class="summary">' + esc(l.summary) + "</span></span>" +
        '<span class="ex-dots" title="Exercises solved">' + dots + "<small>" + ls.done + "/" + ls.total + "</small></span></a></li>";
    }).join("");
    var cps = m.challenges.map(function (id) {
      var p = PROBLEMS[id];
      return '<a class="cp-item" href="#/problem/' + id + '">' + statusIcon(problemStatus(id)) +
        "<span>" + esc(problemTitle(p)) + "</span>" + diffLabel(p.difficulty) + "</a>";
    }).join("");
    var note = s.lessonsDone < s.lessons ? "Best tackled after this module's lessons" : s.chSolved === s.challenges ? "Checkpoint cleared" : "You're ready for this";
    return '<section class="module' + (s.complete ? " done" : "") + '" id="module-' + m.id + '">' +
      '<div class="module-num">' + pad2(m.number) + "</div><div>" +
      '<div class="module-head"><h2>' + esc(m.title) + '</h2><span class="muted">' + s.lessonsDone + "/" + s.lessons +
      " lessons · " + s.chSolved + "/" + s.challenges + " challenges</span></div>" +
      '<p class="module-blurb">' + esc(m.blurb) + "</p>" +
      '<ol class="lesson-list">' + lessons + "</ol>" +
      '<div class="checkpoint"><div class="checkpoint-head"><h3>' + esc(m.challenge_title) + '</h3><span class="cp-note">' + note + "</span></div>" +
      "<p>" + esc(m.challenge_blurb) + '</p><div class="checkpoint-list">' + cps + "</div></div>" +
      "</div></section>";
  }

  // -------------------------------------------------------------------------
  // Lesson reader
  // -------------------------------------------------------------------------

  function viewLesson(id) {
    var L = LESSONS[id];
    if (!L) return notFound("lesson");
    Store.d.visited[id] = Store.d.visited[id] || Date.now();
    Store.save();
    runner.start();

    var m = L.module;
    var headings = [];
    var examples = [];
    var body = MD.render(L.body, {
      onHeading: function (level, text, hid) { if (level === 2) headings.push({ text: text, id: hid }); },
      onPython: function (code) {
        var i = examples.length;
        examples.push(code);
        return '<div class="example" data-ex="' + i + '"><div class="example-bar"><span class="label">example ' + (i + 1) + "</span>" +
          '<button class="btn btn-sm btn-ghost" type="button" data-act="reset" hidden>Reset</button>' +
          '<button class="btn btn-sm btn-primary" type="button" data-act="run" title="Run (' + MOD + ' + Enter)">' + ICON.play + " Run</button></div>" +
          '<div class="example-editor"></div><pre class="example-out" hidden></pre></div>';
      },
    });

    var pos = LESSON_ORDER.indexOf(L);
    var prev = LESSON_ORDER[pos - 1];
    var next = LESSON_ORDER[pos + 1];
    var lastInModule = L.index === m.lessons.length - 1;

    var side = '<aside class="lesson-side"><h4>Module ' + m.number + " · " + esc(m.title) + "</h4><ol>" +
      m.lessons.map(function (l) {
        return '<li><a href="#/lesson/' + l.id + '"' + (l.id === id ? ' class="current"' : "") + ">" + statusIcon(lessonStatus(l)) +
          "<span>" + esc(l.title) + "</span></a></li>";
      }).join("") +
      '<li><a href="#/problem/' + m.challenges[0] + '">' + statusIcon(moduleStats(m).chSolved === m.challenges.length ? "solved" : "todo") +
      "<span>Checkpoint " + m.number + "</span></a></li></ol>" +
      (headings.length ? '<h4>On this page</h4><ul class="toc">' + headings.map(function (h) {
        return '<li><a href="#/lesson/' + id + '" data-scroll="' + h.id + '">' + esc(h.text) + "</a></li>";
      }).join("") + '<li><a href="#/lesson/' + id + '" data-scroll="practice">Your turn</a></li></ul>' : "") +
      "</aside>";

    var practice = '<section class="practice" id="practice"><span class="eyebrow">Your turn</span><h2>Practice exercises</h2>' +
      "<p>Solve these to complete the lesson. Each one opens in the editor with examples, hidden tests and hints.</p>" +
      '<div class="practice-grid">' + L.exercises.map(function (pid, i) {
        var p = PROBLEMS[pid];
        return '<a class="practice-card" href="#/problem/' + pid + '"><div class="top"><span class="eyebrow">Exercise ' + (i + 1) +
          "</span>" + statusIcon(problemStatus(pid)) + "</div><h3>" + esc(p.title) + "</h3><p>" +
          esc(p.description.split("\n")[0].replace(/[`*]/g, "").slice(0, 110)) + "…</p></a>";
      }).join("") + "</div>" +
      '<nav class="lesson-nav">' +
      (prev ? '<a class="btn" href="#/lesson/' + prev.id + '">' + ICON.left + " " + esc(prev.title) + "</a>" : "<span></span>") +
      (lastInModule ? '<a class="btn btn-primary" href="#/problem/' + m.challenges[0] + '">Checkpoint ' + m.number + " " + ICON.right + "</a>"
        : next ? '<a class="btn btn-primary" href="#/lesson/' + next.id + '">' + esc(next.title) + " " + ICON.right + "</a>" : "") +
      "</nav></section>";

    app.innerHTML = '<div class="lesson-layout">' + side + '<article class="lesson-main"><header>' +
      '<span class="eyebrow">Module ' + m.number + " · Lesson " + (L.index + 1) + " of " + m.lessons.length + "</span>" +
      "<h1>" + esc(L.title) + "</h1><p>" + esc(L.summary) + '</p><div class="meta">About ' + L.minutes + " minutes · " +
      examples.length + " runnable examples · " + L.exercises.length + " exercises</div></header>" +
      '<div class="prose">' + body + "</div>" + practice + "</article></div>";

    app.querySelectorAll("[data-scroll]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var target = document.getElementById(a.dataset.scroll);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    var editors = [];
    app.querySelectorAll(".example").forEach(function (box) {
      var i = Number(box.dataset.ex);
      var original = examples[i];
      var out = box.querySelector(".example-out");
      var runBtn = box.querySelector('[data-act="run"]');
      var resetBtn = box.querySelector('[data-act="reset"]');
      var cm;
      var run = function () {
        runBtn.disabled = true;
        out.hidden = false;
        out.innerHTML = '<span class="empty">' + (runner.state === "ready" ? "Running…" : "Starting Python (the first run takes a few seconds)…") + "</span>";
        runner.run({ action: "script", code: cm.getValue(), setup: L.setup }, { timeoutMs: SCRIPT_TIMEOUT_MS }).then(function (res) {
          runBtn.disabled = false;
          if (res.status === "Time Limit Exceeded") {
            out.innerHTML = '<span class="err">Stopped after ' + SCRIPT_TIMEOUT_MS / 1000 + " seconds. Is there a loop that never ends?</span>";
            return;
          }
          if (res.status === "Internal Error") {
            out.innerHTML = '<span class="err">' + esc(res.error) + "</span>";
            return;
          }
          var html = esc(res.stdout || "");
          if (res.error) html += (html ? "\n" : "") + '<span class="err">' + esc(res.error) + "</span>";
          out.innerHTML = html || '<span class="empty">(no output: add a print() to see results)</span>';
        }, function (err) {
          runBtn.disabled = false;
          out.innerHTML = '<span class="err">Python couldn\'t start: ' + esc((err && err.message) || String(err)) + "</span>";
        });
      };
      var runKey = function () { run(); };
      cm = makeEditor(box.querySelector(".example-editor"), original, {
        options: { viewportMargin: Infinity },
        keys: { "Cmd-Enter": runKey, "Ctrl-Enter": runKey },
      });
      cm.on("change", function () { resetBtn.hidden = cm.getValue() === original; });
      runBtn.addEventListener("click", run);
      resetBtn.addEventListener("click", function () { cm.setValue(original); out.hidden = true; });
      editors.push(cm);
    });
    return null;
  }

  // -------------------------------------------------------------------------
  // Problems list
  // -------------------------------------------------------------------------

  var filters = { q: "", diff: "all", status: "all", tag: "all", exercises: false };

  function viewProblems() {
    var t = totals();
    var tags = {};
    Object.keys(PROBLEMS).forEach(function (id) { PROBLEMS[id].tags.forEach(function (tag) { tags[tag] = true; }); });
    var tagOptions = Object.keys(tags).sort().map(function (tag) {
      return '<option value="' + esc(tag) + '"' + (filters.tag === tag ? " selected" : "") + ">" + esc(tag) + "</option>";
    }).join("");
    var opt = function (v, label, cur) { return '<option value="' + v + '"' + (cur === v ? " selected" : "") + ">" + label + "</option>"; };

    app.innerHTML = '<div class="page"><div class="problems-head"><div><span class="eyebrow">Challenge library</span><h1>Problems</h1></div>' +
      '<div class="solved-summary"><span><b>' + t.challengesDone + "</b>/" + t.challenges + " solved</span>" +
      '<span class="diff-Easy">Easy <b>' + t.byDiff.Easy[0] + "</b>/" + t.byDiff.Easy[1] + "</span>" +
      '<span class="diff-Medium">Medium <b>' + t.byDiff.Medium[0] + "</b>/" + t.byDiff.Medium[1] + "</span>" +
      '<span class="diff-Hard">Hard <b>' + t.byDiff.Hard[0] + "</b>/" + t.byDiff.Hard[1] + "</span></div></div>" +
      '<div class="filters">' +
      '<input type="search" id="f-q" placeholder="Search problems" aria-label="Search problems" value="' + esc(filters.q) + '">' +
      '<select id="f-diff" aria-label="Difficulty">' + opt("all", "All difficulties", filters.diff) + opt("Easy", "Easy", filters.diff) +
      opt("Medium", "Medium", filters.diff) + opt("Hard", "Hard", filters.diff) + "</select>" +
      '<select id="f-status" aria-label="Status">' + opt("all", "Any status", filters.status) + opt("todo", "Not started", filters.status) +
      opt("attempted", "Attempted", filters.status) + opt("solved", "Solved", filters.status) + "</select>" +
      '<select id="f-tag" aria-label="Skill">' + opt("all", "All skills", filters.tag) + tagOptions + "</select>" +
      '<label class="check"><input type="checkbox" id="f-ex"' + (filters.exercises ? " checked" : "") + "> Include lesson exercises</label>" +
      '<button class="btn" type="button" id="f-random">Pick one for me</button>' +
      "</div>" +
      '<div class="ptable-wrap"><table class="ptable"><thead><tr><th class="col-status">Status</th><th>Title</th>' +
      '<th class="col-tags">Skills combined</th><th class="col-module">Section</th><th class="col-diff">Difficulty</th></tr></thead>' +
      '<tbody id="ptable-body"></tbody></table></div></div>';

    var body = document.getElementById("ptable-body");

    function filtered() {
      var ids = filters.exercises ? CHALLENGE_ORDER.concat(EXERCISE_ORDER) : CHALLENGE_ORDER;
      var q = filters.q.trim().toLowerCase();
      return ids.filter(function (id) {
        var p = PROBLEMS[id];
        if (filters.diff !== "all" && p.difficulty !== filters.diff) return false;
        if (filters.status !== "all" && problemStatus(id) !== filters.status) return false;
        if (filters.tag !== "all" && p.tags.indexOf(filters.tag) < 0) return false;
        if (q && (p.title + " " + p.tags.join(" ") + " " + (p.number || "")).toLowerCase().indexOf(q) < 0) return false;
        return true;
      });
    }

    function draw() {
      var ids = filtered();
      if (!ids.length) {
        body.innerHTML = '<tr><td colspan="5" class="empty-state">No problems match these filters.</td></tr>';
        return;
      }
      body.innerHTML = ids.map(function (id) {
        var p = PROBLEMS[id];
        var section = p.kind === "challenge" ? "Checkpoint " + MODULE_BY_ID[p.module].number : "Lesson: " + LESSONS[p.lesson].title;
        var tagsHtml = (p.tags.length ? p.tags : ["Practice"]).slice(0, 3).map(function (tag) { return '<span class="chip">' + esc(tag) + "</span>"; }).join("");
        return '<tr data-id="' + id + '"><td class="col-status">' + statusIcon(problemStatus(id)) + "</td>" +
          '<td class="title-cell"><a href="#/problem/' + id + '">' + (p.number ? '<span class="num">' + p.number + ".</span>" : "") + esc(p.title) + "</a></td>" +
          '<td class="col-tags"><div class="tags">' + tagsHtml + "</div></td>" +
          '<td class="col-module muted">' + esc(section) + "</td>" +
          '<td class="col-diff">' + diffLabel(p.difficulty) + "</td></tr>";
      }).join("");
    }

    body.addEventListener("click", function (e) {
      var row = e.target.closest("tr[data-id]");
      if (row && !e.target.closest("a")) location.hash = "#/problem/" + row.dataset.id;
    });
    document.getElementById("f-q").addEventListener("input", function (e) { filters.q = e.target.value; draw(); });
    document.getElementById("f-diff").addEventListener("change", function (e) { filters.diff = e.target.value; draw(); });
    document.getElementById("f-status").addEventListener("change", function (e) { filters.status = e.target.value; draw(); });
    document.getElementById("f-tag").addEventListener("change", function (e) { filters.tag = e.target.value; draw(); });
    document.getElementById("f-ex").addEventListener("change", function (e) { filters.exercises = e.target.checked; draw(); });
    document.getElementById("f-random").addEventListener("click", function () {
      var pool = filtered().filter(function (id) { return !isSolved(id); });
      if (!pool.length) pool = filtered();
      if (!pool.length) { toast("No problems match these filters."); return; }
      location.hash = "#/problem/" + pool[Math.floor(Math.random() * pool.length)];
    });
    draw();
    return null;
  }

  // -------------------------------------------------------------------------
  // Progress
  // -------------------------------------------------------------------------

  function viewProgress() {
    var t = totals();
    var C = 2 * Math.PI * 52;
    var offset = 0;
    var arcs = ["Easy", "Medium", "Hard"].map(function (d) {
      var len = (t.byDiff[d][0] / t.challenges) * C;
      var arc = len > 0 ? '<circle cx="66" cy="66" r="52" fill="none" stroke="var(--' + d.toLowerCase() + ')" stroke-width="10" stroke-dasharray="' +
        len.toFixed(2) + " " + (C - len).toFixed(2) + '" stroke-dashoffset="' + (-offset).toFixed(2) + '"/>' : "";
      offset += len;
      return arc;
    }).join("");

    var diffRows = ["Easy", "Medium", "Hard"].map(function (d) {
      var s = t.byDiff[d];
      return '<div class="diff-bar-row"><span class="diff diff-' + d + '">' + d + '</span><div class="bar ' + d.toLowerCase() +
        '"><span style="width:' + (s[1] ? (100 * s[0] / s[1]) : 0) + '%"></span></div><span class="n">' + s[0] + " / " + s[1] + "</span></div>";
    }).join("");

    // Activity heatmap: the last 20 weeks, one column per week.
    var weeks = 20;
    var start = new Date();
    start.setDate(start.getDate() - start.getDay() - (weeks - 1) * 7);
    var cells = "";
    var totalSubs = 0;
    for (var i = 0; i < weeks * 7; i++) {
      var d = new Date(start);
      d.setDate(start.getDate() + i);
      var n = Store.d.activity[dayKey(d)] || 0;
      totalSubs += n;
      var lvl = n === 0 ? "" : n === 1 ? "l1" : n <= 3 ? "l2" : "l3";
      var future = d > new Date();
      cells += "<i" + (lvl ? ' class="' + lvl + '"' : "") + (future ? ' style="visibility:hidden"' : "") +
        ' title="' + dayKey(d) + ": " + n + " submission" + (n === 1 ? "" : "s") + '"></i>';
    }

    var moduleRows = MODULES.map(function (m) {
      var s = moduleStats(m);
      var done = s.lessonsDone + s.chSolved;
      var all = s.lessons + s.challenges;
      return '<div class="module-progress-row"><a href="#/lesson/' + m.lessons[0].id + '">' + m.number + ". " + esc(m.title) + "</a>" +
        '<div class="bar ok"><span style="width:' + (100 * done / all) + '%"></span></div><span class="n">' + done + " / " + all + "</span></div>";
    }).join("");

    var recent = [];
    Object.keys(Store.d.subs).forEach(function (id) {
      if (!PROBLEMS[id]) return;
      Store.d.subs[id].forEach(function (s) { recent.push({ id: id, s: s }); });
    });
    recent.sort(function (a, b) { return b.s.at - a.s.at; });
    var recentHtml = recent.length ? '<ul class="recent">' + recent.slice(0, 8).map(function (r) {
      var ok = r.s.status === "Accepted";
      return '<li><a href="#/problem/' + r.id + '">' + esc(problemTitle(PROBLEMS[r.id])) + '</a><span class="' + (ok ? "s-Accepted" : "s-bad") + '">' +
        esc(r.s.status) + '</span><span class="muted">' + timeAgo(r.s.at) + "</span></li>";
    }).join("") + "</ul>" : '<p class="muted">No submissions yet. Solve an exercise to get started.</p>';

    app.innerHTML = '<div class="page"><div class="problems-head"><div><span class="eyebrow">Your progress</span><h1>Progress</h1></div></div>' +
      '<div class="progress-grid">' +
      '<section class="card span-7"><h2>Challenges solved</h2><div class="ring-wrap"><div class="ring"><svg viewBox="0 0 132 132">' +
      '<circle cx="66" cy="66" r="52" fill="none" stroke="var(--surface-3)" stroke-width="10"/>' + arcs + "</svg>" +
      '<div class="center"><b>' + t.challengesDone + "</b><span>of " + t.challenges + "</span></div></div>" +
      '<div class="diff-bars">' + diffRows + "</div></div></section>" +
      '<section class="card span-5"><h2>Learning</h2><div class="kv">' +
      "<div><b>" + t.lessonsDone + "/" + t.lessons + "</b><span>lessons complete</span></div>" +
      "<div><b>" + t.exercisesDone + "/" + t.exercises + "</b><span>exercises solved</span></div>" +
      "<div><b>" + streak() + "</b><span>day streak</span></div>" +
      "</div></section>" +
      '<section class="card span-12"><h2>Activity · ' + totalSubs + " submissions in the last " + weeks + ' weeks</h2><div class="heatmap">' + cells + "</div>" +
      '<div class="heatmap-legend">Less <i style="background:var(--surface-3)"></i><i style="background:color-mix(in srgb, var(--ok) 35%, var(--surface-3))"></i>' +
      '<i style="background:color-mix(in srgb, var(--ok) 65%, var(--surface-3))"></i><i style="background:var(--ok)"></i> More</div></section>' +
      '<section class="card span-7"><h2>Modules</h2><div class="module-progress">' + moduleRows + "</div></section>" +
      '<section class="card span-5"><h2>Recent submissions</h2>' + recentHtml + "</section>" +
      '<section class="card span-12"><h2>Your data</h2><p class="muted" style="margin:0 0 12px">Progress and code are saved in this browser only. Export a backup to move it to another device.</p>' +
      '<div class="data-actions"><button class="btn" type="button" id="export-btn">Export progress</button>' +
      '<label class="btn" for="import-file">Import progress</label><input type="file" id="import-file" accept="application/json,.json" hidden>' +
      '<button class="btn btn-ghost" type="button" id="reset-btn">Reset all progress</button><span id="reset-confirm"></span></div></section>' +
      "</div></div>";

    document.getElementById("export-btn").addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(Store.d, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "pyforge-progress-" + dayKey() + ".json";
      document.body.appendChild(a);
      a.click();
      a.remove();
    });
    document.getElementById("import-file").addEventListener("change", function (e) {
      var file = e.target.files[0];
      if (!file) return;
      file.text().then(function (text) {
        var data = JSON.parse(text);
        if (!data || typeof data !== "object" || !data.solved) throw new Error("not a PyForge progress file");
        Store.replace(data);
        applyTheme();
        toast("Progress imported.");
        route();
      }).catch(function (err) { toast("Couldn't import that file: " + err.message); });
    });
    document.getElementById("reset-btn").addEventListener("click", function () {
      var slot = document.getElementById("reset-confirm");
      slot.innerHTML = '<span class="confirm-inline">Delete all progress and saved code? <button class="btn btn-sm" type="button" id="reset-yes">Yes, reset</button>' +
        '<button class="btn btn-sm btn-ghost" type="button" id="reset-no">Cancel</button></span>';
      document.getElementById("reset-yes").addEventListener("click", function () { Store.reset(); toast("Progress reset."); route(); });
      document.getElementById("reset-no").addEventListener("click", function () { slot.innerHTML = ""; });
    });
    return null;
  }

  // -------------------------------------------------------------------------
  // Problem workspace
  // -------------------------------------------------------------------------

  function formatInput(p, args) {
    return p.params.map(function (param, i) { return param.name + " = " + args[i]; }).join(p.style === "design" ? "\n" : ", ");
  }

  function renderDescription(p) {
    var solved = isSolved(p.id);
    var html = '<h1 class="problem-title">' + esc(problemTitle(p)) + "</h1>" +
      '<div class="problem-meta"><span class="pill diff-' + p.difficulty + '">' + p.difficulty + "</span>" +
      p.tags.map(function (tag) { return '<span class="chip">' + esc(tag) + "</span>"; }).join("") +
      (solved ? '<span class="solved-flag">' + statusIcon("solved") + "Solved</span>" : "") + "</div>";
    if (p.kind === "exercise") {
      var L = LESSONS[p.lesson];
      html += '<div class="problem-lesson-link">Practice for <a href="#/lesson/' + L.id + '">Module ' + L.module.number + " · " + esc(L.title) + "</a></div>";
    } else {
      html += '<div class="problem-lesson-link muted">' + esc(MODULE_BY_ID[p.module].challenge_title) + "</div>";
    }
    html += '<div class="problem-desc prose">' + MD.render(p.description) + "</div>";
    p.examples.forEach(function (ex, i) {
      html += '<div class="ex-block"><h4>Example ' + (i + 1) + '</h4><div class="ex-io">' +
        '<div><span class="k">Input:</span><code>' + esc(formatInput(p, ex.args)) + "</code></div>" +
        '<div><span class="k">Output:</span><code>' + esc(ex.expected) + "</code></div>" +
        (ex.why ? '<div><span class="k">Explanation:</span><span class="why">' + MD.inline(ex.why) + "</span></div>" : "") +
        "</div></div>";
    });
    if (p.constraints.length) {
      html += '<div class="constraints"><h4>Constraints</h4><ul>' +
        p.constraints.map(function (c) { return "<li>" + MD.inline(c) + "</li>"; }).join("") + "</ul></div>";
    }
    return html;
  }

  function viewProblem(id) {
    var P = PROBLEMS[id];
    if (!P) return notFound("problem");
    runner.start();
    app.classList.add("app-fixed");

    var seq = P.kind === "challenge" ? CHALLENGE_ORDER : EXERCISE_ORDER;
    var pos = seq.indexOf(id);
    var prevId = seq[pos - 1];
    var nextId = seq[pos + 1];
    var back, crumb;
    if (P.kind === "exercise") {
      var L = LESSONS[P.lesson];
      back = '<a class="btn btn-ghost btn-sm" href="#/lesson/' + L.id + '">' + ICON.left + " Lesson</a>";
      crumb = "Module " + L.module.number + " · " + L.title + " · Exercise " + (L.exercises.indexOf(id) + 1) + " of " + L.exercises.length;
    } else {
      back = '<a class="btn btn-ghost btn-sm" href="#/problems">' + ICON.left + " Problems</a>";
      crumb = MODULE_BY_ID[P.module].challenge_title;
    }

    var layout = Store.d.layout;
    app.innerHTML = '<div class="ws"><div class="ws-toolbar"><div class="left">' + back +
      (prevId ? '<a class="icon-btn" href="#/problem/' + prevId + '" title="Previous problem" aria-label="Previous problem">' + ICON.left + "</a>" : "") +
      (nextId ? '<a class="icon-btn" href="#/problem/' + nextId + '" title="Next problem" aria-label="Next problem">' + ICON.right + "</a>" : "") +
      '<span class="crumb">' + esc(crumb) + "</span></div>" +
      '<div class="center"><button class="btn" type="button" id="run-btn" title="Run the test cases (' + MOD + " + ')\">" + ICON.play + " Run</button>" +
      '<button class="btn btn-submit" type="button" id="submit-btn" title="Submit against all tests (' + MOD + ' + Enter)">Submit</button></div>' +
      '<div class="right"></div></div>' +
      '<div class="ws-body" id="ws-body" style="--left-basis:' + ((layout.left || 0.44) * 100) + '%">' +
      '<section class="pane pane-left" id="pane-left"><div class="tabs" role="tablist" id="left-tabs">' +
      '<button class="tab" role="tab" type="button" data-tab="desc" aria-selected="true">Description</button>' +
      '<button class="tab" role="tab" type="button" data-tab="hints">Hints <span class="badge">' + P.hints.length + "</span></button>" +
      '<button class="tab" role="tab" type="button" data-tab="solution">Solution</button>' +
      '<button class="tab" role="tab" type="button" data-tab="subs">Submissions <span class="badge" id="subs-count">' + (Store.d.subs[id] || []).length + "</span></button>" +
      '</div><div class="pane-scroll" id="left-content"></div></section>' +
      '<div class="gutter-x" id="gutter-x" role="separator" aria-orientation="vertical" aria-label="Resize panels"></div>' +
      '<section class="pane-right" id="pane-right" style="--editor-basis:' + ((layout.editor || 0.6) * 100) + '%">' +
      '<div class="pane editor-pane" id="editor-pane"><div class="editor-head"><span class="lang">Python 3</span>' +
      '<span class="saved" id="saved-note"></span><button class="btn btn-ghost btn-sm" type="button" id="reset-code">Reset code</button></div>' +
      '<div class="editor-host" id="editor-host"></div></div>' +
      '<div class="gutter-y" id="gutter-y" role="separator" aria-orientation="horizontal" aria-label="Resize editor"></div>' +
      '<div class="pane console-pane" id="console-pane"><div class="tabs" role="tablist" id="console-tabs">' +
      '<button class="tab" role="tab" type="button" data-tab="cases" aria-selected="true">Testcase</button>' +
      '<button class="tab" role="tab" type="button" data-tab="result">Test Result</button>' +
      '</div><div class="pane-scroll" id="console-content"></div></div></section></div></div>';

    var leftContent = document.getElementById("left-content");
    var consoleContent = document.getElementById("console-content");
    var runBtn = document.getElementById("run-btn");
    var submitBtn = document.getElementById("submit-btn");
    var savedNote = document.getElementById("saved-note");

    // --- editor ---------------------------------------------------------
    var busy = false;
    var cm = makeEditor(document.getElementById("editor-host"), Store.d.code[id] != null ? Store.d.code[id] : P.starter, {
      keys: {
        "Cmd-Enter": function () { submit(); },
        "Ctrl-Enter": function () { submit(); },
        "Cmd-'": function () { run(); },
        "Ctrl-'": function () { run(); },
      },
    });
    var persist = debounce(function () {
      Store.d.code[id] = cm.getValue();
      Store.save();
      savedNote.textContent = "Saved";
    }, 500);
    cm.on("change", function () { savedNote.textContent = "Editing…"; persist(); });
    setTimeout(function () { cm.refresh(); }, 0);

    var resetBtn = document.getElementById("reset-code");
    var resetArmed = null;
    resetBtn.addEventListener("click", function () {
      if (!resetArmed) {
        resetBtn.textContent = "Click again to reset";
        resetArmed = setTimeout(function () { resetBtn.textContent = "Reset code"; resetArmed = null; }, 3000);
        return;
      }
      clearTimeout(resetArmed);
      resetArmed = null;
      resetBtn.textContent = "Reset code";
      cm.setValue(P.starter);
      toast("Code reset to the starter template.");
    });

    // --- left pane tabs -------------------------------------------------
    var leftTab = "desc";
    function drawLeft() {
      document.querySelectorAll("#left-tabs .tab").forEach(function (b) { b.setAttribute("aria-selected", String(b.dataset.tab === leftTab)); });
      if (leftTab === "desc") {
        leftContent.innerHTML = renderDescription(P);
      } else if (leftTab === "hints") {
        leftContent.innerHTML = P.hints.length ? P.hints.map(function (h, i) {
          return '<details class="hint"><summary>Hint ' + (i + 1) + '</summary><div class="body">' + MD.inline(h) + "</div></details>";
        }).join("") + '<p class="console-note">Open one hint at a time and try again before reading the next.</p>' : '<p class="placeholder">No hints for this one.</p>';
      } else if (leftTab === "solution") {
        if (!isSolved(id) && !Store.d.revealed[id]) {
          leftContent.innerHTML = '<div class="gate">' + ICON.lock + "<h3>Solution locked</h3>" +
            "<p>It unlocks when you solve the problem. Stuck? Try the hints first, or run your code on a small case you can check by hand.</p>" +
            '<button class="btn" type="button" id="reveal-btn">Show the solution anyway</button></div>';
          document.getElementById("reveal-btn").addEventListener("click", function () {
            Store.d.revealed[id] = Date.now();
            Store.save();
            drawLeft();
          });
        } else {
          leftContent.innerHTML = '<div class="prose" style="margin:0">' + MD.render(P.explanation) + "</div>" +
            '<pre class="md-pre solution-code"><code>' + MD.highlight(P.reference.trimEnd()) + "</code></pre>";
        }
      } else if (leftTab === "subs") {
        var subs = (Store.d.subs[id] || []).slice().reverse();
        leftContent.innerHTML = subs.length ? '<table class="subs-table"><thead><tr><th>Status</th><th>Tests</th><th>Runtime</th><th>When</th></tr></thead><tbody>' +
          subs.map(function (s, i) {
            return '<tr data-i="' + i + '" title="Load this code into the editor"><td class="' + (s.status === "Accepted" ? "s-Accepted" : "s-bad") + '">' + esc(s.status) +
              "</td><td>" + (s.total ? s.passed + " / " + s.total : "–") + "</td><td>" + (s.runtime != null ? s.runtime.toFixed(1) + " ms" : "–") +
              '</td><td class="muted">' + timeAgo(s.at) + "</td></tr>";
          }).join("") + '</tbody></table><p class="console-note">Click a submission to load its code into the editor.</p>'
          : '<p class="placeholder">You haven\'t submitted this problem yet. Submissions run your code against every hidden test.</p>';
        leftContent.querySelectorAll("tr[data-i]").forEach(function (row) {
          row.addEventListener("click", function () {
            var s = subs[Number(row.dataset.i)];
            var doc = cm.getDoc();
            doc.replaceRange(s.code, { line: 0, ch: 0 }, { line: doc.lastLine() });
            toast("Loaded that submission. Undo with " + MOD + " + Z.");
          });
        });
      }
      leftContent.scrollTop = 0;
    }
    document.getElementById("left-tabs").addEventListener("click", function (e) {
      var b = e.target.closest(".tab");
      if (b) { leftTab = b.dataset.tab; drawLeft(); }
    });
    drawLeft();

    // --- test cases ------------------------------------------------------
    var defaultCases = function () { return P.examples.map(function (ex) { return { args: ex.args.slice() }; }); };
    var cases = Store.d.cases[id] ? JSON.parse(JSON.stringify(Store.d.cases[id])) : defaultCases();
    var activeCase = 0;
    var consoleTab = "cases";
    var lastResult = null;
    var activeResultCase = 0;

    function saveCases() {
      var isDefault = JSON.stringify(cases) === JSON.stringify(defaultCases());
      if (isDefault) delete Store.d.cases[id]; else Store.d.cases[id] = cases;
      Store.save();
    }

    function showConsole(tab) {
      consoleTab = tab;
      document.querySelectorAll("#console-tabs .tab").forEach(function (b) { b.setAttribute("aria-selected", String(b.dataset.tab === tab)); });
      drawConsole();
    }
    document.getElementById("console-tabs").addEventListener("click", function (e) {
      var b = e.target.closest(".tab");
      if (b) showConsole(b.dataset.tab);
    });

    function rowsFor(text) { return Math.min(8, Math.max(1, String(text).split("\n").length, Math.ceil(String(text).length / 70))); }

    function drawCases() {
      var c = cases[activeCase];
      var custom = !!Store.d.cases[id];
      consoleContent.innerHTML = '<div class="case-tabs">' + cases.map(function (_, i) {
        return '<button class="case-tab" type="button" data-case="' + i + '" aria-selected="' + (i === activeCase) + '">Case ' + (i + 1) +
          (cases.length > 1 ? '<span class="x" data-remove="' + i + '" title="Remove case" aria-label="Remove case ' + (i + 1) + '">×</span>' : "") + "</button>";
      }).join("") + (cases.length < 8 ? '<button class="case-tab" type="button" data-add title="Add a test case" aria-label="Add a test case">+</button>' : "") + "</div>" +
        P.params.map(function (param, j) {
          return '<div class="field"><label for="case-arg-' + j + '">' + esc(param.name) + " =</label>" +
            '<textarea id="case-arg-' + j + '" data-arg="' + j + '" rows="' + rowsFor(c.args[j]) + '" spellcheck="false" autocomplete="off">' +
            esc(c.args[j]) + "</textarea></div>";
        }).join("") +
        '<p class="console-note">Inputs are Python expressions. When you edit or add cases, the expected answer comes from the reference solution.' +
        (custom ? ' <a href="#" id="restore-cases">Restore the original examples</a>' : "") + "</p>";
      consoleContent.querySelectorAll("textarea").forEach(function (ta) {
        ta.addEventListener("input", function () {
          cases[activeCase].args[Number(ta.dataset.arg)] = ta.value;
          saveCases();
        });
      });
      var restore = document.getElementById("restore-cases");
      if (restore) restore.addEventListener("click", function (e) {
        e.preventDefault();
        cases = defaultCases();
        activeCase = 0;
        saveCases();
        drawCases();
      });
    }

    consoleContent.addEventListener("click", function (e) {
      if (consoleTab === "cases") {
        var rm = e.target.closest("[data-remove]");
        if (rm) {
          e.stopPropagation();
          cases.splice(Number(rm.dataset.remove), 1);
          activeCase = Math.min(activeCase, cases.length - 1);
          saveCases();
          drawCases();
          return;
        }
        if (e.target.closest("[data-add]")) {
          cases.push({ args: cases[activeCase].args.slice() });
          activeCase = cases.length - 1;
          saveCases();
          drawCases();
          return;
        }
        var tab = e.target.closest("[data-case]");
        if (tab) { activeCase = Number(tab.dataset.case); drawCases(); }
      } else {
        var rt = e.target.closest("[data-rcase]");
        if (rt) { activeResultCase = Number(rt.dataset.rcase); drawResult(); }
        var act = e.target.closest("[data-action]");
        if (act) {
          var a = act.dataset.action;
          if (a === "solution") { leftTab = "solution"; drawLeft(); }
          if (a === "add-case" && lastResult && lastResult.cases[0]) {
            cases.push({ args: lastResult.cases[0].input.map(function (x) { return x.value; }) });
            activeCase = cases.length - 1;
            saveCases();
            showConsole("cases");
          }
        }
      }
    });

    function drawConsole() {
      if (consoleTab === "cases") drawCases(); else drawResult();
    }

    function valueBlock(label, value, cls) {
      return '<div class="field"><span class="label">' + esc(label) + '</span><div class="value-box' + (cls ? " " + cls : "") + '">' + esc(value) + "</div></div>";
    }

    function inputsBlock(inputs) {
      return (inputs || []).map(function (x) { return valueBlock(x.name + " =", x.value); }).join("");
    }

    function drawRunning(text) {
      consoleContent.innerHTML = '<div class="running"><span class="spinner"></span><span id="run-status">' + esc(text) + "</span></div>";
    }

    function drawResult() {
      var r = lastResult;
      if (!r) {
        consoleContent.innerHTML = '<p class="placeholder">Run your code to see results here. Press <kbd>' + MOD + " + '</kbd> to run and <kbd>" + MOD + " + Enter</kbd> to submit.</p>";
        return;
      }
      var head = function (title, ok, sub) {
        return '<div class="result-head"><h3 class="' + (ok ? "r-ok" : "r-bad") + '">' + esc(title) + "</h3>" + (sub ? '<span class="sub">' + sub + "</span>" : "") + "</div>";
      };
      var html = "";
      if (r.status === "Compile Error" || r.status === "Invalid Testcase" || r.status === "Internal Error") {
        html = head(r.status, false) + '<div class="error-box">' + esc(r.error || "") + "</div>";
      } else if (r.status === "Time Limit Exceeded" && r.cases) {
        // The judge timed a test that finished, but too slowly.
        var slow = r.cases[r.cases.length - 1];
        html = head("Time Limit Exceeded", false, r.passed + " / " + r.total + " testcases passed") +
          "<p>Test " + (slow.index + 1) + " took " + Math.round(slow.ms).toLocaleString() + " ms. The limit is " +
          r.limit_ms.toLocaleString() + " ms per test. Your answer may be correct, but the approach is too slow for large inputs. " +
          "Look for a way to avoid re-scanning the input inside a loop.</p>" +
          '<h4 class="eyebrow" style="margin:14px 0 8px">Last executed input</h4>' + inputsBlock(slow.input);
      } else if (r.status === "Time Limit Exceeded") {
        // A test was still running when its time ran out, so the worker was stopped.
        var p0 = r.progress;
        var where = !p0 ? "" : p0.index < 0 ? "Stopped while loading your code"
          : "Stopped during test " + (p0.index + 1) + " of " + p0.total + (r.mode === "submit" ? " · " + p0.index + " passed" : "");
        var why = p0 && p0.index < 0 ? "The code outside your function never finished. Check for a loop at the top level."
          : r.mode === "submit" ? "Either a loop never ends, or the approach is far too slow for the large hidden inputs. Look for a way to avoid re-scanning the input inside a loop."
          : "Check for a loop that never ends.";
        html = head("Time Limit Exceeded", false, where) +
          "<p>That test was still running after " + (r.limitMs / 1000).toFixed(1).replace(/\.0$/, "") + " seconds, so it was stopped " +
          "(the limit is " + (P.time_limit_ms / 1000) + " s per test). " + why + "</p>";
      } else if (r.status === "Runtime Error") {
        var c0 = r.cases[r.cases.length - 1];
        html = head("Runtime Error", false, r.mode === "submit" ? r.passed + " / " + r.total + " testcases passed" : "") +
          '<div class="error-box">' + esc(r.error || "") + "</div>" +
          (r.last_input ? '<h4 class="eyebrow" style="margin:0 0 8px">Last executed input</h4>' + inputsBlock(r.last_input) : "") +
          (c0 && c0.stdout ? valueBlock("Stdout", c0.stdout) : "");
      } else if (r.mode === "submit") {
        if (r.status === "Accepted") {
          var nextLink = nextId ? '<a class="btn btn-submit" href="#/problem/' + nextId + '">Next problem ' + ICON.right + "</a>" : "";
          var backLink = P.kind === "exercise" ? '<a class="btn" href="#/lesson/' + P.lesson + '">Back to the lesson</a>' : "";
          html = head("Accepted", true, r.passed + " / " + r.total + " testcases passed · " + r.runtime_ms.toFixed(1) + " ms") +
            '<div class="accepted-box"><p>Every test passed, including the hidden ones. The solution write-up is now unlocked, so compare approaches.</p>' +
            '<div class="accepted-actions">' + nextLink + backLink + '<button class="btn" type="button" data-action="solution">Read the solution</button></div></div>';
        } else {
          var f = r.cases[0];
          var reusable = f && f.input.every(function (x) { return x.value.indexOf("…") < 0; });
          html = head("Wrong Answer", false, r.passed + " / " + r.total + " testcases passed") +
            inputsBlock(f.input) + (f.stdout ? valueBlock("Stdout", f.stdout) : "") +
            valueBlock("Output", f.output, "bad") + valueBlock("Expected", f.expected, "good") +
            (reusable ? '<button class="btn btn-sm" type="button" data-action="add-case">Add this input to my test cases</button>' : "");
        }
      } else {
        var all = r.status === "Accepted";
        activeResultCase = Math.min(activeResultCase, r.cases.length - 1);
        var c = r.cases[activeResultCase];
        html = head(all ? "Accepted" : "Wrong Answer", all, "Runtime " + r.runtime_ms.toFixed(1) + " ms") +
          '<div class="case-tabs">' + r.cases.map(function (cs, i) {
            return '<button class="case-tab" type="button" data-rcase="' + i + '" aria-selected="' + (i === activeResultCase) + '"><span class="dot ' +
              (cs.passed ? "pass" : "fail") + '"></span>Case ' + (cs.index + 1) + "</button>";
          }).join("") + "</div>" +
          (c ? inputsBlock(c.input) + (c.stdout ? valueBlock("Stdout", c.stdout) : "") +
            valueBlock("Output", c.output, c.passed ? "good" : "bad") + valueBlock("Expected", c.expected) : "") +
          (all ? '<p class="console-note">The examples pass. Submit to run the hidden tests too.</p>' : "");
      }
      consoleContent.innerHTML = html;
    }

    // --- run & submit ----------------------------------------------------
    function setBusy(on) {
      busy = on;
      runBtn.disabled = on;
      submitBtn.disabled = on;
    }

    function progressText(verb, m) {
      return verb + " test " + (m.index + 1) + " of " + m.total + "…";
    }

    function execute(mode) {
      if (busy) return;
      setBusy(true);
      lastResult = null;
      showConsole("result");
      var verb = mode === "submit" ? "Judging" : "Running";
      drawRunning(runner.state === "ready" ? verb + "…" : "Starting Python. The first run downloads the runtime and takes a few seconds…");
      var request = { action: "judge", problem: P, code: cm.getValue(), mode: mode };
      if (mode === "run") request.cases = cases.map(function (c) { return { args: c.args }; });
      var timeout = mode === "submit" ? SUBMIT_TIMEOUT_MS : RUN_TIMEOUT_MS;
      runner.run(request, {
        timeoutMs: timeout,
        caseTimeoutMs: P.time_limit_ms + CASE_GRACE_MS,
        onProgress: function (m) {
          var el = document.getElementById("run-status");
          if (el) el.textContent = progressText(verb, m);
        },
      }).then(function (res) {
        res.mode = res.mode || mode;
        lastResult = res;
        activeResultCase = res.cases ? Math.max(0, res.cases.findIndex(function (c) { return !c.passed; })) : 0;
        if (mode === "submit") recordSubmission(res);
        drawResult();
        setBusy(false);
      }, function (err) {
        lastResult = { status: "Internal Error", error: "Python couldn't start: " + ((err && err.message) || err), mode: mode };
        drawResult();
        setBusy(false);
      });
    }

    function run() { execute("run"); }
    function submit() { execute("submit"); }

    function recordSubmission(res) {
      var list = Store.d.subs[id] || (Store.d.subs[id] = []);
      list.push({ status: res.status, runtime: res.runtime_ms, passed: res.passed, total: res.total, code: cm.getValue(), at: Date.now() });
      if (list.length > 25) list.splice(0, list.length - 25);
      var today = dayKey();
      Store.d.activity[today] = (Store.d.activity[today] || 0) + 1;
      if (res.status === "Accepted" && !Store.d.solved[id]) {
        Store.d.solved[id] = Date.now();
        toast(P.kind === "exercise" ? "Exercise solved!" : "Challenge solved!");
      }
      Store.save();
      document.getElementById("subs-count").textContent = list.length;
      if (leftTab === "desc" || leftTab === "subs" || leftTab === "solution") drawLeft();
    }

    runBtn.addEventListener("click", run);
    submitBtn.addEventListener("click", submit);

    function onKey(e) {
      if (e.defaultPrevented || !(e.metaKey || e.ctrlKey)) return;
      if (e.key === "Enter") { e.preventDefault(); submit(); }
      else if (e.key === "'") { e.preventDefault(); run(); }
    }
    document.addEventListener("keydown", onKey);

    // --- resizable panes -------------------------------------------------
    var wsBody = document.getElementById("ws-body");
    var paneRight = document.getElementById("pane-right");
    function resizer(gutter, container, axis, key, cssVar, min, max) {
      gutter.addEventListener("pointerdown", function (e) {
        e.preventDefault();
        gutter.setPointerCapture(e.pointerId);
        gutter.classList.add("dragging");
        var rect = container.getBoundingClientRect();
        function move(ev) {
          var ratio = axis === "x" ? (ev.clientX - rect.left) / rect.width : (ev.clientY - rect.top) / rect.height;
          ratio = Math.min(max, Math.max(min, ratio));
          container.style.setProperty(cssVar, (ratio * 100) + "%");
          Store.d.layout[key] = ratio;
          cm.refresh();
        }
        function up() {
          gutter.classList.remove("dragging");
          gutter.removeEventListener("pointermove", move);
          gutter.removeEventListener("pointerup", up);
          Store.save();
        }
        gutter.addEventListener("pointermove", move);
        gutter.addEventListener("pointerup", up);
      });
    }
    resizer(document.getElementById("gutter-x"), wsBody, "x", "left", "--left-basis", 0.22, 0.7);
    resizer(document.getElementById("gutter-y"), paneRight, "y", "editor", "--editor-basis", 0.2, 0.85);
    var onResize = debounce(function () { cm.refresh(); }, 100);
    window.addEventListener("resize", onResize);

    drawConsole();

    return {
      destroy: function () {
        document.removeEventListener("keydown", onKey);
        window.removeEventListener("resize", onResize);
        Store.d.code[id] = cm.getValue();
        Store.save();
      },
    };
  }

  route();
})();
