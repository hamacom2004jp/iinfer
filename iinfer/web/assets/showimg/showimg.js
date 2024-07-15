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
  if ($('.split-pane').length > 0) {
    $('.split-pane').splitPane();
  }
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
          div.addClass('d-flex');
          div.addClass('m-3');
          div.append(`<h4><pre class="m-0">${v}</pre></h4>`);
        } else if(i==1) {
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
    const protocol = window.location.protocol.endsWith('s:') ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = window.location.port;
    const path = window.location.pathname;
    const ws = new WebSocket(`${protocol}//${host}:${port}${path}/sub_img`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const img_url = data['img_url'];
      const img_id = data['img_id'];
      const outputs_key = data['outputs_key'];
      const outputs = data['success'];
      const elem = $($("#img_template").html());
      if (img_url) {
        const img_12_elem = $('#img_container .col-12').find('img').css('height', 'calc(100vh - 300px)').attr('img_id', img_id);
        const img_elem = elem.find('img').css('height', '200px').attr('img_id', img_id);
        img_12_elem.attr('src', img_url);
        img_elem.attr('src', img_url);
        const click_func = (e) => {
          $('#img_container img').removeClass('card-selected');
          const img_e = $(e.currentTarget).addClass('card-selected');
          const img_id = img_e.attr('img_id');
          const img_12 = $('#img_container .col-12').find('img');
          if (img_12.attr('img_id') != img_id) {
            img_12.attr('src', img_e.attr('src')).attr('img_id', img_id);
          }
          $("#out_container").children('table').hide();
          $("#out_container").children(`table[img_id="${img_id}"]`).show();
        };
        img_12_elem.off('click').on('click', click_func);
        img_elem.off('click').on('click', click_func);
        $('#img_container .col-12').after(elem.get(0));
        $('#img_container .col-2:gt(5)').remove();
      }
      if (outputs) {
        const elem = $("#out_container");
        elem.children('table:visible').hide();
        elem.children('table:visible:gt(5)').remove();
        render_result_func(elem, outputs);
        const table = elem.children('table:visible');
        table.attr('img_id', img_id);
        const thead = table.children('thead')
        const tbody = table.children('tbody');
        tbody.children('tr').addClass('old');
        thead.children('th').each((i, e) => {
          const head_th = $(e);
          tbody.append(`<tr data-col="${i}"></tr>`);
          tr = tbody.children(`[data-col="${i}"]`);
          tr.append(head_th);
        });
        const filter_outputs = {};
        filter_output(outputs, outputs_key, filter_outputs);
        Object.keys(dst_outputs).forEach((key) => {
          const val = dst_outputs[key];
          if (!val) return;
          tbody.prepend(`<tr class="table_title fs-1" style="overflow-wrap:break-word;word-break:break-all;"><th colspan="2">${val}</th></tr>`);
        });  
        thead.remove();
        tbody.children('.old').each((i, e) => {
          const body_tr = $(e);
          body_tr.children('td').each((j, e) => {
            const body_td = $(e);
            const tr = tbody.children(`[data-col="${j}"]`)
            tr.append(body_td);
          });
        });
        tbody.children('.old').remove();
      }
    };
    const filter_output = (src, keys, dst) => {
      for (const key of keys) {
        if (src[key]) {
          dst[key] = src[key];
          continue;
        }
        if (typeof src !== 'object') continue;
        Object.keys(src).forEach((k) => {
          if (typeof src[k] !== 'object') return;
          filter_output(src[k], keys, dst);
        });
      }
    }
  }
  sub_img();
});
