const change_dark_mode = (dark_mode) => {
  const html = $('html');
  if(dark_mode) html.attr('data-bs-theme','dark');
  else if(html.attr('data-bs-theme')=='dark') html.removeAttr('data-bs-theme');
  else html.attr('data-bs-theme','dark');
}
const show_loading = () => {
  const loading = $('#loading');
  loading.removeClass('d-none');
}
const hide_loading = () => {
  const loading = $('#loading');
  loading.addClass('d-none');
  const progress = $('#progress');
  progress.addClass('d-none');
}
$(() => {
  // ダークモード対応
  change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
  // copyright情報取得
  const copyright_func = async () => {
    const response = await fetch('copyright');
    const copyright = await response.text();
    $('.copyright').text(copyright);
  };
  copyright_func();
  $('.split-pane').splitPane();
  $('#versions_modal').on('shown.bs.modal	', () => {
    // iinferのバージョン情報取得
    const versions_iinfer_func = async () => {
      const response = await fetch('versions_iinfer');
      const versions_iinfer = await response.json();
      $('#versions_iinfer').html('');
      versions_iinfer.forEach((v, i) => {
        v = v.replace(/<([^>]+)>/g, '<a href="$1" target="_blank">$1</a>');
        const div = $('<div class="d-block"></div>');
        $('#versions_iinfer').append(div);
        if(i==0) {
          div.addClass('m-3');
          div.append(`<h4>${v}</h4>`);
        } else {
          div.addClass('ms-5 me-5');
          div.append(`<h6>${v}</h6>`);
        }
      });
    };
    versions_iinfer_func();
    // usedのバージョン情報取得
    const versions_used_func = async () => {
      const response = await fetch('versions_used');
      const versions_used = await response.json();
      $('#versions_used').html('');
      const div = $('<div class="overflow-auto" style="height:calc(100vh - 260px);"></div>');
      const table = $('<table class="table table-bordered table-hover table-sm"></table>');
      const table_head = $('<thead class="table-dark bg-dark"></thead>');
      const table_body = $('<tbody></tbody>');
      table.append(table_head);
      table.append(table_body);
      div.append(table);
      $('#versions_used').append(div);
      versions_used.forEach((row, i) => {
        const tr = $('<tr></tr>');
        row.forEach((cel, j) => {
          const td = $('<td></td>').text(cel);
          tr.append(td);
        });
        if(i==0) table_head.append(tr);
        else table_body.append(tr);
      });
    };
    versions_used_func();
  })

  $('.btn_window_stack').off('click').on('click', () => {
    $('.btn_window_stack').css('margin-left', '0px').hide();
    $('.btn_window').css('margin-left', 'auto').show();
    $('.btn_window_stack').parents('.modal-dialog').removeClass('modal-fullscreen');
  });
  $('.btn_window').off('click').on('click', () => {
    $('.btn_window_stack').css('margin-left', 'auto').show();
    $('.btn_window').css('margin-left', '0px').hide();
    $('.btn_window_stack').parents('.modal-dialog').addClass('modal-fullscreen');
  });
  $('.btn_window_stack').css('margin-left', '0px').hide();
  $('.btn_window').css('margin-left', 'auto').show();

  // disable F5 and Ctrl+R
  $(document).on('keydown', (e) => {
    if ((e.which || e.keyCode) == 116) {
      return false;
    } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
      return false;
    }
  });
});
