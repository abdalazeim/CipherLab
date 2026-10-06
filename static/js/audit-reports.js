// ============================================================
//  AUDIT REPORTS (سجل التدقيق)
//  Generic system audit-log reports (domain-agnostic).
// ============================================================
var auditReports = (function () {
  var _currentPage = 1;
  var _pageSize = 25;
  var _totalPages = 1;
  var _allRows = [];
  var _summary = { actions: [], modules: [] };

  var ACTION_LABELS = {
    create: 'إنشاء',
    update: 'تحديث',
    delete: 'حذف',
    login: 'دخول',
    logout: 'خروج',
    approve: 'اعتماد',
    reject: 'رفض',
    other: 'أخرى',
  };

  var ACTION_COLORS = {
    create: '#318a7d',
    update: '#3d7f9a',
    delete: '#d95f49',
    login: '#6f8293',
    logout: '#8a9690',
    approve: '#56846b',
    reject: '#c94f4f',
    other: '#8a9690',
  };

  function init() {
    _currentPage = 1;
    _renderActionFilter();
    load();
  }

  function _renderActionFilter() {
    var sel = document.getElementById('rpt-action');
    if (!sel) return;
    var html = '<option value="">الكل</option>';
    Object.keys(ACTION_LABELS).forEach(function (k) {
      html += '<option value="' + k + '">' + ACTION_LABELS[k] + '</option>';
    });
    sel.innerHTML = html;
  }

  function load() {
    var params = new URLSearchParams();
    params.set('page', _currentPage);
    params.set('page_size', _pageSize);

    var search = (document.getElementById('rpt-search') || {}).value || '';
    if (search) params.set('search', search);

    var action = (document.getElementById('rpt-action') || {}).value || '';
    if (action) params.set('action', action);

    var dateFrom = (document.getElementById('rpt-date-from') || {}).value || '';
    if (dateFrom) params.set('date_from', dateFrom);

    var dateTo = (document.getElementById('rpt-date-to') || {}).value || '';
    if (dateTo) params.set('date_to', dateTo);

    var body = document.getElementById('reportTableBody');
    var info = document.getElementById('rpt-pagination-info');
    if (body) body.innerHTML = '<tr><td colspan="7" class="report-table-state"><i class="fas fa-spinner fa-spin"></i> جارٍ تحميل السجلات...</td></tr>';
    if (info) info.textContent = 'جارٍ تطبيق الفلاتر';

    return apiFetch(API_BASE + '/audit-logs?' + params.toString())
      .then(function (r) {
        if (r.status === 401) { window.location.href = '/login'; throw new Error('unauthorized'); }
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (d) {
        var payload = (d && d.data) || {};
        var items = payload.items || [];
        var meta = payload.meta || {};
        _allRows = items;
        _totalPages = meta.pages || 1;
        _summary = meta.summary || { actions: [], modules: [] };
        _renderStats(items.length, meta.total || 0);
        _renderBreakdowns();
        _renderTable(items);
        _renderPagination(meta);
      })
      .catch(function () {
        _allRows = [];
        _summary = { actions: [], modules: [] };
        _renderStats(0, 0);
        _renderBreakdowns();
        _renderTable([]);
        _renderPagination({ page: 1, pages: 1 });
        showToast('فشل تحميل سجل التدقيق', 'error');
      });
  }

  function _renderStats(count, total) {
    var statsEl = document.getElementById('reportStats');
    if (!statsEl) return;
    var actionTypes = (_summary.actions || []).length;
    var topAction = (_summary.actions || []).slice().sort(function (a, b) { return b.total - a.total; })[0];
    statsEl.innerHTML =
      '<article class="report-summary-card"><span class="report-summary-icon report-summary-coral"><i class="fas fa-list-check"></i></span><div><span>نتائج مطابقة</span><strong>' + Number(total).toLocaleString('ar') + '</strong><small>وفق الفلاتر الحالية</small></div></article>' +
      '<article class="report-summary-card"><span class="report-summary-icon report-summary-teal"><i class="fas fa-file-lines"></i></span><div><span>في الصفحة</span><strong>' + Number(count).toLocaleString('ar') + '</strong><small>من ' + Number(_totalPages).toLocaleString('ar') + ' صفحة</small></div></article>' +
      '<article class="report-summary-card"><span class="report-summary-icon report-summary-lime"><i class="fas fa-shapes"></i></span><div><span>أنواع الإجراءات</span><strong>' + Number(actionTypes).toLocaleString('ar') + '</strong><small>ضمن النتائج المطابقة</small></div></article>' +
      '<article class="report-summary-card"><span class="report-summary-icon report-summary-blue"><i class="fas fa-arrow-trend-up"></i></span><div><span>الأكثر تكراراً</span><strong>' + escapeHtml(topAction ? (ACTION_LABELS[topAction.action] || topAction.action) : '—') + '</strong><small>' + (topAction ? Number(topAction.total).toLocaleString('ar') + ' حدث' : 'لا توجد بيانات') + '</small></div></article>';
  }

  function _renderBreakdowns() {
    var actionsEl = document.getElementById('report-action-breakdown');
    var modulesEl = document.getElementById('report-module-breakdown');
    var actions = _summary.actions || [];
    var modules = _summary.modules || [];
    var actionTotal = actions.reduce(function (sum, item) { return sum + Number(item.total || 0); }, 0);
    if (actionsEl) {
      actionsEl.innerHTML = actionTotal ? actions.map(function (item) {
        var value = Number(item.total || 0);
        var percent = Math.round(value / actionTotal * 100);
        return '<div class="report-breakdown-item"><div class="report-breakdown-label"><span><i style="--breakdown-color:' + (ACTION_COLORS[item.action] || '#8a9690') + '"></i>' + escapeHtml(ACTION_LABELS[item.action] || item.action) + '</span><strong>' + value.toLocaleString('ar') + '</strong></div><div class="report-breakdown-track"><span style="width:' + percent + '%;--breakdown-color:' + (ACTION_COLORS[item.action] || '#8a9690') + '"></span></div></div>';
      }).join('') : '<div class="report-analysis-empty">لا توجد إجراءات مطابقة</div>';
    }
    if (modulesEl) {
      var maxModule = Math.max.apply(null, modules.map(function (item) { return Number(item.total) || 0; }).concat([1]));
      modulesEl.innerHTML = modules.length ? modules.map(function (item, index) {
        var value = Number(item.total || 0);
        var percent = Math.round(value / maxModule * 100);
        var name = item.module || 'غير محدد';
        return '<div class="report-breakdown-item"><div class="report-breakdown-label"><span class="report-module-name"><b>' + (index + 1) + '</b>' + escapeHtml(name) + '</span><strong>' + value.toLocaleString('ar') + '</strong></div><div class="report-breakdown-track"><span class="module-breakdown-bar" style="width:' + percent + '%"></span></div></div>';
      }).join('') : '<div class="report-analysis-empty">لا توجد وحدات ضمن النتائج</div>';
    }
  }

  function _actionBadge(action) {
    var label = ACTION_LABELS[action] || action;
    var color = ACTION_COLORS[action] || '#9ca3af';
    return '<span class="badge" style="background:' + color + ';color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;">' + label + '</span>';
  }

  function _renderTable(items) {
    var head = document.getElementById('reportTableHead');
    var body = document.getElementById('reportTableBody');
    var title = document.getElementById('reportTitle');
    if (title) title.innerHTML = '<i class="fas fa-history"></i> سجل التدقيق';
    if (head) {
      head.innerHTML = '<tr>' +
        '<th style="width:50px">#</th>' +
        '<th>المستخدم</th>' +
        '<th>الإجراء</th>' +
        '<th>الوحدة</th>' +
        '<th>الوصف</th>' +
        '<th>IP</th>' +
        '<th>التاريخ</th>' +
        '</tr>';
    }
    if (!body) return;
    if (items.length === 0) {
      body.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:30px;color:#9ca3af"><i class="fas fa-inbox" style="display:block;font-size:32px;margin-bottom:8px"></i>لا توجد سجلات</td></tr>';
      return;
    }
    body.innerHTML = items.map(function (e, i) {
      var offset = (_currentPage - 1) * _pageSize;
      var date = e.created_at ? new Date(e.created_at) : null;
      var dateStr = date ? date.toLocaleDateString('ar') + ' ' + date.toLocaleTimeString('ar', { hour: '2-digit', minute: '2-digit' }) : '—';
      return '<tr>' +
        '<td>' + (offset + i + 1) + '</td>' +
        '<td><strong>' + escapeHtml(e.user_name || '—') + '</strong></td>' +
        '<td>' + _actionBadge(e.action) + '</td>' +
        '<td>' + escapeHtml(e.module || '—') + '</td>' +
        '<td>' + escapeHtml(e.object_repr || '—') + '</td>' +
        '<td style="direction:ltr;font-size:12px;color:#6b7280;">' + escapeHtml(e.ip_address || '—') + '</td>' +
        '<td style="font-size:12px;color:#6b7280;">' + dateStr + '</td>' +
        '</tr>';
    }).join('');
  }

  function _renderPagination(meta) {
    var infoEl = document.getElementById('rpt-pagination-info');
    var btnsEl = document.getElementById('rpt-pagination-btns');
    if (infoEl) {
      var from = _allRows.length === 0 ? 0 : ((meta.page || 1) - 1) * (meta.page_size || _pageSize) + 1;
      var to = from === 0 ? 0 : from + _allRows.length - 1;
      infoEl.textContent = 'عرض ' + from + ' إلى ' + to + ' من ' + (meta.total || 0) + ' سجل';
    }
    if (!btnsEl) return;
    var pages = meta.pages || 1;
    var current = meta.page || 1;
    var html = '';
    html += '<button class="pagination-btn" onclick="auditReports.goTo(' + (current - 1) + ')" ' + (current <= 1 ? 'disabled' : '') + '><i class="fas fa-chevron-right"></i></button>';
    var start = Math.max(1, current - 2);
    var end = Math.min(pages, start + 4);
    start = Math.max(1, end - 4);
    for (var p = start; p <= end; p++) {
      html += '<button class="pagination-btn' + (p === current ? ' active' : '') + '" onclick="auditReports.goTo(' + p + ')">' + p + '</button>';
    }
    html += '<button class="pagination-btn" onclick="auditReports.goTo(' + (current + 1) + ')" ' + (current >= pages ? 'disabled' : '') + '><i class="fas fa-chevron-left"></i></button>';
    btnsEl.innerHTML = html;
  }

  function goTo(page) {
    if (page < 1 || page > _totalPages) return;
    _currentPage = page;
    load();
  }

  function filterLocal() {
    _currentPage = 1;
    debounce(load, 300)();
  }

  function filterChanged() {
    _currentPage = 1;
    load();
  }

  function resetFilters() {
    ['rpt-search', 'rpt-action', 'rpt-date-from', 'rpt-date-to'].forEach(function (id) {
      var field = document.getElementById(id);
      if (field) field.value = '';
    });
    _currentPage = 1;
    load();
  }

  function printReport() {
    var rows = _allRows;
    if (rows.length === 0) { showToast('لا توجد بيانات للطباعة', 'error'); return; }
    var html = '<!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>سجل التدقيق</title><style>' +
      'body{font-family:"Traditional Arabic","Arial",sans-serif;font-size:13px;direction:rtl;padding:16px}' +
      'h2{text-align:center;margin:0 0 4px}' +
      'p.meta{text-align:center;color:#555;margin:0 0 14px}' +
      'table{width:100%;border-collapse:collapse}' +
      'th,td{border:1px solid #000;padding:5px 8px;text-align:center}' +
      'th{background:#000;color:#fff}' +
      '</style></head><body>' +
      '<h2>سجل التدقيق</h2>' +
      '<p class="meta">' + new Date().toLocaleDateString('ar') + ' — ' + new Date().toLocaleTimeString('ar') + '</p>' +
      '<table><thead><tr><th>#</th><th>المستخدم</th><th>الإجراء</th><th>الوحدة</th><th>الوصف</th><th>IP</th><th>التاريخ</th></tr></thead><tbody>';
    rows.forEach(function (e, i) {
      var date = e.created_at ? new Date(e.created_at) : null;
      var dateStr = date ? date.toLocaleDateString('ar') + ' ' + date.toLocaleTimeString('ar') : '—';
      html += '<tr><td>' + (i + 1) + '</td><td>' + escapeHtml(e.user_name || '—') + '</td><td>' + escapeHtml(ACTION_LABELS[e.action] || e.action) + '</td><td>' + escapeHtml(e.module || '—') + '</td><td>' + escapeHtml(e.object_repr || '—') + '</td><td>' + escapeHtml(e.ip_address || '—') + '</td><td>' + dateStr + '</td></tr>';
    });
    html += '</tbody></table></body></html>';
    var win = window.open('', '_blank', 'width=900,height=650');
    if (!win) { showToast('الرجاء السماح بالنوافذ المنبثقة', 'error'); return; }
    win.document.write(html);
    win.document.close();
    win.print();
  }

  function _exportRows(rows) {
    if (rows.length === 0) { showToast('لا توجد بيانات للتصدير', 'error'); return; }
    var cols = ['المستخدم', 'الإجراء', 'الوحدة', 'الوصف', 'IP', 'التاريخ'];
    var lines = [cols.join(',')];
    rows.forEach(function (e) {
      var date = e.created_at ? new Date(e.created_at) : null;
      var dateStr = date ? date.toLocaleDateString('ar') + ' ' + date.toLocaleTimeString('ar') : '';
      var row = [e.user_name || '', ACTION_LABELS[e.action] || e.action, e.module || '', e.object_repr || '', e.ip_address || '', dateStr];
      lines.push(row.map(function (v) { return '"' + String(v).replace(/"/g, '""') + '"'; }).join(','));
    });
    var blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'madar-audit-report-' + new Date().toISOString().slice(0, 10) + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  }

  async function exportCSV() {
    if (!_allRows.length) { showToast('لا توجد بيانات للتصدير', 'error'); return; }
    var rows = [];
    try {
      for (var page = 1; ; page++) {
        var params = new URLSearchParams();
        params.set('page', page);
        params.set('page_size', 100);
        ['search', 'action', 'date_from', 'date_to'].forEach(function (key) {
          var field = document.getElementById('rpt-' + key.replace('_', '-'));
          if (field && field.value) params.set(key, field.value);
        });
        var response = await apiFetchJSON(API_BASE + '/audit-logs?' + params.toString());
        var pageRows = (response.data && response.data.items) || [];
        rows = rows.concat(pageRows);
        if (pageRows.length < 100) break;
      }
      _exportRows(rows);
    } catch (error) {
      showToast('تعذر تحميل جميع النتائج للتصدير', 'error');
    }
  }

  return {
    init: init,
    load: load,
    goTo: goTo,
    filterLocal: filterLocal,
    filterChanged: filterChanged,
    resetFilters: resetFilters,
    printReport: printReport,
    exportCSV: exportCSV,
  };
})();
