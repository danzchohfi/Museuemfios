/* ============================================================================
   MUSEU EM FIOS — camada de interação e motion
   GSAP + ScrollTrigger (vendorizados). Degrada com segurança:
   sem JS ou com prefers-reduced-motion o conteúdo fica 100% visível e usável.
============================================================================ */

(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGsap = typeof window.gsap !== "undefined";
  var gsap = window.gsap;
  if (hasGsap && window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);

  var EASE = "power3.out";

  /* ------------------------------------------------------------ utils -- */

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* Divide um texto em <span class="char"> preservando acessibilidade */
  function splitChars(el) {
    var text = el.textContent;
    el.setAttribute("aria-label", text);
    el.textContent = "";
    text.split("").forEach(function (ch) {
      var s = document.createElement("span");
      s.className = "char";
      s.setAttribute("aria-hidden", "true");
      s.textContent = ch === " " ? " " : ch;
      el.appendChild(s);
    });
    return $$(".char", el);
  }

  function splitWords(el) {
    var text = el.textContent.trim();
    el.setAttribute("aria-label", text);
    el.textContent = "";
    text.split(/\s+/).forEach(function (w, i) {
      var s = document.createElement("span");
      s.className = "palavra";
      s.setAttribute("aria-hidden", "true");
      s.textContent = w;
      el.appendChild(s);
      el.appendChild(document.createTextNode(" "));
    });
    return $$(".palavra", el);
  }

  /* Grafismo do manual: duas metades abertas de hexágono alongado.
     Gerado em coordenadas de pixel do container para o traço e o
     "desenho" da linha (dashoffset) ficarem exatos. */
  function fioPaths(w, h) {
    return [
      "M " + 0.60 * w + " " + 0.02 * h + " L " + 0.96 * w + " " + 0.28 * h + " L " + 0.96 * w + " " + 0.78 * h,
      "M " + 0.04 * w + " " + 0.22 * h + " L " + 0.04 * w + " " + 0.72 * h + " L " + 0.40 * w + " " + 0.98 * h
    ];
  }

  function injectFio(el) {
    var w = el.clientWidth || 300;
    var h = el.clientHeight || 300;
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "fio" + (el.getAttribute("data-fio") === "branco" ? " fio--branco" : ""));
    svg.setAttribute("viewBox", "0 0 " + w + " " + h);
    svg.setAttribute("preserveAspectRatio", "none");
    svg.setAttribute("aria-hidden", "true");
    fioPaths(w, h).forEach(function (d) {
      var p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", d);
      svg.appendChild(p);
    });
    el.appendChild(svg);
    return svg;
  }

  /* Prepara um path para "desenhar" (dashoffset) */
  function drawPaths(svg, opts) {
    if (!hasGsap) return;
    var paths = $$("path", svg);
    paths.forEach(function (p) {
      var len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.style.strokeDashoffset = reduced ? 0 : len;
    });
    if (reduced) return;
    gsap.to(paths, Object.assign({
      strokeDashoffset: 0,
      duration: 1.4,
      ease: "power2.inOut",
      stagger: 0.15
    }, opts || {}));
  }

  /* ----------------------------------------------------------- header -- */

  function initHeader() {
    var header = $(".mf-header");
    if (!header) return;
    var update = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", update, { passive: true });
    update();

    var btn = $(".mf-menu-btn");
    var nav = $(".mf-nav");
    if (btn && nav) {
      btn.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        document.documentElement.style.overflow = open ? "hidden" : "";
      });
      $$("a", nav).forEach(function (a) {
        a.addEventListener("click", function () {
          nav.classList.remove("is-open");
          btn.setAttribute("aria-expanded", "false");
          document.documentElement.style.overflow = "";
        });
      });
    }
  }

  /* --------------------------------------------------------- carrinho -- */

  var CART_KEY = "mf-demo-carrinho";

  function cartCount() {
    return parseInt(sessionStorage.getItem(CART_KEY) || "0", 10);
  }

  function renderCart() {
    $$(".mf-carrinho__count").forEach(function (el) {
      el.textContent = cartCount();
    });
  }

  function toast(msg, linkText, linkHref) {
    var t = $(".mf-toast");
    if (!t) {
      t = document.createElement("div");
      t.className = "mf-toast";
      t.setAttribute("role", "status");
      document.body.appendChild(t);
    }
    t.innerHTML = "";
    var span = document.createElement("span");
    span.textContent = msg;
    t.appendChild(span);
    if (linkText) {
      var a = document.createElement("a");
      a.href = linkHref || "#";
      a.textContent = linkText;
      t.appendChild(a);
    }
    requestAnimationFrame(function () { t.classList.add("is-on"); });
    clearTimeout(t._timer);
    t._timer = setTimeout(function () { t.classList.remove("is-on"); }, 3600);
  }

  function initCart() {
    renderCart();
    $$("[data-add-cart]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var qty = 1;
        var qtyInput = $(".mf-qtd input");
        if (qtyInput && btn.closest(".mf-produto")) qty = parseInt(qtyInput.value, 10) || 1;
        sessionStorage.setItem(CART_KEY, String(cartCount() + qty));
        renderCart();
        toast("Adicionado ao carrinho — " + (btn.getAttribute("data-add-cart") || "kit"), "Ver demo do fluxo", "#");
      });
    });
  }

  /* ------------------------------------------------------------- hero -- */

  function initHero() {
    var hero = $(".mf-hero");
    if (!hero) return;
    var slides = $$(".mf-hero__slide", hero);
    if (!slides.length) return;
    var dots = $$(".mf-hero__dot", hero);
    var atual = 0;
    var timer = null;
    var DURACAO = 6500;

    /* Prepara nomes e fios */
    slides.forEach(function (slide) {
      var nome = $(".mf-hero__nome", slide);
      if (nome && hasGsap && !reduced) splitChars(nome);
      var alvoFio = $(".mf-hero__fio", slide);
      if (alvoFio) injectFio(alvoFio);
    });

    function mostra(i, primeira) {
      var anterior = slides[atual];
      atual = (i + slides.length) % slides.length;
      var slide = slides[atual];

      hero.style.setProperty("--cor-hero", "var(--" + (slide.getAttribute("data-cor") || "azul") + ")");

      slides.forEach(function (s, j) { s.classList.toggle("is-active", j === atual); });
      dots.forEach(function (d, j) {
        d.classList.toggle("is-active", j === atual);
        d.setAttribute("aria-pressed", j === atual ? "true" : "false");
        var prog = $(".prog", d);
        if (prog && hasGsap) {
          gsap.killTweensOf(prog);
          gsap.set(prog, { scaleX: j === atual ? 0 : 0, transformOrigin: "left" });
          if (j === atual && !reduced) gsap.to(prog, { scaleX: 1, duration: DURACAO / 1000, ease: "none" });
          if (j === atual && reduced) gsap.set(prog, { scaleX: 1 });
        }
      });

      if (!hasGsap || reduced) return;

      var chars = $$(".char", $(".mf-hero__nome", slide) || slide);
      var obra = $(".mf-hero__obra img", slide);
      var intro = $(".mf-hero__intro", slide);
      var rodape = $(".mf-hero__rodape", slide);
      var fio = $(".mf-hero__fio .fio", slide);

      var tl = gsap.timeline();
      if (anterior && anterior !== slide && !primeira) {
        tl.to(anterior, { autoAlpha: 0, duration: 0.35, ease: "power1.in" }, 0);
      }
      tl.fromTo(slide, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.45 }, primeira ? 0 : 0.25);
      if (obra) tl.fromTo(obra, { scale: 1.12 }, { scale: 1, duration: 1.6, ease: EASE }, "<");
      if (chars.length) {
        tl.fromTo(chars,
          { yPercent: 60, autoAlpha: 0 },
          { yPercent: 0, autoAlpha: 1, duration: 0.9, ease: EASE, stagger: 0.045 }, "<0.15");
      }
      if (fio) drawPaths(fio, { delay: 0.2 });
      if (intro) tl.fromTo(intro, { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.7, ease: EASE }, "<0.2");
      if (rodape) tl.fromTo(rodape, { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.7, ease: EASE }, "<0.1");
    }

    function agenda() {
      clearInterval(timer);
      if (slides.length < 2 || reduced) return;
      timer = setInterval(function () { mostra(atual + 1); }, DURACAO);
    }

    dots.forEach(function (d, j) {
      d.addEventListener("click", function () { mostra(j); agenda(); });
    });
    hero.addEventListener("mouseenter", function () { clearInterval(timer); });
    hero.addEventListener("mouseleave", agenda);
    hero.addEventListener("focusin", function () { clearInterval(timer); });
    hero.addEventListener("focusout", agenda);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearInterval(timer); else agenda();
    });

    mostra(0, true);
    agenda();
  }

  /* ---------------------------------------------------------- reveals -- */

  function initReveals() {
    if (!hasGsap || !window.ScrollTrigger) return;

    $$("[data-reveal]").forEach(function (el) {
      el.classList.add("mf-reveal");
      var alvos = el.getAttribute("data-reveal") === "grupo" ? Array.prototype.slice.call(el.children) : [el];
      gsap.fromTo(alvos,
        reduced ? { autoAlpha: 0 } : { autoAlpha: 0, y: 34 },
        {
          autoAlpha: 1,
          y: 0,
          duration: reduced ? 0.2 : 0.85,
          ease: EASE,
          stagger: reduced ? 0 : 0.09,
          scrollTrigger: { trigger: el, start: "top 86%", once: true },
          onStart: function () { el.classList.add("is-in"); }
        });
    });

    /* Fios que se desenham ao entrar na tela */
    $$("[data-fio]").forEach(function (el) {
      if ($(".fio", el)) return; /* hero já injetou */
      var svg = injectFio(el);
      if (reduced) return;
      window.ScrollTrigger.create({
        trigger: el,
        start: "top 82%",
        once: true,
        onEnter: function () { drawPaths(svg); }
      });
    });

    /* Manifesto: palavras sobem uma a uma */
    var frase = $(".mf-manifesto__frase");
    if (frase && !reduced) {
      var palavras = splitWords(frase);
      gsap.fromTo(palavras,
        { yPercent: 110, autoAlpha: 0 },
        {
          yPercent: 0, autoAlpha: 1,
          duration: 0.7, ease: EASE, stagger: 0.035,
          scrollTrigger: { trigger: frase, start: "top 80%", once: true }
        });
    }

    /* Parallax sutil nas obras dos cards e seções */
    if (!reduced) {
      $$("[data-parallax] img").forEach(function (img) {
        gsap.fromTo(img, { yPercent: -6 }, {
          yPercent: 6,
          ease: "none",
          scrollTrigger: { trigger: img, scrub: 0.6 }
        });
      });
    }
  }

  /* ---------------------------------------------------------- produto -- */

  function initProduto() {
    var qtd = $(".mf-qtd");
    if (qtd) {
      var input = $("input", qtd);
      $$("button", qtd).forEach(function (b) {
        b.addEventListener("click", function () {
          var v = parseInt(input.value, 10) || 1;
          v += b.getAttribute("data-passo") === "-" ? -1 : 1;
          input.value = Math.max(1, Math.min(99, v));
        });
      });
    }

    var palco = $(".mf-produto__palco img");
    $$(".mf-produto__thumbs button").forEach(function (b) {
      b.addEventListener("click", function () {
        $$(".mf-produto__thumbs button").forEach(function (x) {
          x.classList.remove("is-active");
          x.setAttribute("aria-pressed", "false");
        });
        b.classList.add("is-active");
        b.setAttribute("aria-pressed", "true");
        if (!palco) return;
        var src = b.getAttribute("data-img");
        if (hasGsap && !reduced) {
          gsap.to(palco, {
            autoAlpha: 0, duration: 0.18, onComplete: function () {
              palco.src = src;
              gsap.fromTo(palco, { autoAlpha: 0, scale: 1.04 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: EASE });
            }
          });
        } else {
          palco.src = src;
        }
      });
    });
  }

  /* ------------------------------------------------------------ loja -- */

  function initFiltros() {
    var botoes = $$(".mf-filtro");
    if (!botoes.length) return;
    var cards = $$("[data-artista]");
    botoes.forEach(function (b) {
      b.addEventListener("click", function () {
        botoes.forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        var alvo = b.getAttribute("data-filtro");
        cards.forEach(function (c) {
          var mostra = alvo === "todos" || c.getAttribute("data-artista") === alvo;
          c.style.display = mostra ? "" : "none";
        });
        if (window.ScrollTrigger) window.ScrollTrigger.refresh();
      });
    });
  }

  /* ------------------------------------------------------- newsletter -- */

  function initNews() {
    $$(".mf-news form").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var email = $("input", f);
        if (email && email.value.indexOf("@") > 0) {
          toast("Endereço registrado. Você vai receber as novas obras em primeira mão.");
          email.value = "";
        } else {
          toast("Digite um e-mail válido para receber as novidades.");
        }
      });
    });
  }

  /* ------------------------------------------------- cursor com fio -- */

  function initCursor() {
    if (reduced) return;
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    var dot = document.createElement("div");
    dot.className = "mf-cursor";
    document.body.appendChild(dot);

    var canvas = document.createElement("canvas");
    canvas.className = "mf-fio-canvas";
    document.body.appendChild(canvas);
    var ctx = canvas.getContext("2d");

    function resize() {
      canvas.width = window.innerWidth * devicePixelRatio;
      canvas.height = window.innerHeight * devicePixelRatio;
      ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    }
    resize();
    window.addEventListener("resize", resize);

    var alvoX = -100, alvoY = -100, x = -100, y = -100;
    var pontos = [];
    var MAX = 32;

    document.addEventListener("mousemove", function (e) {
      alvoX = e.clientX; alvoY = e.clientY;
    });

    document.addEventListener("mouseover", function (e) {
      dot.classList.toggle("is-link", !!e.target.closest("a, button, [role='button'], summary"));
    });

    function frame() {
      x += (alvoX - x) * 0.22;
      y += (alvoY - y) * 0.22;
      dot.style.transform = "translate(" + x + "px," + y + "px) translate(-50%,-50%)";

      pontos.push({ x: x, y: y });
      if (pontos.length > MAX) pontos.shift();

      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
      if (pontos.length > 2) {
        ctx.beginPath();
        ctx.moveTo(pontos[0].x, pontos[0].y);
        for (var i = 1; i < pontos.length - 1; i++) {
          var mx = (pontos[i].x + pontos[i + 1].x) / 2;
          var my = (pontos[i].y + pontos[i + 1].y) / 2;
          ctx.quadraticCurveTo(pontos[i].x, pontos[i].y, mx, my);
        }
        ctx.strokeStyle = "rgba(255,255,255,0.9)";
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------- boot -- */

  function init() {
    if (hasGsap) document.documentElement.classList.add("mf-js");
    initHeader();
    initCart();
    initHero();
    initReveals();
    initProduto();
    initFiltros();
    initNews();
    initCursor();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
