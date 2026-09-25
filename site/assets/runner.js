/* Runs Python in the browser with Pyodide.

   Pyodide lives in a Web Worker so that learner code which never finishes can
   be stopped: when a run exceeds its time limit the worker is terminated and a
   fresh one is started, and the run is reported as "Time Limit Exceeded".
   If the browser refuses to create a worker, Python runs on the page itself
   (without time limits) as a fallback. */
(function () {
  "use strict";

  var PYODIDE_VERSION = "0.29.5";
  var INDEX_URL = "https://cdn.jsdelivr.net/npm/pyodide@" + PYODIDE_VERSION + "/";

  // Everything inside this function runs in the worker, not on the page.
  function workerMain() {
    var handle = null;

    async function boot(indexURL, harness) {
      importScripts(indexURL + "pyodide.js");
      var pyodide = await loadPyodide({ indexURL: indexURL });
      pyodide.FS.writeFile("/home/pyodide/pyforge_harness.py", harness);
      pyodide.runPython("import sys\nsys.path.insert(0, '/home/pyodide')\nimport pyforge_harness");
      handle = pyodide.pyimport("pyforge_harness").handle;
    }

    self.onmessage = async function (event) {
      var msg = event.data;
      if (msg.type === "init") {
        try {
          await boot(msg.indexURL, msg.harness);
          self.postMessage({ type: "ready" });
        } catch (err) {
          self.postMessage({ type: "init-error", error: String((err && err.message) || err) });
        }
        return;
      }
      if (msg.type === "run") {
        try {
          var progress = function (index, total) {
            self.postMessage({ type: "progress", id: msg.id, index: index, total: total });
          };
          var text = handle(JSON.stringify(msg.request), progress);
          self.postMessage({ type: "result", id: msg.id, result: JSON.parse(text) });
        } catch (err) {
          self.postMessage({ type: "result", id: msg.id, error: String((err && err.message) || err) });
        }
      }
    };
  }

  function PyRunner(harnessSource) {
    this.harness = harnessSource;
    this.worker = null;
    this.ready = null;
    this.mainThread = null;
    this.seq = 0;
    this.chain = Promise.resolve();
    this.listeners = [];
    this.state = "idle";
  }

  PyRunner.prototype.onState = function (fn) {
    this.listeners.push(fn);
    fn(this.state, this.detail);
  };

  PyRunner.prototype._setState = function (state, detail) {
    this.state = state;
    this.detail = detail;
    this.listeners.forEach(function (fn) { fn(state, detail); });
  };

  /* Start Python if it isn't running yet. Resolves once it's ready. */
  PyRunner.prototype.start = function () {
    if (this.ready) return this.ready;
    var self = this;
    this._setState("loading", "Starting Python…");
    this.ready = new Promise(function (resolve, reject) {
      var worker;
      try {
        var src = "(" + workerMain.toString() + ")();";
        var url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
        worker = new Worker(url);
      } catch (err) {
        self._startMainThread().then(resolve, reject);
        return;
      }
      self.worker = worker;
      var onMessage = function (e) {
        if (e.data.type === "ready") {
          worker.removeEventListener("message", onMessage);
          self._setState("ready", "Python ready");
          resolve();
        } else if (e.data.type === "init-error") {
          worker.removeEventListener("message", onMessage);
          worker.terminate();
          self.worker = null;
          self._startMainThread().then(resolve, reject);
        }
      };
      worker.addEventListener("message", onMessage);
      worker.addEventListener("error", function (e) {
        if (self.state === "loading") {
          worker.terminate();
          self.worker = null;
          self._startMainThread().then(resolve, reject);
        }
        e.preventDefault && e.preventDefault();
      });
      worker.postMessage({ type: "init", indexURL: INDEX_URL, harness: self.harness });
    });
    this.ready.catch(function (err) {
      self.ready = null;
      self._setState("error", "Python failed to load: " + ((err && err.message) || err));
    });
    return this.ready;
  };

  /* Fallback: load Pyodide on the page itself. */
  PyRunner.prototype._startMainThread = function () {
    var self = this;
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = INDEX_URL + "pyodide.js";
      script.onload = async function () {
        try {
          var pyodide = await window.loadPyodide({ indexURL: INDEX_URL });
          pyodide.FS.writeFile("/home/pyodide/pyforge_harness.py", self.harness);
          pyodide.runPython("import sys\nsys.path.insert(0, '/home/pyodide')\nimport pyforge_harness");
          self.mainThread = pyodide.pyimport("pyforge_harness").handle;
          self._setState("ready", "Python ready (no time limit in this browser)");
          resolve();
        } catch (err) { reject(err); }
      };
      script.onerror = function () { reject(new Error("couldn't download Pyodide. Check your internet connection.")); };
      document.head.appendChild(script);
    });
  };

  PyRunner.prototype.restart = function () {
    if (this.worker) this.worker.terminate();
    this.worker = null;
    this.ready = null;
    this.start();
  };

  /* Run one request. Requests are queued so only one runs at a time.
     Resolves with the harness result, or {status: "Time Limit Exceeded"} if
     the whole run exceeds options.timeoutMs or a single test (announced by a
     progress message) runs longer than options.caseTimeoutMs. */
  PyRunner.prototype.run = function (request, options) {
    var self = this;
    var job = this.chain.then(function () { return self._run(request, options || {}); });
    this.chain = job.catch(function () {});
    return job;
  };

  PyRunner.prototype._run = async function (request, options) {
    await this.start();
    var self = this;
    this._setState("busy", "Running…");

    if (this.mainThread) {
      await new Promise(function (r) { setTimeout(r, 30); }); // let the UI paint first
      try {
        var text = this.mainThread(JSON.stringify(request), function (index, total) {
          if (options.onProgress && index >= 0) options.onProgress({ index: index, total: total });
        });
        return JSON.parse(text);
      } catch (err) {
        return { status: "Internal Error", error: String((err && err.message) || err) };
      } finally {
        this._setState("ready", "Python ready (no time limit in this browser)");
      }
    }

    return new Promise(function (resolve) {
      var id = ++self.seq;
      var worker = self.worker;
      var last = null;
      var caseTimer = null;
      function stop(killedBy, limitMs) {
        cleanup();
        self.restart();
        resolve({ status: "Time Limit Exceeded", progress: last, killedBy: killedBy, limitMs: limitMs });
      }
      var timer = setTimeout(function () { stop("total", options.timeoutMs); }, options.timeoutMs || 10000);
      function onMessage(e) {
        var m = e.data;
        if (m.id !== id) return;
        if (m.type === "progress") {
          last = m;
          if (options.caseTimeoutMs) {
            clearTimeout(caseTimer);
            caseTimer = setTimeout(function () { stop("case", options.caseTimeoutMs); }, options.caseTimeoutMs);
          }
          if (options.onProgress && m.index >= 0) options.onProgress(m);
        } else if (m.type === "result") {
          cleanup();
          self._setState("ready", "Python ready");
          if (m.error) {
            // A JavaScript-level failure (e.g. a stack overflow) can leave
            // Python in a broken state, so start a fresh interpreter.
            self.restart();
            resolve({ status: "Internal Error", error: m.error });
          } else {
            resolve(m.result);
          }
        }
      }
      function cleanup() {
        clearTimeout(timer);
        clearTimeout(caseTimer);
        worker.removeEventListener("message", onMessage);
      }
      worker.addEventListener("message", onMessage);
      worker.postMessage({ type: "run", id: id, request: request });
    });
  };

  window.PyRunner = PyRunner;
})();
