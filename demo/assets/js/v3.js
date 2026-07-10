/* ============================================================================
   MUSEU EM FIOS — V3 · "Do amanhecer à noite"
   Sol/lua percorrem o céu no scroll, o relógio do ritual acompanha as cenas
   e as ilustrações em line-art se desenham como um fio.
   Degrada com segurança: sem GSAP ou com reduced-motion, as cenas ficam
   estáticas (cada uma com seu gradiente próprio) e 100% legíveis.
============================================================================ */

(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (typeof window.gsap === "undefined") return;
  var gsap = window.gsap;
  if (!window.ScrollTrigger) return;
  gsap.registerPlugin(window.ScrollTrigger);

  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }

  var astro = $(".v3-astro");
  var lua = $(".v3-lua");
  var estrelas = $(".v3-estrelas");
  var relogio = $(".v3-relogio");

  /* Relógio do ritual acompanha a cena visível */
  $$(".v3-cena").forEach(function (cena) {
    var quando = cena.getAttribute("data-relogio");
    if (!quando || !relogio) return;
    window.ScrollTrigger.create({
      trigger: cena,
      start: "top 55%",
      end: "bottom 55%",
      onEnter: function () { relogio.textContent = quando; },
      onEnterBack: function () { relogio.textContent = quando; }
    });
  });

  /* Relógio muda de cor na noite */
  var noite = $(".v3-cena--noite");
  if (noite && relogio) {
    window.ScrollTrigger.create({
      trigger: noite,
      start: "top 55%",
      onEnter: function () { relogio.style.color = "#fbfaf6"; },
      onLeaveBack: function () { relogio.style.color = "#1d1d1b"; }
    });
  }

  if (!reduced && astro) {
    /* O sol atravessa o dia: sobe de manhã, desce e esquenta no fim de
       tarde, se põe quando a noite chega */
    var tarde = $(".v3-cena--tarde");
    if (tarde) {
      gsap.timeline({
        scrollTrigger: { trigger: tarde, start: "top bottom", end: "bottom center", scrub: 0.6 }
      })
        .to(astro, { left: "16vw", top: "56vh", background: "#e08a56", boxShadow: "0 0 90px 34px rgba(224,138,86,0.4)", ease: "none" }, 0);
    }
    if (noite) {
      gsap.timeline({
        scrollTrigger: { trigger: noite, start: "top bottom", end: "top 25%", scrub: 0.6 }
      })
        .to(astro, { top: "118vh", autoAlpha: 0, ease: "none" }, 0)
        .to(lua, { opacity: 1, ease: "none" }, 0.3)
        .to(estrelas, { opacity: 1, ease: "none" }, 0.25);
    }
  } else if (astro) {
    gsap.set(astro, { autoAlpha: 0.9 });
    if (lua) gsap.set(lua, { opacity: 1 });
  }

  /* As cenas em line-art se desenham como um fio */
  $$(".v3-arte").forEach(function (svg) {
    var tracos = $$("path, circle, line, rect", svg);
    tracos.forEach(function (t) {
      var len = t.getTotalLength ? t.getTotalLength() : 0;
      if (!len) return;
      t.style.strokeDasharray = len;
      t.style.strokeDashoffset = reduced ? 0 : len;
    });
    if (reduced) return;
    gsap.to(tracos, {
      strokeDashoffset: 0,
      duration: 2.2,
      ease: "power2.inOut",
      stagger: 0.12,
      scrollTrigger: { trigger: svg, start: "top 78%", once: true }
    });
  });

  /* Halo do abajur pulsa devagar */
  var halo = $(".v3-halo");
  if (halo && !reduced) {
    gsap.to(halo, { opacity: 0.55, scale: 1.06, duration: 3.2, ease: "sine.inOut", yoyo: true, repeat: -1 });
  }
})();
