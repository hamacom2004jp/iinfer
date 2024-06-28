const filer = (svpath) => {
  const modal = $('#svfiler_modal').length ? $('#svfiler_modal') : $(
    '<div id="svfiler_modal" class="modal" tabindex="-1">'
      + '<div class="modal-dialog modal-lg">'
        + '<div id="result_form" class="modal-content novalidate">'
          + '<div class="modal-header">'
            + '<div class="input-group p-1">'
              + '<button class="btn btn-outline-secondary dropdown-toggle filer_server_bot" type="button" data-bs-toggle="dropdown" aria-expanded="false">Server</button>'
              + '<ul class="dropdown-menu filer_server"><li class="mb-3 p-3">'
                + '<div class="col-12">'
                  + '<div class="input-group">'
                    + '<label class="input-group-text text-decoration-underline"><span class="text-danger">*</span>host</label>'
                    + '<input name="filer_host" type="text" class="form-control filer_host" param_data_type="str" param_data_multi="false" required>'
                  + '</div>'
                + '</div>'
                + '<div class="col-12">'
                  + '<div class="input-group">'
                    + '<label class="input-group-text text-decoration-underline"><span class="text-danger">*</span>port</label>'
                    + '<input name="filer_port" type="text" class="form-control filer_port" param_data_type="int" param_data_multi="false" required>'
                  + '</div>'
                + '</div>'
                + '<div class="col-12">'
                  + '<div class="input-group">'
                    + '<label class="input-group-text text-decoration-underline"><span class="text-danger">*</span>password</label>'
                    + '<input name="filer_password" type="text" class="form-control filer_password" param_data_type="str" param_data_multi="false" required>'
                    + '<input name="filer_svname" type="hidden" class="filer_svname">'
                    + '<input name="filer_local_data" type="hidden" class="filer_local_data">'
                  + '</div>'
                + '</div>'
              + '</li><li><hr class="dropdown-divider"></li></ul>'
              + '<input type="text" class="form-control filer_address" aria-describedby="button-addon2">'
              + '<button class="btn btn-outline-secondary filer_address_bot" type="button" id="button-addon2">'
                + '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-right-circle" viewBox="0 0 16 16">'
                  + '<path fill-rule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM4.5 7.5a.5.5 0 0 0 0 1h5.793l-2.147 2.146a.5.5 0 0 0 .708.708l3-3a.5.5 0 0 0 0-.708l-3-3a.5.5 0 1 0-.708.708L10.293 7.5H4.5z"/>'
                + '</svg>'
              + '</button>'
            + '</div>'
            + '<button type="button" class="btn btn_window_stack">'
              + '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-window-stack" viewBox="0 0 16 16">'
                + '<path d="M4.5 6a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1ZM6 6a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1Zm2-.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0Z"/>'
                + '<path d="M12 1a2 2 0 0 1 2 2 2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2 2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h10ZM2 12V5a2 2 0 0 1 2-2h9a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1Zm1-4v5a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V8H3Zm12-1V5a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v2h12Z"/>'
              + '</svg>'
            + '</button>'
            + '<button type="button" class="btn btn_window">'
                + '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-window" viewBox="0 0 16 16">'
                  + '<path d="M2.5 4a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1zm2-.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0zm1 .5a.5.5 0 1 0 0-1 .5.5 0 0 0 0 1z"/>'
                  + '<path d="M2 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2H2zm13 2v2H1V3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1zM2 14a1 1 0 0 1-1-1V6h14v7a1 1 0 0 1-1 1H2z"/>'
                + '</svg>'
            + '</button>'
            + '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" style="margin-left: 0px;"></button>'
          + '</div>'
          + '<div class="modal-body row">'
            + '<ul class="tree-menu tree_ul overflow-auto border col-4" style="height:calc(100vh - 240px)"></ul>'
            + '<div class="file-list drop-area overflow-auto col-8 p-1" style="height:calc(100vh - 240px)"></div>'
            + '<div class="progress p-0 d-none" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">'
              + '<div class="progress-bar progress-bar-striped progress-bar-animated bg-success" style="width: 0%"></div>'
            + '</div>'
            + '<a class="filer_download d-none" href="#">.</a>'
          + '</div>'
          + '<div class="modal-footer">'
            + '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
          + '</div>'
        + '</div>'
      + '</div>'
    + '</div>'
  );
  const loading = $('#loading').length ? $('#loading') : $(
    '<div id="loading" class="position-absolute top-0 start-0 w-100 h-100 d-none" style="background:rgba(0, 0, 0, 0.3);z-index:10000;">'
      + '<div class="text-center position-absolute top-50 start-50 w-100 translate-middle">'
        + '<div class="spinner-border text-light" role="status">'
          + '<span class="sr-only"></span>'
        + '</div>'
      + '</div>'
    + '</div>'
  );
  const show_loading = () => {loading.removeClass('d-none');}
  const hide_loading = () => {
    loading.addClass('d-none');
    modal.find('.progress').addClass('d-none');
  }
  const calc_size = (size) => {
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
  // ツリー表示 ================================================================
  const tree = (svpath, current_ul_elem) => {
    show_loading();
    opt = get_server_opt();
    opt['mode'] = 'client';
    opt['cmd'] = 'file_list';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    eel.exec_cmd('file_list', opt, true)().then(async res => {
      current_ul_elem.html('');
      if(res['warn']) {
        alert(res['warn']);
        hide_loading();
        return;
      }
      list_tree = res[0]['success'];
      hide_loading();
      // 左側ペイン
      Object.entries(list_tree).forEach(([key, node]) => {
        if(!node['is_dir']) return;
        children = node['children'];
        current_li_elem = modal.find(`#${key}`);
        if (current_li_elem.length > 0) {
          current_li_elem.find('.folder-close').remove();
        } else {
          current_li_elem = $(`<li id="${key}" data_path="${node['path']}"/>`);
          current_ul_elem.append(current_li_elem);
        }
        const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
        current_a_elem = $(`<a href="#" class="folder-open" style="${font_color}">${node['name']}</a>`);
        current_li_elem.append(current_a_elem);
        mk_func = (_p, _e) => {return ()=>{
          tree(_p, _e);
          event.stopPropagation();
        }}
        current_a_elem.off('click').on('click', mk_func(node['path'], current_ul_elem));
        Object.keys(children).map((k, i) => {
          n = children[k];
          if(!n['is_dir']) return;
          ul_elem = $('<ul class="tree_ul"/>').append(`<li id="${k}" data_path="${n['path']}"><a href="#" class="folder-close" style="${font_color}">${n['name']}</a></li>`);
          current_li_elem.append(ul_elem);
          modal.find(`#${k}`).off('click');
          modal.find(`#${k}`).on('click', mk_func(n['path'], current_ul_elem));
        });
      });
      // 右側ペイン
      Object.entries(list_tree).forEach(([key, node]) => {
        if(!node['path']) return;
        modal.find('.filer_address').val(node['path']);
        const table = $('<table class="table table-bordered table-hover table-sm">'
                      + '<thead><tr><th scope="col">-</th><th scope="col">name</th><th scope="col">size</th><th scope="col">last</th></tr></thead>'
                      + '</table>');
        const table_body = $('<tbody></tbody>');
        modal.find('.file-list').html('');
        modal.find('.file-list').append(table);
        table.append(table_body);
        const children = node['children'];
        if(children) {
          // ツリー表示関数の生成
          const mk_tree = (_p, _e) => {return ()=>tree(_p, _e)}
          // 削除関数の生成
          const mk_delete = (_p, _e, is_dir) => {return ()=>{
            if(confirm(`Do you want to delete "${_p}"？${is_dir?"\nNote: In the case of directories, the contents will also be deleted.":""}`)) {
              const remote = is_dir ? 'file_rmdir' : 'file_remove';
              show_loading();
              const opt = get_server_opt();
              opt['mode'] = 'client';
              opt['cmd'] = remote;
              opt['capture_stdout'] = true;
              opt['svpath'] = _p;
              eel.exec_cmd(remote, opt, true)().then(async res => {
                if(res['warn']) {
                  alert(res['warn']);
                  hide_loading();
                  return;
                }
                hide_loading();
                tree(res[0]['success']['path'], _e);
              }).then(() => {
                hide_loading();
              }, (error) => {
                console.log(error);
                hide_loading();
              });
            }
          }};
          mk_blob = (base64) => {
            const bin = atob(base64.replace(/^.*,/, ''));
            const buffer = new Uint8Array(bin.length);
            for (i=0; i<bin.length; i++) buffer[i] = bin.charCodeAt(i);
            const blob = new Blob([buffer.buffer], {type: 'application/octet-stream'});
            return blob;
          }
          // ダウンロード関数の生成
          mk_download = (_p) => {return ()=>{
            show_loading();
            const opt = get_server_opt();
            opt['mode'] = 'client';
            opt['cmd'] = 'file_download';
            opt['capture_stdout'] = true;
            opt['svpath'] = _p;
            eel.exec_cmd('file_download', opt, true)().then(async res => {
              if(res['warn']) {
                alert(res['warn']);
                hide_loading();
                return;
              }
              const blob = mk_blob(res[0]['success']['data']);
              const link = modal.find('.filer_download');
              link.attr('download', res[0]['success']['name']);
              link.get(0).href = window.URL.createObjectURL(blob);
              link.get(0).click();
              URL.revokeObjectURL(link.get(0).href);
            }).then(() => {
              hide_loading();
            }, (error) => {
              console.log(error);
              hide_loading();
            });
          }};
          // フォルダ作成関数の生成
          mk_mkdir = (_p, _e, is_dir) => {return ()=>{
            _p = _p.substring(0, _p.lastIndexOf('/')+1);
            const prompt_text = prompt('Enter a new folder name.');
            if(prompt_text) {
              show_loading();
              const opt = get_server_opt();
              opt['mode'] = 'client';
              opt['cmd'] = 'file_mkdir';
              opt['capture_stdout'] = true;
              opt['svpath'] = `${_p=="/"?"":_p}/${prompt_text}`;
              eel.exec_cmd('file_mkdir', opt, true)().then(async res => {
                if(res['warn']) {
                  alert(res['warn']);
                  hide_loading();
                  return;
                }
                hide_loading();
                tree(res[0]['success']['path'], _e);
              }).then(() => {
                hide_loading();
              }, (error) => {
                console.log(error);
                hide_loading();
              });
            }
          }};
          // ファイルリストの生成
          const mk_tr = (_p, _e, _n) => {
            const png = _n["is_dir"] ? 'folder-close.png' : 'file.png';
            const dt = _n["is_dir"] ? '-' : new Date(_n["last"]).toLocaleDateString('ja-JP', {
              year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'
            });
            const tr = $('<tr>'
                + `<td><img src="/assets/tree-menu/image/${png}"></td>`
                + '<td>'
                  + '<div class="droudown">'
                    + `<a class="dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">${_n['name']}</a>`
                    + '<ul class="dropdown-menu"/>'
                  + '</div>'
                + '</td>'
                + `<td class="text-end">${calc_size(_n['size'])}</td>`
                + `<td class="text-end">${dt}</td>`
              + '</tr>');
            if (_n["is_dir"]) {
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item open" href="#">Open</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
            } else {
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item download" href="#">Download</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
              tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
            }
            tr.find('.open').off('click').on('click', mk_tree(_p, _e));
            tr.find('.delete').off('click').on('click', mk_delete(_p, _e, _n["is_dir"]));
            tr.find('.mkdir').off('click').on('click', mk_mkdir(_p, _e, _n["is_dir"]));
            tr.find('.download').off('click').on('click', mk_download(_p));
            return tr;
          };
          // ディレクトリを先に表示
          Object.entries(children).forEach(([k, n]) => {
            if(!n['is_dir'] || node['path']==n['path']) return;
            const tr = mk_tr(n['path'], current_ul_elem, n);
            table_body.append(tr);
          });
          // ファイルを表示
          Object.entries(children).forEach(([k, n]) => {
            if(n['is_dir']) return;
            const tr = mk_tr(n['path'], current_ul_elem, n);
            table_body.append(tr);
          });
        }
      });
    }).then(() => {
      hide_loading();
    }, (error) => {
      console.log(error);
      hide_loading();
    });
  }
  // サーバー一覧を取得 ========================================================
  const get_server_opt = () => {
    let filer_host = modal.find('.filer_host').val();
    let filer_port = modal.find('.filer_port').val();
    let filer_password = modal.find('.filer_password').val();
    let filer_svname = modal.find('.filer_svname').val();
    let filer_local_data = modal.find('.filer_local_data').val();
    if (!filer_host) {
      filer_host = localStorage.getItem('filer_host');
      filer_host = filer_host ? filer_host : 'localhost';
      modal.find('.filer_host').val(filer_host);
    }
    if (!filer_port) {
      filer_port = localStorage.getItem('filer_port');
      filer_port = filer_port ? filer_port : 6379;
      modal.find('.filer_port').val(filer_port);
    }
    if (!filer_password) {
      filer_password = localStorage.getItem('filer_password');
      filer_password = filer_password ? filer_password : 'password';
      modal.find('.filer_password').val(filer_password);
    }
    if (!filer_svname) {
      filer_svname = localStorage.getItem('filer_svname');
      filer_svname = filer_svname ? filer_svname : 'server';
      modal.find('.filer_svname').val(filer_svname);
    }
    if (!filer_local_data) {
      filer_local_data = localStorage.getItem('filer_local_data');
      filer_local_data = filer_local_data ? filer_local_data : '';
      modal.find('.filer_local_data').val(filer_local_data);
    }
    return {"host":filer_host, "port":filer_port, "password":filer_password, "svname":filer_svname, "local_data": filer_local_data};
  }
  const load_server_list = () => {
    show_loading();
    modal.find('.filer_svnames').remove();
    const opt = get_server_opt();
    opt['mode'] = 'server';
    opt['cmd'] = 'list';
    opt["capture_stdout"] = true;
    delete opt['svname'];
    eel.exec_cmd("server_list", opt, true)().then(async res => {
      if(res["warn"]) {
        alert(res["warn"]);
        hide_loading();
        return;
      }
      if(res.length<=0 || !res[0]['success']) {
        hide_loading();
        return;
      }
      const mk_func = (elem) => {return ()=>{
        modal.find('.filer_server_bot').text(elem.attr('data-svname'));
        modal.find('.filer_host').val(elem.attr('data-host'));
        modal.find('.filer_port').val(elem.attr('data-port'));
        modal.find('.filer_password').val(elem.attr('data-password'));
        modal.find('.filer_svname').val(elem.attr('data-svname'));
        modal.find('.filer_local_data').val(elem.attr('data-local_data'));
        localStorage.setItem('filer_host', elem.attr('data-host'));
        localStorage.setItem('filer_port', elem.attr('data-port'));
        localStorage.setItem('filer_password', elem.attr('data-password'));
        localStorage.setItem('filer_svname', elem.attr('data-svname'));
        localStorage.setItem('filer_local_data', elem.attr('data-local_data'));
        tree("/", modal.find('.tree-menu'))
      }};
      res[0]['success'].forEach(elem => {
        const a_elem = $(`<a class="dropdown-item" href="#" data-host="${opt['host']}" data-port="${opt['port']}" data-password="${opt['password']}" data-svname="${elem['svname']}" data-local_data="">${elem['svname']} ( ${opt['host']}:${opt['port']} )</a>`);
        a_elem.off("click").on("click", mk_func(a_elem));
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        modal.find('.filer_server').append(li_elem);
      });
      const cl = async () => {
        const local_data = await get_local_data();
        const a_elem = $(`<a class="dropdown-item" href="#" data-host="localhost" data-port="6379" data-password="password" data-svname="client" data-local_data="${local_data}">client</a>`);
        a_elem.off("click").on("click", mk_func(a_elem));
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        modal.find('.filer_server').append(li_elem);
      }
      await cl();
      modal.find('.filer_server').find('.dropdown-item:first').click();
    }).then(() => {
      hide_loading();
    }, (error) => {
      console.log(error);
      hide_loading();
    });
  }
  // ファイルアップロード ========================================================
  const upload = async (event) => {
    show_loading();
    const progress = (_min, _max, _now, _text, _show, _cycle) => {
      const prog_elem = modal.find('.progress');
      const bar_elem = prog_elem.find('.progress-bar');
      if(_show) prog_elem.removeClass('d-none');
      else prog_elem.addClass('d-none');
      prog_elem.attr('aria-valuemin', _min);
      prog_elem.attr('aria-valuemax', _max);
      prog_elem.attr('aria-valuenow', _now);
      if (!_cycle) {
        const par = Math.floor((_now / (_max-_min)) * 10000) / 100
        bar_elem.css('left', 'auto').css('width', `${par}%`);
        bar_elem.text(`${par}% ( ${_now} / ${_max} ) ${_text}`);
        clearTimeout(progress_handle);
      } else {
        let maxwidth = prog_elem.css('width');
        maxwidth = parseInt(maxwidth.replace('px', ''));
        let left = bar_elem.css('left');
        if (!left || left=='auto') left = 0;
        else left = parseInt(left.replace('px', ''));
        if (left > maxwidth) left = -200;
        left += 2;
        bar_elem.css('width', '200px').css('position', 'relative').css('left', `${left}px`);
        bar_elem.text('Server processing...');
        var progress_handle = setTimeout(() => {
          if (!loading.is('.d-none')) progress(_min, _max, _now, _text, _show, _cycle);
        }, 20);
      }
    }
    // https://qiita.com/KokiSakano/items/a122bc0a1a368c697643
    const files = [];
    const searchFile = async (entry) => {
      // ファイルのwebkitRelativePathにパスを登録する
      if (entry.isFile) {
        const file = await new Promise((resolve) => {
          entry.file((file) => {
            Object.defineProperty(file, "webkitRelativePath", {
              // fullPathは/から始まるので二文字目から抜き出す
              value: entry.fullPath.slice(1),
            });
            resolve(file);
          });
        });
        files.push(file);
        // ファイルが現れるまでこちらの分岐をループし続ける
      } else if (entry.isDirectory) {
        const dirReader = entry.createReader();
        let allEntries = [];
        const getEntries = () =>
          new Promise((resolve) => {
            dirReader.readEntries((entries) => {
              resolve(entries);
            });
          });
        // readEntriesは100件ずつの取得なので、再帰で0件になるまで取ってくるようにする
        // https://developer.mozilla.org/en-US/docs/Web/API/FileSystemDirectoryReader/readEntries
        const readAllEntries = async () => {
          const entries = await getEntries();
          if (entries.length > 0) {
            allEntries = [...allEntries, ...entries];
            await readAllEntries();
          }
        };
        await readAllEntries();
        for (const entry of allEntries) {
          await searchFile(entry);
        }
      }
    };
    const items = event.originalEvent.dataTransfer.items;
    const calcFullPathPerItems = Array.from(items).map((item) => {
      return new Promise((resolve) => {
        const entry = item.webkitGetAsEntry();
        if (!entry) {
          resolve;
          return;
        }
        resolve(searchFile(entry));
      });
    });
    await Promise.all(calcFullPathPerItems);

    //const files = event.originalEvent.dataTransfer.files;
    const formData = new FormData();
    Object.keys(files).map((key) => {
      formData.append('files', files[key], files[key].webkitRelativePath);
    });
    svpath = modal.find('.filer_address').val();
    // https://developer.mozilla.org/ja/docs/Web/API/fetch
    param = {method: 'POST', body: formData};
    opt = get_server_opt();
    $.ajax({ // fetchだとxhr.upload.onprogressが使えないため、$.ajaxを使用
      url: `/filer/upload?host=${encodeURI(opt['host'])}&port=${encodeURI(opt['port'])}&password=${encodeURI(opt['password'])}&svname=${encodeURI(opt['svname'])}&svpath=${encodeURI(svpath)}`,
      type: 'POST',
      processData: false,
      contentType: false,
      async: true,
      data: formData,
      xhr: function() {
        const xhr = $.ajaxSettings.xhr();
        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            progress(0, e.total, e.loaded, '', true, e.total==e.loaded);
          }
        };
        return xhr;
      },
      success: function(data) {
        alert(data);
        tree(svpath, modal.find('.tree-menu'));
      },
      error: function(data) {
        console.log(data);
        alert(data);
        tree(svpath, modal.find('.tree-menu'));
      }
    });
  }
  // モーダル表示 ==============================================================
  modal.modal('show');
  modal.find('.btn_window_stack').click(function(){
    modal.find('.btn_window_stack').css('margin-left', '0px').hide();
    modal.find('.btn_window').css('margin-left', 'auto').show();
    modal.find('.modal-dialog').removeClass('modal-fullscreen');
  });
  modal.find('.btn_window').click(function(){
    modal.find('.btn_window_stack').css('margin-left', 'auto').show();
    modal.find('.btn_window').css('margin-left', '0px').hide();
    modal.find('.modal-dialog').addClass('modal-fullscreen');
  });
  modal.find('.btn_window_stack').css('margin-left', '0px').hide();
  modal.find('.btn_window').css('margin-left', 'auto').show();
  modal.find('.filer_address').val(svpath);
  modal.find('.filer_address_bot').click(()=>{
    tree(modal.find('.filer_address').val(), modal.find('.tree-menu'));
  })
  modal.find('.modal-dialog').draggable({cursor:"move"});
  modal.find('.drop-area').on('dragover', (event) => {
    modal.find('.drop-area').addClass('dragover');
    event.preventDefault();
  });
  modal.find('.drop-area').on('dragleave', (event) => {
    modal.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  modal.find('.drop-area').on('drop', (event) => {
    upload(event);
    modal.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  modal.find('.filer_host').on('change', (event) => {load_server_list();});
  modal.find('.filer_port').on('change', (event) => {load_server_list();});
  modal.find('.filer_password').on('change', (event) => {load_server_list();});
  
  $("body").append(loading);
  load_server_list();
}
