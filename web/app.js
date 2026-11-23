/* IntraMaps front end: the state, the screens and the calls to the API. */
(function () {
  'use strict';

  var TYPES = {
    'room': 'Sala',
    'washroom': 'Sanitário',
    'study-space': 'Espaço de estudo',
    'photo-spot': 'Ponto de foto',
    'cafeteria': 'Cantina',
    'building-exit': 'Saída',
    'drinking-fountain': 'Bebedouro',
    'bicycle-parking': 'Bicicletário'
  };
  var NEAREST = ['washroom', 'cafeteria', 'building-exit', 'drinking-fountain', 'bicycle-parking', 'study-space', 'photo-spot'];
  var CONNECTIONS = { corridor: 'Corredor', stairs: 'Escada', elevator: 'Elevador', ramp: 'Rampa' };
  var BY = { stairs: 'pela escada', elevator: 'pelo elevador', ramp: 'pela rampa' };
  var ACCESS = [['none', 'Sem restrição'], ['wheelchair', 'Cadeira de rodas'], ['crutches', 'Muletas']];
  var GENDERS = [['none', 'Prefiro não informar'], ['male', 'Masculino'], ['female', 'Feminino'], ['other', 'Outro']];
  var ROLES = { student: 'Aluno', faculty: 'Professor', staff: 'Funcionário (staff)' };
  var STATUS = { maintenance: 'Em manutenção', closed: 'Fechado' };

  var ICON = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#17202E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">';
  var STEP_ICONS = {
    left: ICON + '<path d="M18 20v-7a4 4 0 0 0-4-4H6"/><path d="M10 5L5 9l5 4"/></svg>',
    right: ICON + '<path d="M6 20v-7a4 4 0 0 1 4-4h8"/><path d="M14 5l5 4-5 4"/></svg>',
    straight: ICON + '<path d="M12 20V5"/><path d="M6 11l6-6 6 6"/></svg>',
    back: ICON + '<path d="M7 20V10a5 5 0 0 1 10 0v6"/><path d="M13 12l4 4 4-4"/></svg>',
    stairs: ICON + '<path d="M4 20h4v-4h4v-4h4V8h4"/></svg>',
    elevator: ICON + '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 10l3-3 3 3M9 14l3 3 3-3"/></svg>',
    flag: ICON + '<path d="M6 21V4"/><path d="M6 5h11l-2 4 2 4H6"/></svg>'
  };
  var TRASH = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg>';
  var STAR = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.5 2.9 1-6.1L3.1 9.5l6.1-.9z"/></svg>';

  var state = {
    floors: [], floorsById: {}, places: [], byId: {},
    origin: null, dest: null, route: null, texts: [], groups: [], sel: 0,
    user: null, favs: [], hist: [], showMaint: false,
    profile: { gender: 'none', accessibility: 'none' }
  };
  var map = null;
  var comboFrom = null;
  var comboTo = null;
  var accTab = 'favs';

  function $(id) { return document.getElementById(id); }

  function esc(text) {
    return String(text).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function norm(text) {
    return String(text).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  function levelOf(floorId) {
    return state.floorsById[floorId] ? state.floorsById[floorId].level : floorId;
  }

  function labelOf(p) {
    if (p.type === 'room') { return 'Sala ' + (p.number || p.name || p.id); }
    return p.name || p.number || TYPES[p.type] || p.type;
  }

  function kindOf(p) {
    return (TYPES[p.type] || p.type) + ' · Andar ' + levelOf(p.floor_id);
  }

  function initials(name) {
    return String(name).replace(/[^a-z0-9]/gi, ' ').trim().split(/\s+/).slice(0, 2).map(function (w) { return w.charAt(0); }).join('').toUpperCase() || '?';
  }

  function fmtTime(seconds) {
    var s = Math.round(seconds);
    if (s < 60) { return s + ' s'; }
    var m = Math.floor(s / 60);
    var r = s % 60;
    return r ? m + ' min ' + r + ' s' : m + ' min';
  }

  function fmtSpeed(v) {
    return String(v).replace('.', ',') + ' m/s';
  }

  function fmtDate(text) {
    var d = new Date(String(text).replace(' ', 'T') + 'Z');
    if (isNaN(d.getTime())) { return String(text); }
    var now = new Date();
    function day(x) { return x.getFullYear() * 400 + x.getMonth() * 32 + x.getDate(); }
    var hh = ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2);
    if (day(d) === day(now)) { return 'hoje, ' + hh; }
    if (day(d) === day(new Date(now.getTime() - 86400000))) { return 'ontem, ' + hh; }
    return ('0' + d.getDate()).slice(-2) + '/' + ('0' + (d.getMonth() + 1)).slice(-2) + ', ' + hh;
  }

  function showMsg(text) {
    var el = $('msg');
    el.textContent = text;
    el.hidden = false;
  }

  function hideMsg() {
    $('msg').hidden = true;
  }

  function setBusy(on) {
    document.body.classList.toggle('busy', on);
  }

  /* ---------- places and the search boxes ---------- */

  function setPlaces(list) {
    state.places = list;
    state.byId = {};
    list.forEach(function (p) {
      state.byId[p.id] = p;
      p._s = norm(labelOf(p) + ' ' + (p.number || '') + ' ' + (p.name || '') + ' ' + (TYPES[p.type] || '') + ' andar ' + levelOf(p.floor_id));
    });
  }

  function Combo(input, list, onPick) {
    var self = this;
    this.input = input;
    this.list = list;
    this.onPick = onPick;
    this.place = null;
    this.items = [];
    this.active = -1;
    input.addEventListener('input', function () {
      if (!input.value.trim() && self.place) { self.place = null; self.onPick(null); }
      self.open();
    });
    input.addEventListener('focus', function () { input.select(); self.open(); });
    input.addEventListener('keydown', function (e) { self.key(e); });
    input.addEventListener('blur', function () {
      setTimeout(function () {
        if (!self.list.hidden && self.items.length === 1 && input.value.trim()) {
          self.pick(0);
        } else {
          self.close();
          self.restore();
        }
      }, 120);
    });
    list.addEventListener('mousedown', function (e) {
      var li = e.target.closest('li[data-i]');
      if (li) { e.preventDefault(); self.pick(Number(li.getAttribute('data-i'))); }
    });
  }

  Combo.prototype.open = function () {
    var terms = norm(this.input.value).split(/\s+/).filter(Boolean);
    var first = terms.length ? terms[0] : '';
    var found = state.places.filter(function (p) {
      return terms.every(function (t) { return p._s.indexOf(t) >= 0; });
    });
    found.sort(function (a, b) {
      var sa = norm(labelOf(a)).indexOf(first) === 0 ? 0 : 1;
      var sb = norm(labelOf(b)).indexOf(first) === 0 ? 0 : 1;
      if (sa !== sb) { return sa - sb; }
      return labelOf(a).localeCompare(labelOf(b), 'pt-BR', { numeric: true });
    });
    this.items = found.slice(0, 8);
    this.active = this.items.length ? 0 : -1;
    this.draw();
  };

  Combo.prototype.draw = function () {
    var self = this;
    if (!this.items.length) {
      this.list.innerHTML = '<li class="none">Nenhum lugar encontrado</li>';
    } else {
      this.list.innerHTML = this.items.map(function (p, i) {
        return '<li role="option" id="' + self.list.id + '-' + i + '" data-i="' + i + '" aria-selected="' + (i === self.active) + '">' +
          '<span class="t">' + esc(labelOf(p)) + '</span><span class="s">' + esc(kindOf(p)) + '</span></li>';
      }).join('');
    }
    this.list.hidden = false;
    this.input.setAttribute('aria-expanded', 'true');
    if (this.active >= 0) {
      this.input.setAttribute('aria-activedescendant', this.list.id + '-' + this.active);
    } else {
      this.input.removeAttribute('aria-activedescendant');
    }
  };

  Combo.prototype.close = function () {
    this.list.hidden = true;
    this.input.setAttribute('aria-expanded', 'false');
    this.input.removeAttribute('aria-activedescendant');
  };

  Combo.prototype.key = function (e) {
    var n = this.items.length;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (this.list.hidden) { this.open(); return; }
      if (!n) { return; }
      this.active = (this.active + (e.key === 'ArrowDown' ? 1 : -1) + n) % n;
      this.draw();
    } else if (e.key === 'Enter') {
      if (!this.list.hidden && this.active >= 0) { e.preventDefault(); this.pick(this.active); }
    } else if (e.key === 'Escape') {
      this.close();
    }
  };

  Combo.prototype.pick = function (i) {
    var place = this.items[i];
    if (!place) { return; }
    this.place = place;
    this.input.value = labelOf(place);
    this.close();
    this.onPick(place);
  };

  Combo.prototype.set = function (place) {
    this.place = place;
    this.input.value = place ? labelOf(place) : '';
  };

  Combo.prototype.restore = function () {
    this.input.value = this.place ? labelOf(this.place) : '';
  };

  function renderNearest() {
    var present = {};
    state.places.forEach(function (p) { present[p.type] = true; });
    $('nearest').innerHTML = '<span class="muted">Mais próximo:</span>' + NEAREST.filter(function (t) { return present[t]; }).map(function (t) {
      return '<button type="button" class="pill" data-near="' + t + '">' + esc(TYPES[t]) + '</button>';
    }).join('');
  }

  /* ---------- profile of who is not logged in ---------- */

  function loadProfile() {
    try {
      var saved = JSON.parse(window.localStorage.getItem('intramaps.profile') || 'null');
      if (saved && saved.gender && saved.accessibility) { state.profile = saved; }
    } catch (e) { /* the page works without storage */ }
  }

  function saveProfile() {
    try { window.localStorage.setItem('intramaps.profile', JSON.stringify(state.profile)); } catch (e) { /* ignore */ }
  }

  function describeUser(u) {
    var access = ACCESS.filter(function (a) { return a[0] === u.accessibility; })[0];
    var gender = GENDERS.filter(function (g) { return g[0] === u.gender; })[0];
    return [access ? access[1] : u.accessibility, gender ? gender[1] : u.gender, fmtSpeed(u.speed)].join(' · ');
  }

  function renderProfile() {
    var el = $('profile');
    if (state.user) {
      el.innerHTML = '<p class="note">Usando o perfil de <strong>' + esc(state.user.username) + '</strong>: ' + esc(describeUser(state.user)) + '.</p>';
      return;
    }
    el.innerHTML = '<span class="eyebrow-lite">Perfil de quem não entrou na conta</span>' +
      '<div class="seg" role="group" aria-label="Acessibilidade">' + ACCESS.map(function (a) {
        return '<button type="button" data-access="' + a[0] + '" aria-pressed="' + (state.profile.accessibility === a[0]) + '">' + a[1] + '</button>';
      }).join('') + '</div>' +
      '<label class="lbl inline">Gênero<select id="sel-gender" class="inp">' + GENDERS.map(function (g) {
        return '<option value="' + g[0] + '"' + (state.profile.gender === g[0] ? ' selected' : '') + '>' + g[1] + '</option>';
      }).join('') + '</select></label>';
  }

  function profileQuery() {
    if (state.user) { return {}; }
    return {
      gender: state.profile.gender === 'none' ? undefined : state.profile.gender,
      accessibility: state.profile.accessibility === 'none' ? undefined : state.profile.accessibility
    };
  }

  /* ---------- the route ---------- */

  function iconKey(steps, i) {
    var s = steps[i];
    if (s.connection !== 'corridor') { return s.connection === 'elevator' ? 'elevator' : 'stairs'; }
    if (i === steps.length - 1) { return 'flag'; }
    var m = s.movement;
    if (m === 'up' || m === 'down') { return steps[i + 1].connection === 'elevator' ? 'elevator' : 'stairs'; }
    if (m && m.indexOf('left') >= 0) { return 'left'; }
    if (m && m.indexOf('right') >= 0) { return 'right'; }
    if (m === 'back') { return 'back'; }
    return 'straight';
  }

  /* The steps that go straight on are told together with the step after them, as the API does:
     each group is [first step, last step], and the sentences come in the same order. */
  function groupsOf(steps) {
    var groups = [];
    var first = 0;
    steps.forEach(function (s, i) {
      if (s.movement === 'straight' && s.connection === 'corridor') { return; }
      groups.push([first, i]);
      first = i + 1;
    });
    return groups;
  }

  function metaOf(group) {
    var steps = state.route.steps.slice(group[0], group[1] + 1);
    var step = steps[steps.length - 1];
    var first = steps[0].points[0].floor_id;
    var last = step.points[step.points.length - 1].floor_id;
    if (step.connection !== 'corridor') {
      return (CONNECTIONS[step.connection] || 'Passagem') + ' · andar ' + levelOf(first) +
        (step.changes_floor ? ' para o andar ' + levelOf(last) : '');
    }
    var meters = steps.reduce(function (sum, s) { return sum + s.meters; }, 0);
    return 'Andar ' + levelOf(first) + ' · ' + Math.max(1, Math.round(meters)) + ' m';
  }

  function renderSummary() {
    var r = state.route;
    var seq = [];
    r.steps.forEach(function (s) {
      s.points.forEach(function (p) { if (seq[seq.length - 1] !== p.floor_id) { seq.push(p.floor_id); } });
    });
    var parts = r.steps.filter(function (s) { return s.changes_floor; }).map(function (s) {
      var a = levelOf(s.points[0].floor_id);
      var b = levelOf(s.points[s.points.length - 1].floor_id);
      var n = Math.abs(b - a);
      return (b > a ? 'sobe ' : 'desce ') + n + (n === 1 ? ' andar ' : ' andares ') + (BY[s.connection] || '');
    });
    var arrow = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
    var box = $('summary');
    box.innerHTML = '<div><div class="time">' + esc(fmtTime(r.seconds)) + '</div>' +
      '<div class="sub">' + esc(Math.round(r.meters) + ' m · ' + (parts.length ? parts.join(' e ') : 'no mesmo andar')) + '</div></div>' +
      '<div class="floors">' + seq.map(function (id) { return '<span class="chip white">Andar ' + esc(levelOf(id)) + '</span>'; }).join(arrow) + '</div>';
    box.hidden = false;
  }

  function renderSteps() {
    var r = state.route;
    $('steps').innerHTML = state.groups.map(function (g, k) {
      return '<button type="button" class="step" data-i="' + k + '" aria-pressed="' + (k === state.sel) + '">' +
        '<span class="ico">' + STEP_ICONS[iconKey(r.steps, g[1])] + '</span>' +
        '<span class="txt"><span class="main">' + esc(state.texts[k] || '') + '</span><span class="meta">' + esc(metaOf(g)) + '</span></span>' +
        '<span class="num">' + (k + 1) + '</span></button>';
    }).join('');
    $('steps-block').hidden = false;
  }

  function updateStepButtons() {
    Array.prototype.forEach.call($('steps').children, function (el, i) {
      el.setAttribute('aria-pressed', String(i === state.sel));
      if (i === state.sel && el.scrollIntoView) { el.scrollIntoView({ block: 'nearest' }); }
    });
  }

  function selectStep(i) {
    state.sel = i;
    updateStepButtons();
    map.setSelected(i);
  }

  function applyRoute(route, instructions) {
    hideMsg();
    state.route = route;
    state.texts = instructions.map(function (i) { return i.text; });
    state.groups = groupsOf(route.steps);
    state.sel = 0;
    renderSummary();
    renderSteps();
    map.setRoute(route, { originLabel: labelOf(state.origin), destLabel: labelOf(state.dest), texts: state.texts, groups: state.groups });
    updateFav();
    try { window.history.replaceState(null, '', '#rota=' + state.origin.id + '-' + state.dest.id); } catch (e) { /* ignore */ }
  }

  function clearRoute() {
    state.route = null;
    state.texts = [];
    state.groups = [];
    $('summary').hidden = true;
    $('steps-block').hidden = true;
    map.clearRoute();
  }

  async function go() {
    if (!state.origin || !state.dest) { return; }
    if (state.origin.id === state.dest.id) {
      clearRoute();
      showMsg('A origem e o destino são o mesmo lugar.');
      return;
    }
    setBusy(true);
    try {
      var q = profileQuery();
      var route = await Api.route(state.origin.id, state.dest.id, q);
      var ins = await Api.instructions(state.origin.id, state.dest.id, q);
      applyRoute(route, ins.instructions);
    } catch (e) {
      clearRoute();
      showMsg(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function goNearest(type) {
    if (!state.origin) {
      showMsg('Escolha a origem primeiro.');
      $('in-from').focus();
      return;
    }
    setBusy(true);
    try {
      var q = profileQuery();
      var route = await Api.nearest(state.origin.id, type, q);
      var ins = await Api.nearestInstructions(state.origin.id, type, q);
      state.dest = state.byId[route.destination.id] || route.destination;
      comboTo.set(state.dest);
      applyRoute(route, ins.instructions);
    } catch (e) {
      var gender = state.user ? state.user.gender : state.profile.gender;
      if (e.status === 404 && type === 'washroom' && gender === 'none') {
        showMsg('Para achar um sanitário, escolha o gênero no perfil.');
      } else if (e.status === 404) {
        showMsg('Não encontrei ' + TYPES[type].toLowerCase() + ' que dê para alcançar a partir de ' + labelOf(state.origin) + '.');
      } else {
        showMsg(e.message);
      }
    } finally {
      setBusy(false);
    }
  }

  function picked() {
    updateFav();
    if (state.origin && state.dest) {
      go();
    } else if (state.route) {
      clearRoute();
    }
  }

  /* ---------- favorites ---------- */

  function updateFav() {
    var btn = $('btn-fav');
    btn.hidden = !(state.user && state.dest);
    var on = !!state.dest && state.favs.indexOf(state.dest.id) >= 0;
    btn.setAttribute('aria-pressed', String(on));
    btn.setAttribute('aria-label', on ? 'Remover o destino dos favoritos' : 'Favoritar o destino');
    btn.classList.toggle('on', on);
  }

  async function toggleFav() {
    if (!state.user || !state.dest) { return; }
    var id = state.dest.id;
    var on = state.favs.indexOf(id) >= 0;
    try {
      if (on) {
        await Api.removeFavorite(id);
        state.favs = state.favs.filter(function (x) { return x !== id; });
      } else {
        await Api.addFavorite(id);
        state.favs.push(id);
      }
    } catch (e) {
      showMsg(e.message);
    }
    updateFav();
  }

  async function loadFavs() {
    var raw = await Api.favorites();
    state.favs = (raw || []).map(function (x) { return x !== null && typeof x === 'object' ? x.id : x; });
  }

  /* ---------- account ---------- */

  function renderAccount() {
    var el = $('account');
    if (state.user) {
      el.innerHTML = '<button type="button" class="who-btn" id="btn-me" aria-label="Abrir minha conta"><span class="avatar">' + esc(initials(state.user.username)) +
        '</span><span class="who">' + esc(state.user.username) + '</span></button><button type="button" class="btn" id="btn-out">Sair</button>';
    } else {
      el.innerHTML = '<button type="button" class="btn" id="btn-signup">Criar conta</button><button type="button" class="btn primary" id="btn-signin">Entrar</button>';
    }
  }

  function updateMaintenance() {
    var staff = state.user && state.user.role === 'staff';
    var list = staff && state.showMaint ? state.places.filter(function (p) { return p.status !== 'ok'; }) : [];
    map.setMaintenance(list.map(function (p) {
      return { floor_id: p.floor_id, x: p.x, y: p.y, label: labelOf(p) + ' · ' + (STATUS[p.status] || p.status) };
    }));
  }

  async function afterLogin(user, rerun) {
    state.user = user;
    try { await loadFavs(); } catch (e) { state.favs = []; }
    renderAccount();
    renderProfile();
    updateFav();
    updateMaintenance();
    if (rerun && state.route) { go(); }
  }

  async function doLogout() {
    await Api.logout();
    state.user = null;
    state.favs = [];
    state.hist = [];
    state.showMaint = false;
    if ($('dlg-account').open) { $('dlg-account').close(); }
    renderAccount();
    renderProfile();
    updateFav();
    updateMaintenance();
    if (state.route) { go(); }
  }

  function openDialog(id) {
    var dlg = $(id);
    ['l-err', 'r-err'].forEach(function (e) { $(e).hidden = true; });
    if (!dlg.open) { dlg.showModal(); }
  }

  function normHistory(raw) {
    return (raw || []).map(function (h) {
      var a = h.origin ? (state.byId[h.origin.id] || h.origin) : state.byId[h.node_a_id];
      var b = h.destination ? (state.byId[h.destination.id] || h.destination) : state.byId[h.node_b_id];
      return { id: h.id, a: a, b: b, at: h.created_at };
    }).filter(function (h) { return h.a && h.b; });
  }

  function accRows(list, build) {
    return list.map(build).join('');
  }

  function accFavs() {
    var places = state.favs.map(function (id) { return state.byId[id]; }).filter(Boolean);
    if (!places.length) {
      return '<p class="note">Você ainda não favoritou nenhum lugar. Escolha um destino e toque na estrela ao lado dele.</p>';
    }
    return accRows(places, function (p) {
      return '<div class="row"><span class="grow"><b>' + esc(labelOf(p)) + '</b><small>' + esc(kindOf(p)) + '</small></span>' +
        '<button type="button" class="btn small" data-act="fav-go" data-id="' + p.id + '">Ir até aqui</button>' +
        '<button type="button" class="icon-btn on" data-act="fav-del" data-id="' + p.id + '" aria-label="Remover ' + esc(labelOf(p)) + ' dos favoritos">' + STAR + '</button></div>';
    });
  }

  function accHistory() {
    if (!state.hist.length) { return '<p class="note">Nenhuma rota no histórico ainda.</p>'; }
    return accRows(state.hist, function (h) {
      return '<div class="row"><span class="grow"><b>' + esc(labelOf(h.a)) + ' → ' + esc(labelOf(h.b)) + '</b><small>' + esc(fmtDate(h.at)) + '</small></span>' +
        '<button type="button" class="btn small" data-act="hist-open" data-id="' + h.id + '">Abrir</button>' +
        '<button type="button" class="icon-btn" data-act="hist-del" data-id="' + h.id + '" aria-label="Apagar do histórico">' + TRASH + '</button></div>';
    }) + '<button type="button" class="btn" data-act="hist-clear">Limpar histórico</button>';
  }

  function accProfile() {
    var u = state.user;
    function options(list, current) {
      return list.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === current ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('');
    }
    var roles = Object.keys(ROLES).map(function (k) { return [k, ROLES[k]]; });
    return '<form class="dlg-form flat" id="f-profile" novalidate>' +
      '<label class="lbl">Gênero<select id="p-gender" class="inp">' + options(GENDERS, u.gender) + '</select></label>' +
      '<label class="lbl">Acessibilidade<select id="p-access" class="inp">' + options(ACCESS, u.accessibility) + '</select></label>' +
      '<label class="lbl">Vínculo<select id="p-role" class="inp">' + options(roles, u.role) + '</select></label>' +
      '<label class="lbl"><span class="row-between"><span>Velocidade ao caminhar</span><output id="p-speed-out">' + esc(fmtSpeed(u.speed)) + '</output></span>' +
      '<input id="p-speed" type="range" min="0.5" max="3" step="0.1" value="' + u.speed + '"></label>' +
      '<div class="alert" id="p-err" role="alert" hidden></div><div class="alert ok" id="p-ok" role="status" hidden>Perfil salvo.</div>' +
      '<div class="row-actions"><button type="submit" class="btn primary grow">Salvar</button>' +
      '<button type="button" class="btn danger" data-act="prof-delete">Excluir conta</button></div></form>';
  }

  var maintFilter = { status: '', floor: '', text: '' };

  function maintList() {
    var text = maintFilter.text.trim().toLowerCase();
    var list = state.places.filter(function (p) {
      return p.status !== 'ok' && (!maintFilter.status || p.status === maintFilter.status) &&
        (!maintFilter.floor || String(p.floor_id) === maintFilter.floor) &&
        (!text || (labelOf(p) + ' ' + kindOf(p)).toLowerCase().indexOf(text) >= 0);
    });
    return list.length ? accRows(list, function (p) {
      return '<div class="row"><span class="grow"><b>' + esc(labelOf(p)) + '</b><small>' + esc(kindOf(p)) + ' · andar ' + esc(levelOf(p.floor_id)) + '</small></span>' +
        '<span class="status ' + esc(p.status) + '">' + esc(STATUS[p.status] || p.status) + '</span>' +
        '<button type="button" class="btn small" data-act="maint-view" data-id="' + p.id + '">Ver na planta</button></div>';
    }) : '<p class="note">Nenhum lugar encontrado com esses filtros.</p>';
  }

  function accMaint() {
    var floors = state.floors.map(function (f) {
      return '<option value="' + f.id + '"' + (maintFilter.floor === String(f.id) ? ' selected' : '') + '>Andar ' + esc(f.level) + '</option>';
    }).join('');
    function opt(v, t) { return '<option value="' + v + '"' + (maintFilter.status === v ? ' selected' : '') + '>' + t + '</option>'; }
    return '<label class="switch"><input type="checkbox" id="chk-maint"' + (state.showMaint ? ' checked' : '') + '> Mostrar na planta</label>' +
      '<div class="row-actions"><select id="m-status" aria-label="Situação">' + opt('', 'Todas as situações') + opt('maintenance', 'Em manutenção') + opt('closed', 'Fechado') + '</select>' +
      '<select id="m-floor" aria-label="Andar"><option value="">Todos os andares</option>' + floors + '</select>' +
      '<input id="m-text" type="search" placeholder="Buscar por nome ou tipo" value="' + esc(maintFilter.text) + '" class="grow"></div>' +
      '<div id="maint-list">' + maintList() + '</div>';
  }

  async function drawAccount() {
    var tabs = [['favs', 'Favoritos'], ['history', 'Histórico'], ['profile', 'Perfil']];
    if (state.user.role === 'staff') { tabs.push(['maint', 'Manutenção']); }
    $('acc-tabs').innerHTML = tabs.map(function (t) {
      return '<button type="button" role="tab" data-tab="' + t[0] + '" aria-selected="' + (t[0] === accTab ? 'true' : 'false') + '">' + t[1] + '</button>';
    }).join('');
    var body = $('acc-body');
    var tab = accTab;
    if (tab === 'favs') {
      body.innerHTML = accFavs();
    } else if (tab === 'history') {
      body.innerHTML = '<p class="note">Carregando…</p>';
      try { state.hist = normHistory(await Api.history()); } catch (e) { state.hist = []; }
      if (accTab === tab) { body.innerHTML = accHistory(); }
    } else if (tab === 'profile') {
      body.innerHTML = accProfile();
    } else if (tab === 'maint') {
      try {
        (await Api.places()).forEach(function (p) { if (state.byId[p.id]) { state.byId[p.id].status = p.status; } });
      } catch (e) { /* keep what is loaded */ }
      if (accTab === tab) { body.innerHTML = accMaint(); }
    }
  }

  function openAccount(tab) {
    if (!state.user) { return; }
    accTab = tab || 'favs';
    $('acc-name').textContent = state.user.username;
    $('acc-avatar').textContent = initials(state.user.username);
    $('acc-role').textContent = ROLES[state.user.role] || state.user.role;
    drawAccount();
    if (!$('dlg-account').open) { $('dlg-account').showModal(); }
  }

  function chooseRoute(a, b) {
    state.origin = a;
    state.dest = b;
    comboFrom.set(a);
    comboTo.set(b);
    if ($('dlg-account').open) { $('dlg-account').close(); }
    updateFav();
    go();
  }

  async function accountAction(el) {
    var act = el.getAttribute('data-act');
    var id = Number(el.getAttribute('data-id'));
    try {
      if (act === 'fav-go') {
        var place = state.byId[id];
        if (!state.origin) {
          $('dlg-account').close();
          state.dest = place;
          comboTo.set(place);
          updateFav();
          showMsg('Destino escolhido. Agora escolha a origem.');
          $('in-from').focus();
        } else {
          chooseRoute(state.origin, place);
        }
      } else if (act === 'fav-del') {
        await Api.removeFavorite(id);
        state.favs = state.favs.filter(function (x) { return x !== id; });
        updateFav();
        drawAccount();
      } else if (act === 'hist-open') {
        var h = state.hist.filter(function (x) { return x.id === id; })[0];
        if (h) { chooseRoute(h.a, h.b); }
      } else if (act === 'hist-del') {
        await Api.deleteHistory(id);
        state.hist = state.hist.filter(function (x) { return x.id !== id; });
        $('acc-body').innerHTML = accHistory();
      } else if (act === 'hist-clear') {
        if (window.confirm('Apagar todo o histórico?')) {
          await Api.clearHistory();
          state.hist = [];
          $('acc-body').innerHTML = accHistory();
        }
      } else if (act === 'maint-view') {
        $('dlg-account').close();
        map.focusPlace(state.byId[id]);
      } else if (act === 'prof-delete') {
        if (window.confirm('Excluir sua conta? Isso apaga também favoritos e histórico.')) {
          await Api.deleteMe();
          state.user = null;
          state.favs = [];
          state.hist = [];
          state.showMaint = false;
          $('dlg-account').close();
          renderAccount();
          renderProfile();
          updateFav();
          updateMaintenance();
          if (state.route) { go(); }
        }
      }
    } catch (e) {
      showMsg(e.message);
    }
  }

  /* ---------- events ---------- */

  function wire() {
    $('nearest').addEventListener('click', function (e) {
      var b = e.target.closest('[data-near]');
      if (b) { goNearest(b.getAttribute('data-near')); }
    });

    $('profile').addEventListener('click', function (e) {
      var b = e.target.closest('[data-access]');
      if (!b) { return; }
      state.profile.accessibility = b.getAttribute('data-access');
      saveProfile();
      renderProfile();
      if (state.route) { go(); }
    });
    $('profile').addEventListener('change', function (e) {
      if (e.target.id === 'sel-gender') {
        state.profile.gender = e.target.value;
        saveProfile();
        if (state.route) { go(); }
      }
    });

    $('steps').addEventListener('click', function (e) {
      var b = e.target.closest('.step');
      if (b) { selectStep(Number(b.getAttribute('data-i'))); }
    });

    $('btn-swap').addEventListener('click', function () {
      var a = state.origin;
      state.origin = state.dest;
      state.dest = a;
      comboFrom.set(state.origin);
      comboTo.set(state.dest);
      picked();
    });
    $('btn-fav').addEventListener('click', toggleFav);

    $('account').addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) { return; }
      if (b.id === 'btn-signin') { openDialog('dlg-login'); }
      if (b.id === 'btn-signup') { openDialog('dlg-register'); }
      if (b.id === 'btn-me') { openAccount('favs'); }
      if (b.id === 'btn-out') { doLogout(); }
    });

    Array.prototype.forEach.call(document.querySelectorAll('dialog'), function (dlg) {
      dlg.addEventListener('click', function (e) {
        if (e.target === dlg || e.target.closest('[data-close]')) { dlg.close(); }
      });
    });
    $('go-register').addEventListener('click', function () { $('dlg-login').close(); openDialog('dlg-register'); });
    $('go-login').addEventListener('click', function () { $('dlg-register').close(); openDialog('dlg-login'); });

    $('f-login').addEventListener('submit', async function (e) {
      e.preventDefault();
      var err = $('l-err');
      err.hidden = true;
      try {
        var res = await Api.login({ username: $('l-user').value.trim(), password: $('l-pass').value });
        $('l-pass').value = '';
        $('dlg-login').close();
        await afterLogin(res.user, true);
      } catch (ex) {
        err.textContent = ex.message;
        err.hidden = false;
      }
    });

    $('r-speed').addEventListener('input', function () { $('r-speed-out').textContent = fmtSpeed($('r-speed').value); });
    $('f-register').addEventListener('submit', async function (e) {
      e.preventDefault();
      var err = $('r-err');
      err.hidden = true;
      var username = $('r-user').value.trim();
      var password = $('r-pass').value;
      try {
        await Api.register({
          username: username, password: password, gender: $('r-gender').value, accessibility: $('r-access').value,
          role: $('r-role').value, speed: parseFloat($('r-speed').value)
        });
        var res = await Api.login({ username: username, password: password });
        $('r-pass').value = '';
        $('dlg-register').close();
        await afterLogin(res.user, true);
      } catch (ex) {
        err.textContent = ex.message;
        err.hidden = false;
      }
    });

    $('acc-tabs').addEventListener('click', function (e) {
      var b = e.target.closest('[data-tab]');
      if (b) { accTab = b.getAttribute('data-tab'); drawAccount(); }
    });
    $('acc-body').addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]');
      if (b) { accountAction(b); }
    });
    $('acc-body').addEventListener('change', function (e) {
      if (e.target.id === 'chk-maint') { state.showMaint = e.target.checked; updateMaintenance(); }
      if (e.target.id === 'm-status') { maintFilter.status = e.target.value; $('maint-list').innerHTML = maintList(); }
      if (e.target.id === 'm-floor') { maintFilter.floor = e.target.value; $('maint-list').innerHTML = maintList(); }
    });
    $('acc-body').addEventListener('input', function (e) {
      if (e.target.id === 'm-text') { maintFilter.text = e.target.value; $('maint-list').innerHTML = maintList(); }
      if (e.target.id === 'p-speed') { $('p-speed-out').textContent = fmtSpeed(e.target.value); }
    });
    $('acc-body').addEventListener('submit', async function (e) {
      if (e.target.id !== 'f-profile') { return; }
      e.preventDefault();
      $('p-err').hidden = true;
      $('p-ok').hidden = true;
      try {
        state.user = await Api.updateMe({
          gender: $('p-gender').value, accessibility: $('p-access').value, role: $('p-role').value, speed: parseFloat($('p-speed').value)
        });
        $('p-ok').hidden = false;
        renderProfile();
        $('acc-role').textContent = ROLES[state.user.role] || state.user.role;
        if (state.route) { go(); }
      } catch (ex) {
        $('p-err').textContent = ex.message;
        $('p-err').hidden = false;
      }
    });
    $('dlg-account').addEventListener('close', function () {
      if (state.user && state.user.role !== 'staff') { state.showMaint = false; updateMaintenance(); }
    });
  }

  /* ---------- start ---------- */

  async function init() {
    map = new window.RouteMap({
      root: $('map'), svg: $('map-svg'), overlay: $('overlay'), tabs: $('tabs'), scale: $('scale'), hint: $('hint'),
      onStep: selectStep,
      loadImage: Api.image,
      onError: function (e) { showMsg(e.message); }
    });
    loadProfile();
    renderAccount();
    renderProfile();
    wire();
    try {
      state.floors = await Api.floors();
      state.floors.forEach(function (f) { state.floorsById[f.id] = f; });
      setPlaces(await Api.places());
    } catch (e) {
      showMsg(e.message);
      return;
    }
    if (state.floors.length) { $('building').textContent = state.floors[0].building; }
    map.setFloors(state.floors);
    map.setPlaces(state.places);
    renderNearest();
    comboFrom = new Combo($('in-from'), $('list-from'), function (p) { state.origin = p; picked(); });
    comboTo = new Combo($('in-to'), $('list-to'), function (p) { state.dest = p; picked(); });

    if (Api.hasToken()) {
      try {
        await afterLogin(await Api.me(), false);
      } catch (e) {
        Api.setToken(null);
      }
    }

    var m = /rota=(\d+)-(\d+)/.exec(window.location.hash);
    if (m && state.byId[m[1]] && state.byId[m[2]]) { chooseRoute(state.byId[m[1]], state.byId[m[2]]); }
  }

  init();
}());
