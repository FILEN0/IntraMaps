/* Calls to the IntraMaps API.
   The page is opened as a file, so the API has its own address: http://127.0.0.1:8000 unless the
   page is opened with ?api=http://127.0.0.1:8001 at the end of its address.
   Every request goes out in a queue, one at a time, because the API serves one request at a time. */
(function () {
  'use strict';

  var DEFAULT_ORIGIN = 'http://127.0.0.1:8000';
  var fromAddress = new URLSearchParams(window.location.search).get('api');
  var ORIGIN = (fromAddress || DEFAULT_ORIGIN).replace(/\/+$/, '');
  var BASE = ORIGIN + '/api/v1';
  var KEY = 'intramaps.token';
  var token = null;
  try { token = window.localStorage.getItem(KEY); } catch (e) { token = null; }

  function ApiError(status, message) {
    this.name = 'ApiError';
    this.status = status;
    this.message = message;
  }
  ApiError.prototype = Object.create(Error.prototype);

  function unreachable() {
    return new ApiError(0, 'Não consegui falar com a API em ' + ORIGIN + '. Ela está rodando?');
  }

  function setToken(value) {
    token = value || null;
    try {
      if (token) { window.localStorage.setItem(KEY, token); } else { window.localStorage.removeItem(KEY); }
    } catch (e) { /* the page works without storage */ }
  }

  function detailOf(data, status) {
    if (data && typeof data === 'object' && data.detail !== undefined) {
      if (typeof data.detail === 'string') { return data.detail; }
      if (Array.isArray(data.detail)) {
        return data.detail.map(function (d) {
          var where = d.loc ? d.loc.slice(1).join('.') + ': ' : '';
          return where + d.msg;
        }).join('; ');
      }
    }
    return status >= 500 ? 'Erro interno do servidor.' : 'Erro ' + status + '.';
  }

  function queryOf(query) {
    var parts = [];
    Object.keys(query || {}).forEach(function (key) {
      var value = query[key];
      if (value !== undefined && value !== null && value !== '') {
        parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
      }
    });
    return parts.length ? '?' + parts.join('&') : '';
  }

  var chain = Promise.resolve();

  function queued(task) {
    var run = chain.then(task, task);
    chain = run.then(function () {}, function () {});
    return run;
  }

  async function send(method, path, options) {
    options = options || {};
    var headers = {};
    if (token) { headers.Authorization = 'Bearer ' + token; }
    if (options.body !== undefined) { headers['Content-Type'] = 'application/json'; }
    var response;
    try {
      response = await fetch(BASE + path + queryOf(options.query), {
        method: method,
        headers: headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body)
      });
    } catch (e) {
      throw unreachable();
    }
    if (response.status === 204) { return null; }
    var text = await response.text();
    var data = null;
    try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
    if (!response.ok) { throw new ApiError(response.status, detailOf(data, response.status)); }
    return data;
  }

  function request(method, path, options) {
    return queued(function () { return send(method, path, options); });
  }

  /* The plan goes through the same queue and comes back as an address the page can show. */
  var images = {};

  function image(url) {
    if (!images[url]) {
      images[url] = queued(async function () {
        var response;
        try { response = await fetch(url, { cache: 'no-cache' }); } catch (e) { throw unreachable(); }
        if (!response.ok) { throw new ApiError(response.status, 'Não consegui carregar a planta.'); }
        return URL.createObjectURL(await response.blob());
      }).catch(function (e) {
        delete images[url];
        throw e;
      });
    }
    return images[url];
  }

  window.Api = {
    ApiError: ApiError,
    origin: ORIGIN,
    hasToken: function () { return !!token; },
    setToken: setToken,
    image: image,

    floors: function () { return request('GET', '/floors'); },
    places: function (query) { return request('GET', '/places', { query: query }); },

    route: function (from, to, profile) {
      return request('GET', '/routes/' + from + '/to/' + to, { query: profile });
    },
    instructions: function (from, to, profile) {
      return request('GET', '/routes/' + from + '/to/' + to + '/instructions', { query: profile });
    },
    nearest: function (from, type, profile) {
      return request('GET', '/routes/' + from + '/nearest/' + type, { query: profile });
    },
    nearestInstructions: function (from, type, profile) {
      return request('GET', '/routes/' + from + '/nearest/' + type + '/instructions', { query: profile });
    },

    register: function (body) { return request('POST', '/users', { body: body }); },
    login: async function (body) {
      var result = await request('POST', '/users/login', { body: body });
      setToken(result.token);
      return result;
    },
    logout: async function () {
      try { await request('POST', '/users/logout'); } catch (e) { /* the session may be gone already */ }
      setToken(null);
    },
    me: function () { return request('GET', '/users/me'); },
    updateMe: function (body) { return request('PATCH', '/users/me', { body: body }); },
    deleteMe: async function () {
      await request('DELETE', '/users/me');
      setToken(null);
    },

    favorites: function () { return request('GET', '/users/me/favorites'); },
    addFavorite: function (id) { return request('PUT', '/users/me/favorites/' + id); },
    removeFavorite: function (id) { return request('DELETE', '/users/me/favorites/' + id); },

    history: function () { return request('GET', '/users/me/history'); },
    deleteHistory: function (id) { return request('DELETE', '/users/me/history/' + id); },
    clearHistory: function () { return request('DELETE', '/users/me/history'); }
  };
}());
