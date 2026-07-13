/* ============================================================================
   MUSEU EM FIOS — V5 · "O Fio"
   1) A meada em 3D: cinco fios de bordado (cores da identidade) trançados
      numa mesma onda atravessam a golden hour (three.js).
   2) O fio-costura: um fio contínuo costura a página no scroll, puxado por
      uma agulha — e "entra no tecido" quando passa sob a faixa amarela.
   Degrada com segurança: sem WebGL/GSAP ou com reduced-motion, ficam o céu
   em CSS, a tela do bordado estática e nenhuma costura.
============================================================================ */

import * as THREE from "./vendor/three.module.min.js";

(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------- tela do bordado com tilt 3D -- */
  var tela = document.querySelector(".v5-tela");
  if (tela && !reduced && window.matchMedia("(hover: hover)").matches) {
    var aRX = 0, aRY = 0, rx = 0, ry = 0;
    document.addEventListener("mousemove", function (e) {
      aRY = (e.clientX / window.innerWidth - 0.5) * 10;
      aRX = -(e.clientY / window.innerHeight - 0.5) * 8;
    });
    (function tilt() {
      rx += (aRX - rx) * 0.06;
      ry += (aRY - ry) * 0.06;
      tela.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
      requestAnimationFrame(tilt);
    })();
  }

  /* ------------------------------------------------- a meada em 3D -- */
  var alvo = document.querySelector(".v4-fio3d");
  if (alvo) {
    var renderer = null;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
    } catch (e) { renderer = null; }

    if (renderer) {
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      alvo.appendChild(renderer.domElement);

      var cena = new THREE.Scene();
      var camera = new THREE.PerspectiveCamera(38, 1, 0.1, 60);
      camera.position.set(0, 0, 7);

      cena.add(new THREE.AmbientLight(0x5a4666, 1.1));
      var poente = new THREE.DirectionalLight(0xffc46b, 2.4);
      poente.position.set(0, -3, 4);
      cena.add(poente);
      var ceu = new THREE.DirectionalLight(0x7a6a9e, 0.8);
      ceu.position.set(2, 4, 2);
      cena.add(ceu);

      /* Cinco fios da mesma meada: seguem a MESMA onda, cada um deslocado
         um pouco — como fios de bordado correndo juntos e se trançando. */
      var CORES = [0xf2c440, 0xe0a94f, 0x9cad4e, 0x6a9cc3, 0xd98e4f];
      var N = 8;

      function base(i, t) {
        var x = (i / (N - 1)) * 17 - 8.5;
        var y = Math.sin(t * 0.4 + i * 0.85) * 1.05
              + Math.sin(t * 0.18 + i * 0.33) * 0.55 - 0.35;
        var z = Math.cos(t * 0.26 + i * 0.6) * 0.8 - 0.4;
        return { x: x, y: y, z: z };
      }

      var fios = CORES.map(function (cor, f) {
        var mat = new THREE.MeshStandardMaterial({
          color: cor, metalness: 0.4, roughness: 0.38,
          emissive: cor, emissiveIntensity: 0.06
        });
        var malha = new THREE.Mesh(new THREE.BufferGeometry(), mat);
        cena.add(malha);
        var pontos = [];
        for (var i = 0; i < N; i++) pontos.push(new THREE.Vector3());
        return { malha: malha, pontos: pontos, idx: f };
      });

      function atualizaFios(t) {
        fios.forEach(function (fio) {
          var f = fio.idx;
          for (var i = 0; i < N; i++) {
            var b = base(i, t);
            /* trança: cada fio gira em volta do eixo da meada */
            var ang = t * 0.5 + i * 0.55 + (f / CORES.length) * Math.PI * 2;
            fio.pontos[i].set(
              b.x,
              b.y + Math.cos(ang) * 0.16,
              b.z + Math.sin(ang) * 0.16
            );
          }
          var curva = new THREE.CatmullRomCurve3(fio.pontos);
          var geo = new THREE.TubeGeometry(curva, 150, 0.03, 8, false);
          fio.malha.geometry.dispose();
          fio.malha.geometry = geo;
        });
      }

      function dimensiona() {
        renderer.setSize(alvo.clientWidth, alvo.clientHeight);
        camera.aspect = alvo.clientWidth / alvo.clientHeight;
        camera.updateProjectionMatrix();
      }
      dimensiona();
      window.addEventListener("resize", dimensiona);

      var mx = 0, my = 0;
      if (!reduced) {
        document.addEventListener("mousemove", function (e) {
          mx = (e.clientX / window.innerWidth - 0.5) * 0.7;
          my = (e.clientY / window.innerHeight - 0.5) * 0.4;
        });
      }

      var ativo = true;
      new IntersectionObserver(function (en) { ativo = en[0].isIntersecting; }).observe(alvo);

      var inicio = performance.now();
      if (reduced) {
        atualizaFios(2.4);
        renderer.render(cena, camera);
      } else {
        (function frame(agora) {
          requestAnimationFrame(frame);
          if (!ativo || document.hidden) return;
          atualizaFios((agora - inicio) / 1000);
          camera.position.x += (mx - camera.position.x) * 0.04;
          camera.position.y += (-my - camera.position.y) * 0.04;
          camera.lookAt(0, -0.3, 0);
          renderer.render(cena, camera);
        })(inicio);
      }
    }
  }

  /* --------------------------------------- o fio que costura a página -- */
  if (typeof window.gsap === "undefined" || !window.ScrollTrigger || reduced) return;
  var gsap = window.gsap;
  gsap.registerPlugin(window.ScrollTrigger);

  var main = document.querySelector("main");
  var hero = document.querySelector(".v4-hero");
  if (!main || !hero) return;

  function montaCostura() {
    var antiga = main.querySelector(".v5-costura");
    if (antiga) antiga.remove();

    var W = main.clientWidth;
    var H = main.scrollHeight;
    var y0 = hero.offsetHeight - 40;

    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("class", "v5-costura");
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("aria-hidden", "true");

    /* serpenteia do fim do hero ao rodapé, com um nó no final */
    var xC = W / 2, xL = W * 0.12, xR = W * 0.88;
    var passo = (H - y0 - 260) / 6;
    var y = y0;
    var d = "M " + (W * 0.62) + " " + y;
    d += " C " + xR + " " + (y + passo * 0.5) + ", " + xR + " " + (y + passo * 0.6) + ", " + xC + " " + (y + passo);
    d += " S " + xL + " " + (y + passo * 1.8) + ", " + (W * 0.38) + " " + (y + passo * 2.2);
    d += " S " + xR + " " + (y + passo * 3.1) + ", " + (W * 0.6) + " " + (y + passo * 3.6);
    d += " S " + xL + " " + (y + passo * 4.5) + ", " + (W * 0.4) + " " + (y + passo * 5);
    d += " S " + xC + " " + (y + passo * 5.7) + ", " + (W * 0.52) + " " + (y + passo * 6);
    /* nó de arremate */
    var nx = W * 0.52, ny = y + passo * 6 + 60;
    d += " C " + (nx + 30) + " " + (ny + 20) + ", " + (nx - 30) + " " + (ny + 34) + ", " + (nx + 4) + " " + (ny + 40);
    d += " C " + (nx + 26) + " " + (ny + 44) + ", " + (nx - 8) + " " + (ny + 58) + ", " + nx + " " + (ny + 62);

    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", d);
    svg.appendChild(path);

    /* a agulha que puxa o fio */
    var agulha = document.createElementNS("http://www.w3.org/2000/svg", "path");
    agulha.setAttribute("class", "v5-agulha");
    agulha.setAttribute("d", "M0 0 L46 -2.6 Q54 0 46 2.6 Z M8 0 a2.6 4 0 1 0 0.1 0");
    agulha.setAttribute("fill-rule", "evenodd");
    svg.appendChild(agulha);

    main.appendChild(svg);

    var len = path.getTotalLength();
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len;

    var estado = { p: 0 };
    gsap.to(estado, {
      p: 1,
      ease: "none",
      scrollTrigger: {
        trigger: main,
        start: "top top",
        end: "bottom bottom",
        scrub: 0.8,
        invalidateOnRefresh: true
      },
      onUpdate: function () {
        var l = len * estado.p;
        path.style.strokeDashoffset = len - l;
        var pt = path.getPointAtLength(l);
        var antes = path.getPointAtLength(Math.max(0, l - 2));
        var ang = Math.atan2(pt.y - antes.y, pt.x - antes.x) * 180 / Math.PI;
        agulha.setAttribute("transform", "translate(" + pt.x + " " + pt.y + ") rotate(" + ang + ")");
        agulha.style.opacity = estado.p > 0.001 && estado.p < 0.999 ? 1 : 0;
      }
    });
  }

  if (document.readyState === "complete") montaCostura();
  else window.addEventListener("load", montaCostura);

  var tRedim;
  window.addEventListener("resize", function () {
    clearTimeout(tRedim);
    tRedim = setTimeout(function () {
      montaCostura();
      window.ScrollTrigger.refresh();
    }, 300);
  });
})();
