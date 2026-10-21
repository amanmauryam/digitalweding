/* DigitalWedding — progressive enhancement helpers.
   Everything here is optional: the invitation stays fully usable with
   JavaScript disabled (best for slow 4G connections and old phones). */
(function () {
  "use strict";

  /* ---------------------------------------------------------------- copy */
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand("copy");
    } catch (err) {
      /* ignore */
    }
    document.body.removeChild(area);
    return Promise.resolve();
  }

  window.dwCopy = function (text, messageSelector) {
    return copyText(text).then(function () {
      var node = messageSelector ? document.querySelector(messageSelector) : null;
      if (node) {
        var original = node.textContent;
        node.textContent = node.dataset.copied || "कॉपी हो गया ✓";
        window.setTimeout(function () {
          node.textContent = original;
        }, 2200);
      }
    });
  };

  document.addEventListener("click", function (event) {
    var trigger = event.target.closest("[data-dw-copy]");
    if (!trigger) return;
    event.preventDefault();
    var value = trigger.getAttribute("data-dw-copy");
    window.dwCopy(value, trigger.getAttribute("data-dw-copied-target") || null);
  });

  /* ------------------------------------------------------------- shehnai */
  /* A tiny WebAudio approximation of the shehnai played when the Kohbar
     door opens — no audio asset required, works offline. */
  window.dwShehnai = function () {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    try {
      var ctx = new Ctx();
      var now = ctx.currentTime;
      var master = ctx.createGain();
      master.gain.setValueAtTime(0.0001, now);
      master.gain.exponentialRampToValueAtTime(0.22, now + 0.35);
      master.gain.exponentialRampToValueAtTime(0.0001, now + 2.4);

      var filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(2200, now);

      var lfo = ctx.createOscillator();
      var lfoGain = ctx.createGain();
      lfo.frequency.setValueAtTime(5.5, now);
      lfoGain.gain.setValueAtTime(14, now);
      lfo.connect(lfoGain);

      [392, 466.16, 587.33].forEach(function (freq, index) {
        var osc = ctx.createOscillator();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(freq, now + index * 0.12);
        osc.frequency.linearRampToValueAtTime(freq * 1.02, now + 2.2);
        lfoGain.connect(osc.frequency);
        osc.connect(filter);
        osc.start(now + index * 0.12);
        osc.stop(now + 2.5);
      });

      filter.connect(master);
      master.connect(ctx.destination);
      lfo.start(now);
      lfo.stop(now + 2.5);
      window.setTimeout(function () {
        ctx.close();
      }, 3200);
    } catch (err) {
      /* ignore */
    }
  };

  /* ---------------------------------------------------------- folk music */
  /* Background folk track stays paused until the guest taps (design.md §5.B). */
  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-dw-audio]");
    if (!toggle) return;
    var audio = document.querySelector(toggle.getAttribute("data-dw-audio"));
    if (!audio) return;
    event.preventDefault();
    if (audio.paused) {
      var promise = audio.play();
      if (promise && typeof promise.catch === "function") {
        promise.catch(function () {});
      }
      toggle.setAttribute("data-dw-playing", "1");
    } else {
      audio.pause();
      toggle.setAttribute("data-dw-playing", "0");
    }
  });

  /* --------------------------------------------------------- door opening */
  document.addEventListener("click", function (event) {
    var door = event.target.closest("[data-dw-door]");
    if (!door) return;
    event.preventDefault();
    if (door.classList.contains("is-open")) return;
    door.classList.add("is-open");
    var hint = document.querySelector("[data-dw-door-hint]");
    if (hint) hint.setAttribute("hidden", "hidden");
    var content = document.querySelector("[data-dw-door-content]");
    if (content) {
      content.removeAttribute("hidden");
      content.classList.add("dw-fade-in");
    }
    if (window.dwShehnai) window.dwShehnai();
  });
})();
