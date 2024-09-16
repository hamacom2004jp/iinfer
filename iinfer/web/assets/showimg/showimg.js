$(() => {
  // ダークモード対応
  iinfer.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
  // copyright表示
  iinfer.copyright();
  // バージョン情報モーダル初期化
  iinfer.init_version_modal();
  // モーダルボタン初期化
  iinfer.init_modal_button();

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
