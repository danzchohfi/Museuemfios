/* ============================================================================
   MUSEU EM FIOS — V4 · "O Entardecer"
   O fio da marca em três dimensões: dois fios dourados de seda atravessam a
   golden hour em ondulação contínua (three.js), e o quadro responde ao mouse
   com uma inclinação sutil. Degrada com segurança: sem WebGL ou com
   prefers-reduced-motion, fica o céu em CSS e o quadro estático.
============================================================================ */

import * as THREE from "./vendor/three.module.min.js";

(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------ quadro com tilt 3D -- */
  var quadro = document.querySelector(".v4-quadro__moldura");
  if (quadro && !reduced && window.matchMedia("(hover: hover)").matches) {
    var alvoRX = 0, alvoRY = 0, rx = 0, ry = 0;
    document.addEventListener("mousemove", function (e) {
      var nx = e.clientX / window.innerWidth - 0.5;
      var ny = e.clientY / window.innerHeight - 0.5;
      alvoRY = nx * 10;
      alvoRX = -ny * 8;
    });
    (function tiltFrame() {
      rx += (alvoRX - rx) * 0.06;
      ry += (alvoRY - ry) * 0.06;
      quadro.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
      requestAnimationFrame(tiltFrame);
    })();
  }

  /* --------------------------------------------------------- fio em 3D -- */
  var alvo = document.querySelector(".v4-fio3d");
  if (!alvo) return;

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
  } catch (e) {
    return; /* sem WebGL: fica o céu em CSS */
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  alvo.appendChild(renderer.domElement);

  var cena = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(38, 1, 0.1, 60);
  camera.position.set(0, 0, 7);

  /* luz do entardecer: âmbar vindo do horizonte, fill fria do céu */
  cena.add(new THREE.AmbientLight(0x5a4666, 1.1));
  var solPoente = new THREE.DirectionalLight(0xffc46b, 2.6);
  solPoente.position.set(0, -3, 4);
  cena.add(solPoente);
  var ceuFrio = new THREE.DirectionalLight(0x7a6a9e, 0.8);
  ceuFrio.position.set(2, 4, 2);
  cena.add(ceuFrio);

  /* dois fios de seda: um dourado em primeiro plano, um âmbar ao fundo */
  function criaFio(cor, raio, profundidade, fase, amplitude) {
    var N = 7;
    var pontos = [];
    for (var i = 0; i < N; i++) {
      pontos.push(new THREE.Vector3((i / (N - 1)) * 16 - 8, 0, profundidade));
    }
    var material = new THREE.MeshStandardMaterial({
      color: cor,
      metalness: 0.45,
      roughness: 0.32,
      emissive: cor,
      emissiveIntensity: 0.08
    });
    var malha = new THREE.Mesh(new THREE.BufferGeometry(), material);
    cena.add(malha);
    return {
      malha: malha,
      atualiza: function (t) {
        for (var i = 0; i < N; i++) {
          var p = pontos[i];
          p.y = Math.sin(t * 0.45 + fase + i * 0.9) * amplitude
              + Math.sin(t * 0.2 + fase * 2 + i * 0.35) * amplitude * 0.5
              - 0.4;
          p.z = profundidade + Math.cos(t * 0.3 + fase + i * 0.7) * 0.7;
        }
        var curva = new THREE.CatmullRomCurve3(pontos);
        var geometria = new THREE.TubeGeometry(curva, 180, raio, 10, false);
        malha.geometry.dispose();
        malha.geometry = geometria;
      }
    };
  }

  var fios = [
    criaFio(0xf2c440, 0.045, 0.6, 0, 1.15),
    criaFio(0xd98e4f, 0.028, -1.6, 2.1, 1.5)
  ];

  function dimensiona() {
    var w = alvo.clientWidth, h = alvo.clientHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  dimensiona();
  window.addEventListener("resize", dimensiona);

  /* câmera respira com o mouse */
  var mx = 0, my = 0;
  if (!reduced) {
    document.addEventListener("mousemove", function (e) {
      mx = (e.clientX / window.innerWidth - 0.5) * 0.7;
      my = (e.clientY / window.innerHeight - 0.5) * 0.4;
    });
  }

  /* renderiza só com o hero visível e a aba ativa */
  var ativo = true;
  new IntersectionObserver(function (entradas) {
    ativo = entradas[0].isIntersecting;
  }).observe(alvo);

  var inicio = performance.now();
  function quadroAnim(agora) {
    requestAnimationFrame(quadroAnim);
    if (!ativo || document.hidden) return;
    var t = (agora - inicio) / 1000;
    fios.forEach(function (f) { f.atualiza(reduced ? 0 : t); });
    camera.position.x += (mx - camera.position.x) * 0.04;
    camera.position.y += (-my - camera.position.y) * 0.04;
    camera.lookAt(0, -0.3, 0);
    renderer.render(cena, camera);
  }

  if (reduced) {
    fios.forEach(function (f) { f.atualiza(1.8); });
    renderer.render(cena, camera);
  } else {
    requestAnimationFrame(quadroAnim);
  }
})();
