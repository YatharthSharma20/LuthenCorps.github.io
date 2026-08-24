// ActualWork — Client-Side Search
// Searches a pre-built JSON index loaded inline in the search page.

(function () {
  'use strict';

  var searchInput = document.getElementById('aw-search-input');
  var resultsContainer = document.getElementById('aw-search-results');
  var searchInfo = document.getElementById('aw-search-info');

  if (!searchInput || !resultsContainer) return;

  // Search index is injected by build.py as a global variable
  var entries = window.ACTUALWORK_SEARCH_INDEX || [];

  // Filter state
  var filters = {
    occupation: '',
    industry: '',
    tool: '',
    workType: ''
  };

  // Bind filter selects
  var filterSelects = document.querySelectorAll('.filter-bar select');
  filterSelects.forEach(function (sel) {
    sel.addEventListener('change', function () {
      filters[this.getAttribute('data-filter')] = this.value;
      performSearch();
    });
  });

  searchInput.addEventListener('input', debounce(performSearch, 200));

  // Run initial search (in case of URL params or pre-filled)
  performSearch();

  function performSearch() {
    var query = searchInput.value.trim().toLowerCase();
    var terms = query.split(/\s+/).filter(function (t) { return t.length > 0; });

    var results = entries.filter(function (entry) {
      // Apply filters
      if (filters.occupation && entry.occupation !== filters.occupation) return false;
      if (filters.industry && entry.industry !== filters.industry) return false;
      if (filters.tool && entry.tools.indexOf(filters.tool) === -1) return false;
      if (filters.workType && entry.workTypes.indexOf(filters.workType) === -1) return false;

      // Apply text search
      if (terms.length === 0) return true;

      var searchable = entry.searchText;
      return terms.every(function (term) {
        return searchable.indexOf(term) !== -1;
      });
    });

    renderResults(results, terms.length > 0 || hasActiveFilter());
  }

  function hasActiveFilter() {
    return filters.occupation || filters.industry || filters.tool || filters.workType;
  }

  function renderResults(results, isFiltered) {
    if (!isFiltered) {
      resultsContainer.innerHTML = '';
      if (searchInfo) searchInfo.textContent = entries.length + ' entries available. Type to search or use filters.';
      return;
    }

    if (results.length === 0) {
      resultsContainer.innerHTML = '<p class="no-results">No entries found.</p>';
      if (searchInfo) searchInfo.textContent = '0 results.';
      return;
    }

    if (searchInfo) searchInfo.textContent = results.length + ' result' + (results.length === 1 ? '' : 's') + '.';

    var html = '<ul class="entry-list">';
    results.forEach(function (entry) {
      html += '<li class="entry-item">';
      html += '<div class="entry-title"><a href="' + escapeHtml(entry.url) + '">' + escapeHtml(entry.title) + '</a></div>';
      var metaParts = [];
      if (entry.personName) metaParts.push(escapeHtml(entry.personName));
      if (entry.occupationName) metaParts.push(escapeHtml(entry.occupationName));
      if (entry.companyName) metaParts.push(escapeHtml(entry.companyName));
      if (metaParts.length > 0) {
        html += '<div class="entry-meta">' + metaParts.map(function(p) { return '<span>' + p + '</span>'; }).join('') + '</div>';
      }
      if (entry.description) {
        var desc = entry.description;
        if (desc.length > 180) desc = desc.substring(0, 180) + '…';
        html += '<div class="entry-description">' + escapeHtml(desc) + '</div>';
      }
      html += '</li>';
    });
    html += '</ul>';

    resultsContainer.innerHTML = html;
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function debounce(fn, delay) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, delay);
    };
  }
})();
