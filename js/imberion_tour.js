/* ============================================================================
   imberion_tour.js — Tour guiado de Imberion (welcome modal + spotlight + tooltip)
   ----------------------------------------------------------------------------
   Vanilla, sin dependencias. Cae en cualquier HTML (cargado del CDN o pegado
   inline). Pareja de imberion_tour.css. Misma idea que el tour del portal
   (driver.js) pero autocontenido para entregables HTML sueltos.

   USO
   ---
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/css/imberion_tour.css"/>
   <script src="https://cdn.jsdelivr.net/gh/rogarridoe/imberion-brand@main/js/imberion_tour.js"></script>
   <script>
     ImberionTour.init({
       tourId: 'temisa-asis',                 // clave de localStorage (requerido)
       reactivarDias: 45,                      // opcional: re-arranca tras N días sin entrar
       welcome: {
         eyebrow: 'Guía rápida',
         titulo: 'Cómo leer este documento',
         texto: 'Un recorrido de 30 segundos para sacarle provecho.'
       },
       pasos: [
         { element: '#tabs', title: 'Cinco pestañas', description: 'Cada pestaña es un proceso.', side: 'bottom' },
         { element: '.tab.hall', title: 'Hallazgos es una pestaña', description: 'No es un encabezado: es clickeable.' },
         { element: '#diagwrap', title: 'El flujo de hoy', description: 'Las cajas en acento son oportunidades.', side: 'top',
           alMostrar: function () { show('captacion'); } }   // hook opcional por paso
       ]
     });
   </script>

   Un paso sin `element` se muestra centrado (sirve de mensaje intermedio).
   Los pasos cuyo elemento no está en la página se omiten solos.
   Re-activar: el botón flotante "?" reabre el welcome; ImberionTour.reset()
   borra el "visto" para que vuelva a arrancar en la siguiente carga.
   ============================================================================ */

