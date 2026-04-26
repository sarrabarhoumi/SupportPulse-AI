(function ($) {
  $(function () {
    const previewButton = $('#preview-analysis-btn');
    if (!previewButton.length) return;
    previewButton.on('click', function () {
      const subject = $('#subject').val();
      const content = $('#content').val();
      const customerEmail = $('#customer_email').val();
      const target = $('#preview-analysis-result');
      target.html('<div class="text-muted">Analyse en cours...</div>');
      $.ajax({
        url: '/api/analyze-preview',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({subject: subject, content: content, customer_email: customerEmail}),
        success: function (data) {
          target.html(`
            <div class="row g-3">
              <div class="col-md-4"><div class="panel-card p-3"><div class="subtle">Catégorie</div><div class="fw-semibold">${data.category}</div></div></div>
              <div class="col-md-4"><div class="panel-card p-3"><div class="subtle">Priorité</div><div class="fw-semibold">${data.priority}</div></div></div>
              <div class="col-md-4"><div class="panel-card p-3"><div class="subtle">Urgence</div><div class="fw-semibold">${data.urgency}</div></div></div>
              <div class="col-12"><div class="panel-card p-3"><div class="subtle mb-1">Résumé</div><div>${data.summary}</div></div></div>
            </div>
          `);
        },
        error: function (xhr) {
          const message = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Analyse impossible.';
          target.html(`<div class="alert alert-danger">${message}</div>`);
        }
      });
    });
  });
})(jQuery);
