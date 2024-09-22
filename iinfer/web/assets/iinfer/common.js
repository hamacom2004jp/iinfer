const iinfer = {}
/**
 * ダークモード切替
 * @param {bool} dark_mode 
 */
iinfer.change_dark_mode = (dark_mode) => {
  const html = $('html');
  if(dark_mode) html.attr('data-bs-theme','dark');
  else if(html.attr('data-bs-theme')=='dark') html.removeAttr('data-bs-theme');
  else html.attr('data-bs-theme','dark');
}
/**
 * ローディング表示
 */
iinfer.show_loading = () => {
  const elem = $('#loading');
  elem.removeClass('d-none');
}
/**
 * ローディング非表示
 */
iinfer.hide_loading = () => {
  const elem = $('#loading');
  elem.addClass('d-none');
  const progress = $('#progress');
  progress.addClass('d-none');
}
/**
 * テキストデータかどうか判定
 * @param {number[]} array - バイト配列
 * @returns {bool} - テキストデータかどうか
 */
iinfer.is_text = (array) => {
  const textChars = [7, 8, 9, 10, 12, 13, 27, ...iinfer.range(0x20, 0xff, 1)];
  return array.every(e => textChars.includes(e));
}
/**
 * Dateオブジェクトを日付文字列に変換
 * @param {Date} date - Dateオブジェクト
 * @returns {string} - 日付文字列
 */
iinfer.toDateStr = (date) => {
  return date.toLocaleDateString('ja-JP', {
    year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'
  });
}
/**
 * 指定された範囲の数値の配列を生成する
 * @param {number} start - 開始値
 * @param {number} stop - 終了値
 * @param {number} step - ステップ数
 * @returns {number[]} - 生成された数値の配列
 */
iinfer.range = (start, stop, step) => {
  return Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);
}
/**
 * アラートメッセージ表示
 * @param {object} res - レスポンス
 */
iinfer.message = (res) => {
  msg = JSON.stringify(res)
  alert(msg.replace(/\\n/g, '\n'));
  iinfer.hide_loading();
}
/**
 * コピーライト表示
 */
iinfer.copyright = async () => {
  const res = await fetch('copyright', {method: 'GET'});
  $('.copyright').text(await res.text());
}
/**
 * バージョンモーダルを初期化
 */
