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
    const response = await fetch('/copyright');
    const copyright = await response.text();
    $('.copyright').text(copyright);
  };
  copyright_func();
  $('.split-pane').splitPane();
  $('#versions_modal').on('shown.bs.modal	', () => {
    // iinferのバージョン情報取得
    const versions_iinfer_func = async () => {
      const response = await fetch('/versions_iinfer');
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
      const response = await fetch('/versions_used');
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

  // modal setting
  $('.modal-dialog').draggable({cursor:'move',cancel:'.modal-body'});
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
  const sub_img = () => {
    const protocol = window.location.protocol.endsWith('s') ? 'wss' : 'ws';
    const host = window.location.hostname;
    const port = window.location.port;
    const ws = new WebSocket(`${protocol}://${host}:${port}/showimg/sub_img`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const img_url = data['img_url'];
      const outputs = data['outputs'];
      const elem = $($("#img_template").html());
      if (img_url) {
        elem.find('img').attr('src', img_url);
        document.getElementById('img_container').appendChild(elem.get(0));
      }
    };
  }
  sub_img();
  /**
  eel.expose(js_console_modal_log_func);
  function js_console_modal_log_func(line) {
      const elem = $('#console_modal_log');
      if (typeof line === 'object') {
          line = JSON.stringify(line);
      }
      const text = elem.val() + line;
      elem.val(text);
      elem.get(0).setSelectionRange(text.length-1, text.length-1);
  };

  eel.expose(js_show_func);
  function js_show_func(outputs, img_url) {
      const elem = $($("#img_template").html());
      if (img_url) {
          elem.find('img').attr('src', img_url);
          document.getElementById('img_container').appendChild(elem.get(0));
      }
      if (outputs && outputs['success'] && outputs['success'].length > 0) {
      }
  };
  console.log(js_show_func);
  */
});