window.ImberionTour = (function () {
  'use strict';

  var PREFIX = 'imb_tour_';
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  var cfg = null;     // config actual
  var pasos = [];     // pasos visibles
  var idx = 0;
  var nodes = null;   // refs del DOM

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  function textos() {
    var t = (cfg && cfg.textos) || {};
    return {
      empezar: t.empezar || 'Empezar recorrido',
      ahora_no: t.ahora_no || 'Ahora no',
      saltar: t.saltar || 'Saltar',
      atras: t.atras || 'Atrás',
      siguiente: t.siguiente || 'Siguiente',
      listo: t.listo || 'Entendido'
    };
  }

  function construirDOM() {
    if (nodes) return nodes;

    var fab = el('button', 'imb-tour-fab', '?');
    fab.type = 'button';
    fab.setAttribute('aria-label', 'Abrir la guía de la página');
    fab.title = 'Abrir la guía de la página';

    var welcome = el('div', 'imb-tour-welcome',
      '<div class="imb-tour-card" role="dialog" aria-modal="true" aria-label="Guía de lectura">' +
        '<div class="imb-tour-eyebrow"></div>' +
        '<h3></h3>' +
        '<p></p>' +
        '<div class="imb-tour-wbtns">' +
          '<button type="button" class="imb-tour-b is-primary imb-tour-empezar"></button>' +
          '<button type="button" class="imb-tour-b is-ghost imb-tour-ahorano"></button>' +
        '</div>' +
        '<div class="imb-tour-note"></div>' +
      '</div>');

    var ov = el('div', 'imb-tour-ov');
    var spot = el('div', 'imb-tour-spot');
    var tip = el('div', 'imb-tour-tip',
      '<div class="imb-tour-num"></div>' +
      '<h4></h4>' +
      '<p></p>' +
      '<div class="imb-tour-row">' +
        '<div class="imb-tour-dots"></div>' +
        '<div class="imb-tour-btns">' +
          '<button type="button" class="imb-tour-b is-ghost imb-tour-saltar"></button>' +
          '<button type="button" class="imb-tour-b imb-tour-atras"></button>' +
          '<button type="button" class="imb-tour-b is-primary imb-tour-siguiente"></button>' +
        '</div>' +
      '</div>');
    ov.appendChild(spot);
    ov.appendChild(tip);

    document.body.appendChild(fab);
    document.body.appendChild(welcome);
    document.body.appendChild(ov);

    nodes = {
      fab: fab, welcome: welcome, ov: ov, spot: spot, tip: tip,
      eyebrow: welcome.querySelector('.imb-tour-eyebrow'),
      wtitle: welcome.querySelector('h3'),
      wtext: welcome.querySelector('p'),
      wnote: welcome.querySelector('.imb-tour-note'),
      empezar: welcome.querySelector('.imb-tour-empezar'),
      ahorano: welcome.querySelector('.imb-tour-ahorano'),
      num: tip.querySelector('.imb-tour-num'),
      ttitle: tip.querySelector('h4'),
      ttext: tip.querySelector('p'),
      dots: tip.querySelector('.imb-tour-dots'),
      saltar: tip.querySelector('.imb-tour-saltar'),
      atras: tip.querySelector('.imb-tour-atras'),
      siguiente: tip.querySelector('.imb-tour-siguiente')
    };

    fab.addEventListener('click', abrirWelcome);
    nodes.empezar.addEventListener('click', function () { cerrarWelcome(); start(); });
    nodes.ahorano.addEventListener('click', function () { cerrarWelcome(); marcarVisto(); });
    nodes.siguiente.addEventListener('click', siguiente);
    nodes.atras.addEventListener('click', atras);
    nodes.saltar.addEventListener('click', terminar);

    return nodes;
  }

  function abrirWelcome() {
    construirDOM();
    var w = cfg.welcome || {};
    var tx = textos();
    nodes.eyebrow.textContent = w.eyebrow || 'Guía rápida';
    nodes.wtitle.textContent = w.titulo || 'Cómo leer este documento';
    nodes.wtext.innerHTML = w.texto || 'Un recorrido corto para sacarle provecho.';
    nodes.wnote.innerHTML = w.nota || 'Puedes reabrir esta guía con el botón <b>?</b> abajo a la derecha.';
    nodes.empezar.textContent = tx.empezar;
    nodes.ahorano.textContent = tx.ahora_no;
    nodes.welcome.classList.add('is-open');
  }
  function cerrarWelcome() { if (nodes) nodes.welcome.classList.remove('is-open'); }

  function start() {
    construirDOM();
    pasos = (cfg.pasos || []).filter(function (p) {
      return !p.element || document.querySelector(p.element);
    });
    if (!pasos.length) { marcarVisto(); return; }
    nodes.dots.innerHTML = '';
    for (var i = 0; i < pasos.length; i++) nodes.dots.appendChild(el('i'));
    idx = 0;
    nodes.ov.classList.add('is-open');
    document.addEventListener('keydown', onKey);
    window.addEventListener('resize', colocar);
    window.addEventListener('scroll', colocar, true);
    colocar();
  }

  function colocar() {
    if (!nodes) return;
    var tx = textos();
    var p = pasos[idx];
    var target = p.element ? document.querySelector(p.element) : null;

    nodes.num.textContent = 'Paso ' + (idx + 1) + ' de ' + pasos.length;
    nodes.ttitle.textContent = p.title || '';
    nodes.ttext.innerHTML = p.description || '';
    var dd = nodes.dots.children;
    for (var k = 0; k < dd.length; k++) dd[k].className = (k === idx ? 'is-on' : '');
    nodes.atras.style.visibility = idx === 0 ? 'hidden' : 'visible';
    nodes.atras.textContent = tx.atras;
    nodes.saltar.textContent = tx.saltar;
    nodes.siguiente.textContent = idx === pasos.length - 1 ? tx.listo : tx.siguiente;

    if (typeof p.alMostrar === 'function') { try { p.alMostrar(); } catch (e) {} }

    var vw = window.innerWidth, vh = window.innerHeight;

    // medir el tooltip sin parpadeo
    nodes.tip.style.display = 'block';
    nodes.tip.style.visibility = 'hidden';
    var tw = nodes.tip.offsetWidth, th = nodes.tip.offsetHeight, gap = 12;

    if (!target) {
      // paso centrado: spotlight nulo, tooltip al centro
      nodes.spot.style.top = (vh / 2) + 'px';
      nodes.spot.style.left = (vw / 2) + 'px';
      nodes.spot.style.width = '0px';
      nodes.spot.style.height = '0px';
      nodes.tip.style.top = Math.max(12, (vh - th) / 2) + 'px';
      nodes.tip.style.left = Math.max(12, (vw - tw) / 2) + 'px';
      nodes.tip.style.visibility = 'visible';
      return;
    }

    if (target.scrollIntoView) target.scrollIntoView({ block: 'nearest' });
    var r = target.getBoundingClientRect();
    var pad = 7;
    var top = Math.max(r.top - pad, 4), left = Math.max(r.left - pad, 4);
    var bottom = Math.min(r.bottom + pad, vh - 4), right = Math.min(r.right + pad, vw - 4);
    nodes.spot.style.top = top + 'px';
    nodes.spot.style.left = left + 'px';
    nodes.spot.style.width = (right - left) + 'px';
    nodes.spot.style.height = (bottom - top) + 'px';

    var side = p.side || 'auto';
    var ty;
    if (side === 'top') { ty = r.top - th - gap; if (ty < 10) ty = r.bottom + gap; }
    else { ty = r.bottom + gap; if (ty + th > vh - 10) ty = r.top - th - gap; }
    if (ty < 10 || ty + th > vh - 10) ty = vh - th - 16;
    var tlx = r.left + r.width / 2 - tw / 2;
    tlx = Math.max(12, Math.min(tlx, vw - tw - 12));
    nodes.tip.style.top = ty + 'px';
    nodes.tip.style.left = tlx + 'px';
    nodes.tip.style.visibility = 'visible';
  }

  function siguiente() { if (idx < pasos.length - 1) { idx++; colocar(); } else { terminar(); } }
  function atras() { if (idx > 0) { idx--; colocar(); } }
  function onKey(e) {
    if (e.key === 'Escape') terminar();
    else if (e.key === 'ArrowRight') siguiente();
    else if (e.key === 'ArrowLeft') atras();
  }
  function terminar() {
    if (!nodes) return;
    nodes.ov.classList.remove('is-open');
    nodes.tip.style.display = 'none';
    document.removeEventListener('keydown', onKey);
    window.removeEventListener('resize', colocar);
    window.removeEventListener('scroll', colocar, true);
    marcarVisto();
  }

  function marcarVisto() {
    if (!cfg) return;
    try { localStorage.setItem(PREFIX + cfg.tourId + '_visto', String(Date.now())); } catch (e) {}
  }
  function debeArrancar() {
    try {
      var ahora = Date.now();
      var visto = Number(localStorage.getItem(PREFIX + cfg.tourId + '_visto') || 0);
      var ultima = Number(localStorage.getItem(PREFIX + cfg.tourId + '_visita') || 0);
      localStorage.setItem(PREFIX + cfg.tourId + '_visita', String(ahora));
      if (!visto) return true;
      if (cfg.reactivarDias && ultima && (ahora - ultima > cfg.reactivarDias * 86400000)) return true;
      return false;
    } catch (e) { return false; }
  }
  function reset() {
    if (!cfg) return;
    try {
      localStorage.removeItem(PREFIX + cfg.tourId + '_visto');
      localStorage.removeItem(PREFIX + cfg.tourId + '_visita');
    } catch (e) {}
  }

  function arranque() {
    construirDOM();
    if (cfg.boton === false) nodes.fab.style.display = 'none';
    var arrancar = debeArrancar();   // siempre registra la visita
    if (cfg.auto !== false && arrancar) {
      setTimeout(abrirWelcome, cfg.delay != null ? cfg.delay : 400);
    }
  }
  function init(config) {
    cfg = config || {};
    if (!cfg.tourId) cfg.tourId = 'default';
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', arranque);
    } else {
      arranque();
    }
  }

  return { init: init, start: start, abrir: abrirWelcome, reset: reset };
})();
