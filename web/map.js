/* The plan of a floor with the route drawn on it: image, line, markers, pan and zoom.
   Everything is in plan pixels (meters divided by meters_per_pixel), the same unit as the image. */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var MIN_W = 160;
  var NICE = [1, 2, 5, 10, 20, 50, 100, 200];

  var ICON_OPEN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
  var ICONS = {
    stairs: ICON_OPEN + '<path d="M4 20h4v-4h4v-4h4V8h4"/></svg>',
    elevator: ICON_OPEN + '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 10l3-3 3 3M9 14l3 3 3-3"/></svg>',
    ramp: ICON_OPEN + '<path d="M3 19h18L3 9z"/></svg>',
    next: ICON_OPEN + '<path d="M9 6l6 6-6 6"/></svg>',
    prev: ICON_OPEN + '<path d="M15 6l-6 6 6 6"/></svg>',
    wrench: ICON_OPEN + '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.8-.8-.8-2.8z"/></svg>'
  };
  var CHEVRON = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5l8 5.5-8 5.5z" fill="#FFFFFF" stroke="#E8590C" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  var PIN = '<svg width="34" height="40" viewBox="0 0 34 40" aria-hidden="true"><path d="M17 38C17 38 30 25.5 30 16.5a13 13 0 0 0-26 0C4 25.5 17 38 17 38z" fill="#1F3A5F" stroke="#FFFFFF" stroke-width="2.4" stroke-linejoin="round"/><path d="M12.5 22V11M12.5 11.5h8.5l-1.6 3 1.6 3h-8.5" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var CONNECTION_NAME = { stairs: 'da escada', elevator: 'do elevador', ramp: 'da rampa' };

  function esc(text) {
    return String(text).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function clamp(value, low, high) {
    return Math.min(Math.max(value, low), high);
  }

  function RouteMap(options) {
    this.root = options.root;
    this.svg = options.svg;
    this.overlay = options.overlay;
    this.tabs = options.tabs;
    this.scaleBox = options.scale;
    this.hint = options.hint;
    this.onStep = options.onStep || function () {};
    this.onFloor = options.onFloor || function () {};
    this.onError = options.onError || function () {};
    this.loadImage = options.loadImage || function (url) { return Promise.resolve(url); };
    this.floors = [];
    this.floorsById = {};
    this.places = [];
    this.floorId = null;
    this.size = { w: 0, h: 0 };
    this.view = { x: 0, y: 0, w: 4000, h: 2448 };
    this.pendingFit = false;
    this.imageEl = null;
    this.pathsEl = null;
    this.route = null;
    this.selected = 0;
    this.runs = [];
    this.stepPaths = [];
    this.stepEnds = [];
    this.items = [];
    this.maint = [];
    this._bind();
  }

  RouteMap.prototype.floor = function () {
    return this.floorsById[this.floorId] || null;
  };

  RouteMap.prototype.setFloors = function (floors) {
    var self = this;
    this.floors = floors.slice().sort(function (a, b) { return a.level - b.level; });
    this.floorsById = {};
    this.floors.forEach(function (f) { self.floorsById[f.id] = f; });
    if (this.floors.length && this.floorId === null) {
      this.showFloor(this.floors[0].id, true);
    } else {
      this.renderTabs();
    }
  };

  RouteMap.prototype.setPlaces = function (places) {
    this.places = places;
  };

  RouteMap.prototype.showFloor = function (id, fit) {
    var f = this.floorsById[id];
    if (!f) { return; }
    var changed = this.floorId !== id;
    this.floorId = id;
    if (changed || !this.imageEl) {
      while (this.svg.firstChild) { this.svg.removeChild(this.svg.firstChild); }
      var self = this;
      var image = document.createElementNS(NS, 'image');
      this.loadImage(f.plan_url).then(function (src) {
        image.setAttribute('href', src);
      }, function (error) {
        if (self.imageEl === image) { self.onError(error); }
      });
      image.setAttribute('x', '0');
      image.setAttribute('y', '0');
      image.setAttribute('width', f.width_px);
      image.setAttribute('height', f.height_px);
      this.svg.appendChild(image);
      this.imageEl = image;
      this.pathsEl = document.createElementNS(NS, 'g');
      this.svg.appendChild(this.pathsEl);
    }
    this.renderTabs();
    this.renderPaths();
    if (fit) { this.fit(); } else { this.render(); }
  };

  RouteMap.prototype._routeBox = function (floorId) {
    var box = null;
    this.runs.forEach(function (run) {
      if (run.floorId !== floorId) { return; }
      run.pts.forEach(function (p) {
        if (!box) { box = { minX: p[0], maxX: p[0], minY: p[1], maxY: p[1] }; return; }
        box.minX = Math.min(box.minX, p[0]);
        box.maxX = Math.max(box.maxX, p[0]);
        box.minY = Math.min(box.minY, p[1]);
        box.maxY = Math.max(box.maxY, p[1]);
      });
    });
    return box;
  };

  RouteMap.prototype._floorBox = function (f) {
    var box = null;
    this.places.forEach(function (p) {
      if (p.floor_id !== f.id) { return; }
      var x = p.x / f.meters_per_pixel;
      var y = p.y / f.meters_per_pixel;
      if (!box) { box = { minX: x, maxX: x, minY: y, maxY: y }; return; }
      box.minX = Math.min(box.minX, x);
      box.maxX = Math.max(box.maxX, x);
      box.minY = Math.min(box.minY, y);
      box.maxY = Math.max(box.maxY, y);
    });
    return box || { minX: 0, maxX: f.width_px, minY: 0, maxY: f.height_px };
  };

  RouteMap.prototype.fit = function () {
    var f = this.floor();
    if (!f) { return; }
    if (!this.size.w || !this.size.h) { this.pendingFit = true; return; }
    this.pendingFit = false;
    var box = this._routeBox(f.id);
    var pad = box ? 0.22 : 0.06;
    box = box || this._floorBox(f);
    var aspect = this.size.w / this.size.h;
    var w = Math.max((box.maxX - box.minX) * (1 + 2 * pad), 700);
    var h = Math.max((box.maxY - box.minY) * (1 + 2 * pad), 700 / aspect);
    if (w / h < aspect) { w = h * aspect; } else { h = w / aspect; }
    this.view = {
      x: (box.minX + box.maxX) / 2 - w / 2,
      y: (box.minY + box.maxY) / 2 - h / 2 - 40 * (w / this.size.w),
      w: w,
      h: h
    };
    this._clamp();
    this.render();
  };

  RouteMap.prototype._clamp = function () {
    var f = this.floor();
    if (!f || !this.size.w) { return; }
    var aspect = this.size.w / this.size.h;
    var w = clamp(this.view.w, MIN_W, f.width_px);
    var h = w / aspect;
    var cx = clamp(this.view.x + this.view.w / 2, 0, f.width_px);
    var cy = clamp(this.view.y + this.view.h / 2, 0, f.height_px);
    this.view = { x: cx - w / 2, y: cy - h / 2, w: w, h: h };
  };

  RouteMap.prototype._resize = function () {
    var w = this.root.clientWidth;
    var h = this.root.clientHeight;
    if (!w || !h) { return; }
    var first = !this.size.w;
    this.size = { w: w, h: h };
    if (first || this.pendingFit) { this.fit(); return; }
    var cx = this.view.x + this.view.w / 2;
    var cy = this.view.y + this.view.h / 2;
    var vw = this.view.w;
    var vh = vw * h / w;
    this.view = { x: cx - vw / 2, y: cy - vh / 2, w: vw, h: vh };
    this._clamp();
    this.render();
  };

  RouteMap.prototype._pan = function (dx, dy) {
    var k = this.view.w / this.size.w;
    this.view.x -= dx * k;
    this.view.y -= dy * k;
    this._clamp();
    this.render();
  };

  RouteMap.prototype.zoomAt = function (factor, cx, cy) {
    var f = this.floor();
    if (!f || !this.size.w) { return; }
    var v = this.view;
    var k = v.w / this.size.w;
    var px = v.x + cx * k;
    var py = v.y + cy * k;
    var nw = clamp(v.w * factor, MIN_W, f.width_px);
    var nk = nw / this.size.w;
    this.view = { x: px - cx * nk, y: py - cy * nk, w: nw, h: nw * this.size.h / this.size.w };
    this._clamp();
    this.render();
  };

  RouteMap.prototype._bind = function () {
    var self = this;
    var root = this.root;
    var pointers = {};

    function local(e) {
      var r = root.getBoundingClientRect();
      return { x: e.clientX - r.left, y: e.clientY - r.top };
    }

    root.addEventListener('pointerdown', function (e) {
      if (e.target.closest('button, .tabs, .zoom')) { return; }
      pointers[e.pointerId] = local(e);
      try { root.setPointerCapture(e.pointerId); } catch (err) { /* not every browser has it */ }
      root.classList.add('drag');
    });
    root.addEventListener('pointermove', function (e) {
      var prev = pointers[e.pointerId];
      if (!prev) { return; }
      var cur = local(e);
      var ids = Object.keys(pointers);
      if (ids.length === 1) {
        self._pan(cur.x - prev.x, cur.y - prev.y);
      } else if (ids.length === 2) {
        var other = pointers[ids[0] === String(e.pointerId) ? ids[1] : ids[0]];
        var before = Math.hypot(prev.x - other.x, prev.y - other.y);
        var after = Math.hypot(cur.x - other.x, cur.y - other.y);
        if (before > 0 && after > 0) { self.zoomAt(before / after, (cur.x + other.x) / 2, (cur.y + other.y) / 2); }
      }
      pointers[e.pointerId] = cur;
    });
    function end(e) {
      delete pointers[e.pointerId];
      if (!Object.keys(pointers).length) { root.classList.remove('drag'); }
    }
    root.addEventListener('pointerup', end);
    root.addEventListener('pointercancel', end);
    root.addEventListener('wheel', function (e) {
      e.preventDefault();
      var p = local(e);
      var dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
      self.zoomAt(Math.exp(dy * 0.0015), p.x, p.y);
    }, { passive: false });

    root.addEventListener('click', function (e) {
      var el = e.target.closest('[data-act], [data-floor], [data-zoom]');
      if (!el || !root.contains(el)) { return; }
      if (el.getAttribute('data-act') === 'step') {
        self.onStep(Number(el.getAttribute('data-i')));
      } else if (el.hasAttribute('data-floor')) {
        var id = Number(el.getAttribute('data-floor'));
        self.showFloor(id, true);
        self.onFloor(id);
      } else if (el.hasAttribute('data-zoom')) {
        var kind = el.getAttribute('data-zoom');
        if (kind === 'fit') { self.fit(); } else { self.zoomAt(kind === 'in' ? 1 / 1.5 : 1.5, self.size.w / 2, self.size.h / 2); }
      }
    });

    if (window.ResizeObserver) {
      new ResizeObserver(function () { self._resize(); }).observe(root);
    } else {
      window.addEventListener('resize', function () { self._resize(); });
    }
    this._resize();
  };

  RouteMap.prototype._build = function (route, info) {
    var self = this;
    var runs = [];
    var stepPaths = info.groups.map(function () { return []; });
    var groupOf = [];
    var items = [];
    var ends = [];
    var run = null;

    function toPx(p) {
      var f = self.floorsById[p.floor_id];
      return [p.x / f.meters_per_pixel, p.y / f.meters_per_pixel];
    }
    function same(a, b) {
      return !!a && !!b && a[0] === b[0] && a[1] === b[1];
    }

    info.groups.forEach(function (g, k) {
      for (var s = g[0]; s <= g[1]; s += 1) { groupOf[s] = k; }
    });

    route.steps.forEach(function (step, i) {
      var own = stepPaths[groupOf[i]];
      step.points.forEach(function (p) {
        var pt = toPx(p);
        if (!run || run.floorId !== p.floor_id) { run = { floorId: p.floor_id, pts: [] }; runs.push(run); }
        if (!same(run.pts[run.pts.length - 1], pt)) { run.pts.push(pt); }
        var cur = own[own.length - 1];
        if (!cur || cur.floorId !== p.floor_id) { cur = { floorId: p.floor_id, pts: [] }; own.push(cur); }
        if (!same(cur.pts[cur.pts.length - 1], pt)) { cur.pts.push(pt); }
      });
    });

    var n = route.steps.length;
    var firstPoint = route.steps[0].points[0];
    var lastStep = route.steps[n - 1];
    var lastPoint = lastStep.points[lastStep.points.length - 1];
    var a = toPx(firstPoint);
    var z = toPx(lastPoint);
    items.push({ type: 'origin', floorId: firstPoint.floor_id, x: a[0], y: a[1], label: info.originLabel });
    items.push({ type: 'dest', floorId: lastPoint.floor_id, x: z[0], y: z[1], label: info.destLabel });

    info.groups.forEach(function (g, k) {
      var step = route.steps[g[1]];
      var end = step.points[step.points.length - 1];
      var e = toPx(end);
      ends.push({ floorId: end.floor_id, x: e[0], y: e[1] });
      if (g[1] < n - 1) {
        items.push({
          type: 'badge', step: k, floorId: end.floor_id, x: e[0], y: e[1],
          label: 'Instrução ' + (k + 1) + ': ' + (info.texts[k] || '')
        });
        var next = route.steps[g[1] + 1];
        if (next.changes_floor) {
          var target = next.points[next.points.length - 1].floor_id;
          items.push({
            type: 'link', floorId: end.floor_id, x: e[0], y: e[1], toFloor: target, kind: next.connection,
            up: self.floorsById[target].level > self.floorsById[end.floor_id].level,
            level: self.floorsById[target].level
          });
        }
      }
      if (step.changes_floor) {
        var from = step.points[0].floor_id;
        items.push({
          type: 'arrive', floorId: end.floor_id, x: e[0], y: e[1], backFloor: from,
          kind: step.connection, level: self.floorsById[from].level
        });
      }
    });

    this.runs = runs;
    this.stepPaths = stepPaths;
    this.items = items;
    this.stepEnds = ends;
  };

  RouteMap.prototype.setRoute = function (route, info) {
    this.route = route;
    this.selected = 0;
    this._build(route, info);
    if (this.hint) { this.hint.setAttribute('hidden', ''); }
    this.showFloor(route.steps[0].points[0].floor_id, true);
  };

  RouteMap.prototype.clearRoute = function () {
    this.route = null;
    this.runs = [];
    this.stepPaths = [];
    this.stepEnds = [];
    this.items = [];
    if (this.hint) { this.hint.removeAttribute('hidden'); }
    this.renderTabs();
    this.renderPaths();
    this.render();
  };

  RouteMap.prototype.setSelected = function (i) {
    this.selected = i;
    var end = this.stepEnds[i];
    if (end) {
      if (end.floorId !== this.floorId) {
        this.showFloor(end.floorId, true);
        return;
      }
      this._reveal(end.x, end.y);
    }
    this.renderPaths();
    this.render();
  };

  RouteMap.prototype._reveal = function (x, y) {
    var v = this.view;
    var mx = v.w * 0.12;
    var my = v.h * 0.12;
    if (x < v.x + mx || x > v.x + v.w - mx || y < v.y + my || y > v.y + v.h - my) {
      this.view = { x: x - v.w / 2, y: y - v.h / 2, w: v.w, h: v.h };
      this._clamp();
    }
  };

  RouteMap.prototype.setMaintenance = function (places) {
    var self = this;
    this.maint = places.map(function (p) {
      var f = self.floorsById[p.floor_id];
      return { floorId: p.floor_id, x: p.x / f.meters_per_pixel, y: p.y / f.meters_per_pixel, label: p.label };
    });
    this.render();
  };

  RouteMap.prototype.focusPlace = function (place) {
    var f = this.floorsById[place.floor_id];
    if (!f) { return; }
    this.showFloor(place.floor_id, false);
    var w = Math.min(this.view.w, 900);
    this.view = {
      x: place.x / f.meters_per_pixel - w / 2,
      y: place.y / f.meters_per_pixel - (w * this.size.h / this.size.w) / 2,
      w: w,
      h: w * this.size.h / this.size.w
    };
    this._clamp();
    this.render();
  };

  RouteMap.prototype.renderTabs = function () {
    var self = this;
    var touched = {};
    this.runs.forEach(function (r) { touched[r.floorId] = true; });
    this.tabs.innerHTML = this.floors.map(function (f) {
      return '<button type="button" class="tab" data-floor="' + f.id + '" aria-pressed="' + (f.id === self.floorId) + '">' +
        'Andar ' + esc(f.level) + (touched[f.id] ? '<span class="dot" title="A rota passa por este andar"></span>' : '') + '</button>';
    }).join('');
  };

  RouteMap.prototype.renderPaths = function () {
    if (!this.pathsEl) { return; }
    var floorId = this.floorId;
    var html = '';
    function line(pts, cls) {
      return '<polyline class="' + cls + '" vector-effect="non-scaling-stroke" points="' +
        pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ') + '"/>';
    }
    this.runs.forEach(function (run) {
      if (run.floorId === floorId && run.pts.length > 1) { html += line(run.pts, 'casing') + line(run.pts, 'route'); }
    });
    (this.stepPaths[this.selected] || []).forEach(function (run) {
      if (run.floorId === floorId && run.pts.length > 1) { html += line(run.pts, 'sel-casing') + line(run.pts, 'sel'); }
    });
    this.pathsEl.innerHTML = html;
  };

  RouteMap.prototype.render = function () {
    var v = this.view;
    this.svg.setAttribute('viewBox', v.x + ' ' + v.y + ' ' + v.w + ' ' + v.h);
    this._renderOverlay();
    this._renderScale();
  };

  RouteMap.prototype._renderOverlay = function () {
    var f = this.floor();
    if (!f || !this.size.w) { this.overlay.innerHTML = ''; return; }
    var self = this;
    var v = this.view;
    var k = this.size.w / v.w;
    var floorId = f.id;
    var html = '';
    function X(x) { return ((x - v.x) * k).toFixed(1); }
    function Y(y) { return ((y - v.y) * k).toFixed(1); }
    function chip(it, text, gap, dy, fallbackDy) {
      var width = text.length * 7.6 + 26;
      var sx = (it.x - v.x) * k;
      if (sx + gap + width <= self.size.w - 8) { return 'transform:translate(' + gap + 'px,' + dy + ')'; }
      if (sx - gap - width >= 8) { return 'transform:translate(calc(-100% - ' + gap + 'px),' + dy + ')'; }
      var dx = clamp(sx, width / 2 + 8, self.size.w - width / 2 - 8) - sx;
      return 'transform:translate(calc(-50% + ' + dx.toFixed(0) + 'px),' + fallbackDy + ')';
    }
    function pill(it, halfWidth) {
      var sx = (it.x - v.x) * k;
      var sy = (it.y - v.y) * k;
      var dx = clamp(sx, halfWidth + 8, self.size.w - halfWidth - 8) - sx;
      return 'transform:translate(calc(-50% + ' + dx.toFixed(0) + 'px),' + (sy < 90 ? '26px' : 'calc(-100% - 26px)') + ')';
    }

    this.runs.forEach(function (run) {
      if (run.floorId !== floorId) { return; }
      for (var i = 1; i < run.pts.length; i += 1) {
        var a = run.pts[i - 1];
        var b = run.pts[i];
        if (Math.hypot(b[0] - a[0], b[1] - a[1]) * k < 90) { continue; }
        var angle = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;
        html += '<span class="mk chev" style="left:' + X((a[0] + b[0]) / 2) + 'px;top:' + Y((a[1] + b[1]) / 2) +
          'px;transform:translate(-50%,-50%) rotate(' + angle.toFixed(0) + 'deg)">' + CHEVRON + '</span>';
      }
    });

    this.maint.forEach(function (m) {
      if (m.floorId !== floorId) { return; }
      html += '<span class="mk maint" title="' + esc(m.label) + '" style="left:' + X(m.x) + 'px;top:' + Y(m.y) + 'px">' + ICONS.wrench + '</span>';
    });

    this.items.forEach(function (it) {
      if (it.floorId !== floorId) { return; }
      var left = X(it.x);
      var top = Y(it.y);
      var at = 'left:' + left + 'px;top:' + top + 'px';
      if (it.type === 'origin') {
        html += '<span class="mk dot" style="' + at + '"></span>' +
          '<span class="mk label" style="' + at + ';' + chip(it, 'Origem · ' + it.label, 18, '-50%', 'calc(-100% - 20px)') + '">Origem · ' + esc(it.label) + '</span>';
      } else if (it.type === 'dest') {
        html += '<span class="mk pin" style="' + at + '">' + PIN + '</span>' +
          '<span class="mk label" style="' + at + ';' + chip(it, 'Destino · ' + it.label, 24, '-150%', 'calc(-100% - 46px)') + '">Destino · ' + esc(it.label) + '</span>';
      } else if (it.type === 'badge') {
        html += '<button type="button" class="mk badge' + (it.step === self.selected ? ' sel' : '') + '" data-act="step" data-i="' + it.step +
          '" aria-label="' + esc(it.label) + '" style="' + at + '"><span>' + (it.step + 1) + '</span></button>';
      } else if (it.type === 'link') {
        html += '<button type="button" class="mk link" data-floor="' + it.toFloor + '" style="' + at + ';' + pill(it, 125) + '">' +
          (ICONS[it.kind] || ICONS.stairs) + (it.up ? 'Subir' : 'Descer') + ' para o andar ' + esc(it.level) + ICONS.next + '</button>';
      } else if (it.type === 'arrive') {
        html += '<button type="button" class="mk link arrive" data-floor="' + it.backFloor + '" style="' + at + ';' + pill(it, 140) + '">' +
          ICONS.prev + 'Você saiu ' + (CONNECTION_NAME[it.kind] || 'da escada') + ' · voltar ao andar ' + esc(it.level) + '</button>';
      }
    });
    this.overlay.innerHTML = html;
  };

  RouteMap.prototype._renderScale = function () {
    var f = this.floor();
    if (!f || !this.scaleBox || !this.size.w) { return; }
    var metersPerScreenPx = f.meters_per_pixel * this.view.w / this.size.w;
    var length = NICE[NICE.length - 1];
    for (var i = 0; i < NICE.length; i += 1) {
      if (NICE[i] / metersPerScreenPx >= 70) { length = NICE[i]; break; }
    }
    this.scaleBox.innerHTML = '<span>' + length + ' m</span><i style="width:' + Math.round(length / metersPerScreenPx) + 'px"></i>';
  };

  window.RouteMap = RouteMap;
}());
