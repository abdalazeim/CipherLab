(function () {
  var API = API_BASE + '/modules/cipherlab';
  var operation = 'encrypt';
  var algorithms = [];
  var settings = {
    caesar: { parameter: true, parameterLabel: 'إزاحة الأحرف', parameterValue: '3' },
    caesar_ascii: { parameter: false },
    monoalphabetic: { parameter: false },
    vigenere: { key: true, keyLabel: 'مفتاح Vigenere' },
    rail_fence: { parameter: true, parameterLabel: 'عمق المسار', parameterValue: '3' },
    playfair: { key: true, keyLabel: 'مفتاح Playfair' },
    hill: { key: true, keyLabel: 'مصفوفة Hill (أحرف مربعة)' },
    atbash: { parameter: false },
    rot13: { parameter: false },
    vernam: { key: true, keyLabel: 'نص المفتاح المتساوي الطول' },
    vernam_random: { parameter: false },
    otp_binary: { parameter: false },
    des: { key: true, keyLabel: 'مفتاح DES (8 أحرف أو 16 خانة hex)' },
    rsa: { key: true, keyLabel: 'معاملات RSA: e=... أو d=..., n=...' },
    dsa: { key: true, keyLabel: 'مفتاح DER بصيغة Base64', parameter: true, parameterLabel: 'التوقيع Base64 (للتحقق فقط)' },
    xor_shares: { parameter: true, parameterLabel: 'عدد الحصص', parameterValue: '2' }
  };

  function el(id) { return document.getElementById('cipherlab-' + id); }
  function activeAlgorithm() { return el('algorithm').value; }

  function updateControls() {
    var config = settings[activeAlgorithm()] || {};
    var keyWrap = el('key-wrap');
    var parameterWrap = el('parameter-wrap');
    keyWrap.hidden = !config.key;
    parameterWrap.hidden = !config.parameter;
    el('key-label').textContent = config.keyLabel || 'المفتاح';
    el('parameter-label').textContent = config.parameterLabel || 'المعامل';
    if (config.parameterValue) el('parameter').value = config.parameterValue;
    el('parameter').placeholder = activeAlgorithm() === 'dsa' && operation === 'encrypt' ? 'يُترك فارغاً عند إنشاء التوقيع' : '';
    el('parameter').disabled = activeAlgorithm() === 'dsa' && operation === 'encrypt';
    document.querySelector('[data-cipher-operation="encrypt"]').textContent = activeAlgorithm() === 'dsa' ? 'إنشاء توقيع' : 'تشفير';
    document.querySelector('[data-cipher-operation="decrypt"]').textContent = activeAlgorithm() === 'dsa' ? 'التحقق' : 'فك التشفير';
    var decryptButton = document.querySelector('[data-cipher-operation="decrypt"]');
    var unsupportedDecrypt = activeAlgorithm() === 'vernam_random';
    decryptButton.disabled = unsupportedDecrypt;
    if (unsupportedDecrypt && operation === 'decrypt') setOperation('encrypt');
  }

  function setOperation(value) {
    operation = value;
    document.querySelectorAll('[data-cipher-operation]').forEach(function (button) {
      button.classList.toggle('active', button.dataset.cipherOperation === value);
    });
    updateControls();
  }

  function formatError(error) {
    try {
      var payload = JSON.parse(error.message);
      return payload.message || payload.error || error.message;
    } catch (ignore) {
      return error.message || 'تعذر تنفيذ العملية';
    }
  }

  async function loadAlgorithms() {
    var response = await apiFetchJSON(API + '/algorithms/');
    algorithms = (response.data || []).slice();
    el('algorithm').innerHTML = algorithms.map(function (item) {
      return '<option value="' + escapeHtml(item.id) + '">' + escapeHtml(item.name) + '</option>';
    }).join('');
    updateControls();
  }

  async function loadHistory() {
    var body = el('history');
    if (!body) return;
    try {
      var response = await apiFetchJSON(API + '/history/');
      var items = response.data || [];
      body.innerHTML = items.length ? items.map(function (item) {
        var date = new Date(item.created_at).toLocaleString();
        var label = item.operation === 'encrypt' ? 'تشفير' : 'فك';
        return '<tr><td>' + escapeHtml(item.algorithm) + '</td><td>' + label + '</td><td>' + escapeHtml(date) + '</td></tr>';
      }).join('') : '<tr><td colspan="3">لا توجد عمليات بعد</td></tr>';
    } catch (error) {
      body.innerHTML = '<tr><td colspan="3">تعذر تحميل السجل</td></tr>';
    }
  }

  async function run() {
    var button = el('run');
    var status = el('status');
    button.disabled = true;
    status.textContent = 'جارٍ التنفيذ';
    try {
      var response = await apiFetchJSON(API + '/operate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          algorithm: activeAlgorithm(),
          operation: operation,
          text: el('input').value,
          key: el('key').value,
          parameter: el('parameter').value
        })
      });
      var result = response.data.result;
      el('output').value = typeof result === 'string' ? result : JSON.stringify(result, null, 2);
      status.textContent = response.message || 'اكتملت العملية';
      loadHistory();
    } catch (error) {
      status.textContent = formatError(error);
    } finally {
      button.disabled = false;
    }
  }

  function clear() {
    el('input').value = '';
    el('output').value = '';
    el('key').value = '';
    el('status').textContent = '';
    el('input').focus();
  }

  async function copyResult() {
    try {
      await navigator.clipboard.writeText(el('output').value);
      el('status').textContent = 'تم نسخ النتيجة';
    } catch (error) {
      el('output').select();
      document.execCommand('copy');
      el('status').textContent = 'تم نسخ النتيجة';
    }
  }

  window.cipherLab = { setOperation: setOperation, run: run, clear: clear, copyResult: copyResult, loadHistory: loadHistory };
  el('algorithm').addEventListener('change', updateControls);
  window['moduleInit_cipherlab'] = function () {
    if (!algorithms.length) loadAlgorithms().catch(function (error) { el('status').textContent = formatError(error); });
    loadHistory();
  };
})();