iinfer.init_version_modal = () => {
  $('#versions_modal').on('shown.bs.modal', () => {
    // iinferのバージョン情報取得
    const versions_iinfer_func = async () => {
      const res = await fetch('versions_iinfer', {method: 'GET'});
      const vi = await res.json();
      $('#versions_iinfer').html('');
      vi.forEach((v, i) => {
        v = v.replace(/<([^>]+)>/g, '<a href="$1" target="_blank">$1</a>');
        const div = $('<div></div>');
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
      const res = await fetch('versions_used', {method: 'GET'});
      const vu =  await res.json();
      $('#versions_used').html('');
      const div = $('<div class="overflow-auto" style="height:calc(100vh - 260px);"></div>');
      const table = $('<table class="table table-bordered table-hover table-sm"></table>');
      const table_head = $('<thead class="table-dark bg-dark"></thead>');
      const table_body = $('<tbody></tbody>');
      table.append(table_head);
      table.append(table_body);
      div.append(table);
      $('#versions_used').append(div);
      vu.forEach((row, i) => {
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
  });
}
/**
 * モーダルボタン初期化
 */
iinfer.init_modal_button = () => {
  // modal setting
  $('.modal-dialog').draggable({cursor:'move',cancel:'.modal-body'});
  $('#filer_modal .modal-dialog').draggable({cursor:'move',cancel:'.modal-body, .filer_address'});
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
  $('.bbforce').off('click').on('click', async () => {
    await bbforce_cmd();
    iinfer.hide_loading();
  });
  // F5 and Ctrl+R 無効化
  $(document).on('keydown', (e) => {
    if ((e.which || e.keyCode) == 116) {
      return false;
    } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
      return false;
    }
  });
}
/**
 * ファイルサイズ表記を取得する
 * @param {number} size - ファイルサイズ
 * @returns {string} - ファイルサイズ表記
 */
iinfer.calc_size = (size) => {
  const kb = 1024
  const mb = Math.pow(kb, 2)
  const gb = Math.pow(kb, 3)
  const tb = Math.pow(kb, 4)
  let target = null
  let unit = 'B'
  if (size >= tb) {
    target = tb
    unit = 'TB'
  } else if (size >= gb) {
    target = gb
    unit = 'GB'
  } else if (size >= mb) {
    target = mb
    unit = 'MB'
  } else if (size >= kb) {
    target = kb
    unit = 'KB'
  }
  const res = target !== null ? Math.floor((size / target) * 100) / 100 : size
  return `${res} ${unit}`
};
/**
 * カラーコードを取得する
 * @param {bool} color - カラーを指定。省略するとランダムなカラーコードを生成
 * @returns {string, array} - カラーコード
 **/
iinfer.randam_color = (color=undefined) => {
  if (!color) {
    color = [(~~(256 * Math.random())), (~~(256 * Math.random())), (~~(256 * Math.random()))];
  } else if (typeof color === 'string') {
    color = color.split(',').map(e => parseInt(e, 16));
  }
  code = color.map(e => ("00"+e.toString(16)).slice(-2)).join('');
  return code;
}
/**
 * ランダムな文字列を生成する
 * @param {number} length - 文字列の長さ
 * @returns {string} - ランダムな文字列
 **/
iinfer.randam_string = (length) => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  return Array.from({length: length}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}
/**
 * サーバーAPI実行
 * @param {object} opt - オプション
 * @returns {Promise} - レスポンス
 */
iinfer.sv_exec_cmd = async (opt) => {
  return fetch('exec_cmd', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(opt)
  }).then(response => response.json());
};
/**
 * 接続情報取得
 * @param {bool} do_sv_exec_cmd - iinfer.sv_exec_cmdを使用してserverモードのlistコマンドを実行する場合はtrue
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @returns {object | Promise} - 接続情報又はPromise
 */
iinfer.get_server_opt = (do_sv_exec_cmd, parent_elem) => {
  if (do_sv_exec_cmd) {
    const prom = fetch('get_server_opt', {method: 'GET'}).then(res => res.json()).then(opt => {
        iinfer.initargs = opt;
        parent_elem.find('.filer_host').val(opt['host']);
        parent_elem.find('.filer_port').val(opt['port']);
        parent_elem.find('.filer_password').val(opt['password']);
        parent_elem.find('.filer_svname').val(opt['svname']);
        parent_elem.find('.filer_local_data').val(opt['data']);
    });
    return prom;
  }
  try {
    const filer_host = parent_elem.find('.filer_host').val();
    const filer_port = parent_elem.find('.filer_port').val();
    const filer_password = parent_elem.find('.filer_password').val();
    const filer_svname = parent_elem.find('.filer_svname').val();
    const filer_local_data = parent_elem.find('.filer_local_data').val();
    return {"host":filer_host, "port":filer_port, "password":filer_password, "svname":filer_svname, "local_data": filer_local_data};
  } catch (e) {
    console.log(e);
    return {};
  }
}
/**
 * サーバーリスト取得
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @param {function} call_back_func - サーバーリストを選択した時のコールバック関数
 * @param {bool} server_only - サーバーのみ表示
 */
iinfer.load_server_list = (parent_elem, call_back_func, server_only) => {
  iinfer.show_loading();
  parent_elem.find('.filer_svnames').remove();
  const mk_func = (elem) => {return ()=>{
    parent_elem.find('.filer_server_bot').text(elem.attr('data-svname'));
    parent_elem.find('.filer_host').val(elem.attr('data-host'));
    parent_elem.find('.filer_port').val(elem.attr('data-port'));
    parent_elem.find('.filer_password').val(elem.attr('data-password'));
    parent_elem.find('.filer_svname').val(elem.attr('data-svname'));
    parent_elem.find('.filer_local_data').val(elem.attr('data-local_data'));
    if (call_back_func) call_back_func(iinfer.get_server_opt(false, parent_elem));
    //fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
  }};
  if (!iinfer.initargs['client_only']) {
    const opt = iinfer.get_server_opt(false, parent_elem);
    opt['mode'] = 'server';
    opt['cmd'] = 'list';
    opt["capture_stdout"] = true;
    delete opt['svname'];
    iinfer.sv_exec_cmd(opt).then(res => {
      if(!res[0] || !res[0]['success']) {
        iinfer.message(res);
        return;
      }
      if(res.length<=0 || !res[0]['success']) {
        iinfer.hide_loading();
        return;
      }
      const svnames = {};
      res[0]['success'].forEach(elem => {
        const svname = elem['svname'].split('-')[0];
        if (svnames[svname]) return;
        svnames[svname] = true;
        const a_elem = $(`<a class="dropdown-item" href="#" data-local_data="">${svname} ( ${opt['host']}:${opt['port']} )</a>`);
        a_elem.attr('data-host', opt['host']);
        a_elem.attr('data-port', opt['port']);
        a_elem.attr('data-password', opt['password']);
        a_elem.attr('data-svname', svname);
        a_elem.off("click").on("click", mk_func(a_elem));
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        parent_elem.find('.filer_server').append(li_elem);
      });
      parent_elem.find('.filer_server').find('.dropdown-item:first').click();
    }).catch((e) => {
      console.log(e);
    }).finally(() => {
      iinfer.hide_loading();
    });
  }
  const cl = () => {
    const a_elem = $(`<a class="dropdown-item" href="#">client</a>`);
    a_elem.attr('data-host', iinfer.initargs['host']);
    a_elem.attr('data-port', iinfer.initargs['port']);
    a_elem.attr('data-password', iinfer.initargs['password']);
    a_elem.attr('data-svname', 'client');
    a_elem.attr('data-local_data', iinfer.initargs['data']);
    a_elem.off("click").on("click", mk_func(a_elem));
    const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
    parent_elem.find('.filer_server').append(li_elem);
    parent_elem.find('.filer_server').find('.dropdown-item:first').click();
  }
  if (!server_only) cl();
}
/**
 * ファイルアップロード
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {FormData} formData - ファイルデータ
 * @param {bool} orverwrite - 上書きするかどうか
 * @param {function} progress_func - 進捗状況を表示する関数。呼出時の引数はe(イベントオブジェクト)のみ
 * @param {function} success_func - 成功時のコールバック関数。呼出時の引数はtarget, svpath, data
 * @param {function} error_func - エラー時のコールバック関数。呼出時の引数はtarget, svpath, data
 */
iinfer.file_upload = (target, svpath, formData, orverwrite=false, progress_func=undefined, success_func=undefined, error_func=undefined) => {
  param = {method: 'POST', body: formData};
  opt = iinfer.get_server_opt(false, target);
  $.ajax({ // fetchだとxhr.upload.onprogressが使えないため、$.ajaxを使用
    url: `filer/upload?host=${encodeURI(opt['host'])}&port=${encodeURI(opt['port'])}&password=${encodeURI(opt['password'])}&svname=${encodeURI(opt['svname'])}&orverwrite=${!!orverwrite}&svpath=${encodeURI(svpath)}&local_data=${encodeURI(opt['local_data'])}`,
    type: 'POST',
    processData: false,
    contentType: false,
    async: true,
    data: formData,
    xhr: function() {
      const xhr = $.ajaxSettings.xhr();
      xhr.upload.onprogress = function(e) {
        if (e.lengthComputable && progress_func) {
          progress_func(e);
        }
      };
      return xhr;
    },
    success: function(data) {
      if (success_func) {
        success_func(target, svpath, data);
      }
    },
    error: function(data) {
      console.log(data);
      iinfer.message(data);
      if (error_func) {
        error_func(target, svpath, data);
      }
    }
  });
}