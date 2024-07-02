const fsapi = {};
fsapi.left = $('#left_container');
fsapi.right = $('#right_container');
fsapi.loading = $('#loading');
fsapi.progress = (_min, _max, _now, _text, _show, _cycle) => {
  const prog_elem = $('.progress');
  const bar_elem = prog_elem.find('.progress-bar');
  const bar_text = bar_elem.find('.progress-bar-text');
  if(_show) prog_elem.removeClass('d-none');
  else prog_elem.addClass('d-none');
  prog_elem.attr('aria-valuemin', _min);
  prog_elem.attr('aria-valuemax', _max);
  prog_elem.attr('aria-valuenow', _now);
  if (!_cycle) {
    const par = Math.floor((_now / (_max-_min)) * 10000) / 100
    bar_elem.css('left', 'auto').css('width', `${par}%`);
    bar_text.text(`${par.toFixed(2)}% ( ${_now} / ${_max} ) ${_text}`);
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
    bar_text.text('Server processing...');
    var progress_handle = setTimeout(() => {
      if (!fsapi.loading.is('.d-none')) fsapi.progress(_min, _max, _now, _text, _show, _cycle);
    }, 20);
  }
};
fsapi.filer = (svpath, is_local) => {
  // ファイルアップロード ========================================================
  const upload = async (event) => {
    show_loading();
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
    const drop_path = event.originalEvent.dataTransfer.getData('path');
    const formData = new FormData();
    if (drop_path) {
      const relative = async (formData, entry, path) => {
        if (entry.kind === 'file') {
          const f = await entry.getFile();
          let p = path + '/' + entry.name;
          p = p.replace("\\","/").replace("//","/");
          formData.append('files', f, p);
        }
        else if (entry.kind === 'directory') {
          for await (const ent of entry.values()) {
            let p = path + '/' + entry.name;
            p = p.replace("\\","/").replace("//","/");
            await relative(formData, ent, p);
          }
        }
      };
      await relative(formData, fsapi.handles[drop_path], "/");
    } else {
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
      Object.keys(files).map((key) => {
        formData.append('files', files[key], files[key].webkitRelativePath);
      });
    }
    svpath = fsapi.right.find('.filer_address').val();
    // https://developer.mozilla.org/ja/docs/Web/API/fetch
    param = {method: 'POST', body: formData};
    opt = fsapi.get_server_opt();
    $.ajax({ // fetchだとxhr.upload.onprogressが使えないため、$.ajaxを使用
      url: `filer/upload?host=${encodeURI(opt['host'])}&port=${encodeURI(opt['port'])}&password=${encodeURI(opt['password'])}&svname=${encodeURI(opt['svname'])}&svpath=${encodeURI(svpath)}&local_data=${encodeURI(opt['local_data'])}`,
      type: 'POST',
      processData: false,
      contentType: false,
      async: true,
      data: formData,
      xhr: function() {
        const xhr = $.ajaxSettings.xhr();
        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            fsapi.progress(0, e.total, e.loaded, '', true, e.total==e.loaded);
          }
        };
        return xhr;
      },
      success: function(data) {
        //fsapi.message(data);
        fsapi.tree(fsapi.right, svpath, fsapi.right.find('.tree-menu'), false);
      },
      error: function(data) {
        console.log(data);
        fsapi.message(data);
        fsapi.tree(fsapi.right, svpath, fsapi.right.find('.tree-menu'), false);
      }
    });
  }
  // ファイルダウンロード ==============================================================
  const download = (event) => {
    if (!fsapi.left.find('.filer_address').val()) {
      fsapi.message({warn: 'Please select a local directory before downloading.'});
      return;
    }
    show_loading();
    const formData = new FormData();
    formData.append('current_path', event.originalEvent.dataTransfer.getData('path'));
    fetch('gui/list_downloads', {method: 'POST', body: formData}).then(async res => {
      const list_downloads = await res.json();
      const jobs = [];
      fsapi.download_now = 0;
      fsapi.progress(0, list_downloads.length, fsapi.download_now, '', true, false)
      list_downloads.forEach(async path => {
        opt['mode'] = 'client';
        opt['cmd'] = 'file_download';
        opt['capture_stdout'] = true;
        opt['svpath'] = path['svpath'];
        opt['rpath'] = path['rpath'];
        //opt['svpath'] = event.originalEvent.dataTransfer.getData('path');
        jobs.push(fsapi.sv_exec_cmd(opt).then(async res => {
          if(!res[0] || !res[0]['success']) {
            fsapi.download_now ++;
            fsapi.progress(0, list_downloads.length, fsapi.download_now, '', true, false)
            fsapi.message(res);
            return;
          }
          const mk_blob = (base64) => {
            const bin = atob(base64.replace(/^.*,/, ''));
            const buffer = new Uint8Array(bin.length);
            for (i=0; i<bin.length; i++) buffer[i] = bin.charCodeAt(i);
            const blob = new Blob([buffer.buffer], {type: 'application/octet-stream'});
            return blob;
          }
          const file_name = res[0]['success']['name'];
          const file_svpath = res[0]['success']['svpath'];
          const rpath = res[0]['success']['rpath'];
          let file_path = fsapi.left.find('.filer_address').val() + '/' + rpath;
          file_path = file_path.replaceAll("\\","/").replaceAll("//","/");
          fsapi.progress(0, list_downloads.length, fsapi.download_now, file_path, true, false)
          const file_path_parts = file_path.split('/');
          let dh = fsapi.handles['/'];
          for (let i=0; i<file_path_parts.length-1; i++){
            const part = file_path_parts[i];
            if (!part) continue;
            try {
              dh = await dh.getDirectoryHandle(part, {create: true});
              fsapi.handles[file_path_parts.slice(0, i+1).join('/')] = dh;
            } catch (e) {
              continue;
            }
          }
          try {
            const down_dir = fsapi.handles[file_path_parts.slice(0, -1).join('/')];
            const down_file = await down_dir.getFileHandle(file_name, {create: true});
            const writable = await down_file.createWritable();
            const blob = mk_blob(res[0]['success']['data']);
            await writable.write(blob);
            await writable.close();
          } catch (e) {
            console.log(e);
          }
          fsapi.download_now ++;
          fsapi.progress(0, list_downloads.length, fsapi.download_now, file_path, true, false)
        }).catch((e) => {
          console.log(e);
        }));
      });
      Promise.all(jobs).then(() => {
        hide_loading();
        fsapi.progress(0, list_downloads.length, fsapi.download_now, '', false, false)
        fsapi.download_now = 0;
        fsapi.tree(fsapi.left, fsapi.left.find('.filer_address').val(), fsapi.left.find('.tree-menu'), true);
      });
    });
  };
  // 表示 ==============================================================
  const target = is_local ? fsapi.left : fsapi.right;
  target.find('.filer_address').val(svpath);
  fsapi.right.find('.filer_address_bot').off('click').on('click', ()=>{
    fsapi.tree(fsapi.right, fsapi.right.find('.filer_address').val(), fsapi.right.find('.tree-menu'), false);
  })
  fsapi.right.find('.drop-area').off('dragover').on('dragover', (event) => {
    fsapi.right.find('.drop-area').addClass('dragover');
    event.preventDefault();
  });
  fsapi.right.find('.drop-area').off('dragleave').on('dragleave', (event) => {
    fsapi.right.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  fsapi.right.find('.drop-area').off('drop').on('drop', (event) => {
    if (fsapi.right.find('.drop-area').hasClass('dragover')) {
      fsapi.right.find('.drop-area').removeClass('dragover');
      const from = event.originalEvent.dataTransfer.getData('from');
      if (from=="local") {
          upload(event);
      }
    }
    event.preventDefault();
  });

  fsapi.left.find('.drop-area').off('dragover').on('dragover', (event) => {
    fsapi.left.find('.drop-area').addClass('dragover');
    event.preventDefault();
  });
  fsapi.left.find('.drop-area').off('dragleave').on('dragleave', (event) => {
    fsapi.left.find('.drop-area').removeClass('dragover');
    event.preventDefault();
  });
  fsapi.left.find('.drop-area').off('drop').on('drop', (event) => {
    if (fsapi.left.find('.drop-area').hasClass('dragover')) {
      fsapi.left.find('.drop-area').removeClass('dragover');
      const from = event.originalEvent.dataTransfer.getData('from');
      if (from=="server") {
        console.log(event);
        download(event);
      }
    }
    event.preventDefault();
  });

  if (is_local) {
    fsapi.tree(fsapi.left, "/", fsapi.left.find('.tree-menu'), true);
  } else {
    fsapi.load_server_list();
  }
  fsapi.left.find('.filer_local_bot').off('click').on('click', (event) => {
    fsapi.opendir();
  });
}
// 接続情報一覧を取得 ========================================================
fsapi.get_server_opt = () => {
  const filer_host = fsapi.right.find('.filer_host').val();
  const filer_port = fsapi.right.find('.filer_port').val();
  const filer_password = fsapi.right.find('.filer_password').val();
  const filer_svname = fsapi.right.find('.filer_svname').val();
  const filer_local_data = fsapi.right.find('.filer_local_data').val();

  return {"host":filer_host, "port":filer_port, "password":filer_password, "svname":filer_svname, "local_data": filer_local_data};
}
// サーバーリスト取得 ================================================================
fsapi.load_server_list = () => {
  show_loading();
  fsapi.right.find('.filer_svnames').remove();
  const mk_func = (elem) => {return ()=>{
    fsapi.right.find('.filer_server_bot').text(elem.attr('data-svname'));
    fsapi.right.find('.filer_host').val(elem.attr('data-host'));
    fsapi.right.find('.filer_port').val(elem.attr('data-port'));
    fsapi.right.find('.filer_password').val(elem.attr('data-password'));
    fsapi.right.find('.filer_svname').val(elem.attr('data-svname'));
    fsapi.right.find('.filer_local_data').val(elem.attr('data-local_data'));
    fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
  }};
  if (!fsapi.initargs['client_only']) {
    const opt = fsapi.get_server_opt();
    opt['mode'] = 'server';
    opt['cmd'] = 'list';
    opt["capture_stdout"] = true;
    delete opt['svname'];
    fsapi.sv_exec_cmd(opt).then(res => {
      if(!res[0] || !res[0]['success']) {
        fsapi.message(res);
        return;
      }
      if(res.length<=0 || !res[0]['success']) {
        hide_loading();
        return;
      }
      res[0]['success'].forEach(elem => {
        const a_elem = $(`<a class="dropdown-item" href="#" data-local_data="">${elem['svname']} ( ${opt['host']}:${opt['port']} )</a>`);
        a_elem.attr('data-host', opt['host']);
        a_elem.attr('data-port', opt['port']);
        a_elem.attr('data-password', opt['password']);
        a_elem.attr('data-svname', elem['svname']);
        a_elem.off("click").on("click", mk_func(a_elem));
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        fsapi.right.find('.filer_server').append(li_elem);
      });
      fsapi.right.find('.filer_server').find('.dropdown-item:first').click();
    }).catch((e) => {
      console.log(e);
    }).finally(() => {
      hide_loading();
    });
  }
  const cl = () => {
    const a_elem = $(`<a class="dropdown-item" href="#">client</a>`);
    a_elem.attr('data-host', fsapi.initargs['host']);
    a_elem.attr('data-port', fsapi.initargs['port']);
    a_elem.attr('data-password', fsapi.initargs['password']);
    a_elem.attr('data-svname', 'client');
    a_elem.attr('data-local_data', fsapi.initargs['data']);
    a_elem.off("click").on("click", mk_func(a_elem));
    const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
    fsapi.right.find('.filer_server').append(li_elem);
    fsapi.right.find('.filer_server').find('.dropdown-item:first').click();
  }
  cl();
}
// ファイルサイズ表記 ================================================================
fsapi.calc_size = (size) => {
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
fsapi.tree = (target, svpath, current_ul_elem, is_local) => {
  show_loading();
  opt = fsapi.get_server_opt();
  opt['mode'] = 'client';
  opt['cmd'] = 'file_list';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  const exec_cmd = is_local ? fsapi.local_exec_cmd : fsapi.sv_exec_cmd;
  exec_cmd(opt).then(res => {
    current_ul_elem.html('');
    if(!res[0] || !res[0]['success']) {
      fsapi.message(res);
      target.find('.file-list').html('');
      return;
    }
    const list_tree = Object.entries(res[0]['success']).sort();
    hide_loading();
    // 上側ペイン
    list_tree.forEach(([key, node]) => {
      if(!node['is_dir']) return;
      const children = node['children'];
      let current_li_elem = target.find(`#${key}`);
      if (current_li_elem.length > 0) {
        current_li_elem.find('.folder-close').remove();
      } else {
        current_li_elem = $(`<li id="${key}" data_path="${node['path']}"/>`);
        current_ul_elem.append(current_li_elem);
      }
      const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
      const current_a_elem = $(`<a href="#" class="folder-open" style="${font_color}" draggable="false">${node['name']}</a>`);
      current_li_elem.append(current_a_elem);
      mk_func = (_t, _p, _e, _l) => {return ()=>{
        fsapi.tree(_t, _p, _e, _l);
        event.stopPropagation();
      }}
      current_a_elem.off('click').on('click', mk_func(target, node['path'], current_ul_elem, is_local));
      Object.keys(children).map((k, i) => {
        const n = children[k];
        if(!n['is_dir']) return;
        const ul_elem = $('<ul class="tree_ul"/>').append(`<li id="${k}" data_path="${n['path']}"><a href="#" class="folder-close" style="${font_color}" draggable="false">${n['name']}</a></li>`);
        current_li_elem.append(ul_elem);
        target.find(`#${k}`).off('click').on('click', mk_func(target, n['path'], current_ul_elem, is_local));
      });
    });
    // 下側ペイン
    list_tree.forEach(([key, node]) => {
      if(!node['path']) return;
      target.find('.filer_address').val(node['path']);
      const table = $('<table class="table table-bordered table-hover table-sm">'
                    + '<thead><tr><th scope="col">-</th><th scope="col">name</th><th scope="col">size</th><th scope="col">last</th></tr></thead>'
                    + '</table>');
      const table_body = $('<tbody></tbody>');
      target.find('.file-list').html('');
      target.find('.file-list').append(table);
      table.append(table_body);
      const children = node['children'];
      if(children) {
        // ツリー表示関数の生成
        const mk_tree = (_t, _p, _e, _l) => {return ()=>fsapi.tree(_t, _p, _e, _l)}
        // 削除関数の生成
        const mk_delete = (_p, _e, is_dir, _l) => {return ()=>{
          if(confirm(`Do you want to delete "${_p}"？${is_dir?"\nNote: In the case of directories, the contents will also be deleted.":""}`)) {
            const remote = is_dir ? 'file_rmdir' : 'file_remove';
            show_loading();
            const opt = fsapi.get_server_opt();
            opt['mode'] = 'client';
            opt['cmd'] = remote;
            opt['capture_stdout'] = true;
            opt['svpath'] = _p;
            const exec_cmd = _l ? fsapi.local_exec_cmd : fsapi.sv_exec_cmd;
            exec_cmd(opt).then(res => {
              if(!res[0] || !res[0]['success']) {
                fsapi.message(res);
                return;
              }
              hide_loading();
              fsapi.tree(target, res[0]['success']['path'], _e, _l);
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
          const opt = fsapi.get_server_opt();
          opt['mode'] = 'client';
          opt['cmd'] = 'file_download';
          opt['capture_stdout'] = true;
          opt['svpath'] = _p;
          fsapi.sv_exec_cmd(opt).then(res => {
            if(!res[0] || !res[0]['success']) {
              fsapi.message(res);
              return;
            }
            const blob = mk_blob(res[0]['success']['data']);
            const link = target.find('.filer_download');
            link.attr('download', res[0]['success']['name']);
            link.get(0).href = window.URL.createObjectURL(blob);
            link.get(0).click();
            URL.revokeObjectURL(link.get(0).href);
          });
        }};
        // フォルダ作成関数の生成
        mk_mkdir = (_t, _p, _e, is_dir, _l) => {return ()=>{
          _p = _p.substring(0, _p.lastIndexOf('/')+1);
          const prompt_text = prompt('Enter a new folder name.');
          if(prompt_text) {
            show_loading();
            const opt = fsapi.get_server_opt();
            opt['mode'] = 'client';
            opt['cmd'] = 'file_mkdir';
            opt['capture_stdout'] = true;
            opt['svpath'] = `${_p=="/"?"":_p}/${prompt_text}`.replace("//","/");
            const exec_cmd = _l ? fsapi.local_exec_cmd : fsapi.sv_exec_cmd;
            exec_cmd(opt).then(res => {
              if(!res[0] || !res[0]['success']) {
                fsapi.message(res);
                return;
              }
              hide_loading();
              fsapi.tree(_t, res[0]['success']['path'], _e, _l);
            });
          }
        }};
        // ファイルリストの生成
        const mk_tr = (_t, _p, _e, _n, _l) => {
          const png = _n["is_dir"] ? 'folder-close.png' : 'file.png';
          const dt = _n["is_dir"] ? '-' : new Date(_n["last"]).toLocaleDateString('ja-JP', {
            year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'
          });
          const tr = $('<tr>'
              + `<td><img src="assets/tree-menu/image/${png}"></td>`
              + '<td>'
                + '<div class="droudown">'
                  + `<a class="dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">${_n['name']}</a>`
                  + '<ul class="dropdown-menu"/>'
                + '</div>'
              + '</td>'
              + `<td class="text-end">${fsapi.calc_size(_n['size'])}</td>`
              + `<td class="text-end">${dt}</td>`
            + '</tr>');
          tr.find('.dropdown-toggle').on('dragstart', (event) => {
            event.originalEvent.dataTransfer.setData('path', _n['path']);
            event.originalEvent.dataTransfer.setData('from', _l?'local':'server');
          });
          if (_n["is_dir"]) {
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item open" href="#">Open</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
          } else {
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item mkdir" href="#">Create Folder</a></li>');
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item delete" href="#">Delete</a></li>');
            //tr.find('.dropdown-menu').append('<li><a class="dropdown-item download" href="#">Download</a></li>');
          }
          tr.find('.open').off('click').on('click', mk_tree(_t, _p, _e, _l));
          tr.find('.delete').off('click').on('click', mk_delete(_p, _e, _n["is_dir"], _l));
          tr.find('.mkdir').off('click').on('click', mk_mkdir(_t, _p, _e, _n["is_dir"], _l));
          tr.find('.download').off('click').on('click', mk_download(_p));
          return tr;
        };
        // ディレクトリを先に表示
        Object.entries(children).forEach(([k, n]) => {
          if(!n['is_dir'] || node['path']==n['path']) return;
          const tr = mk_tr(target, n['path'], current_ul_elem, n, is_local);
          table_body.append(tr);
        });
        // ファイルを表示
        Object.entries(children).forEach(([k, n]) => {
          if(n['is_dir']) return;
          const tr = mk_tr(target, n['path'], current_ul_elem, n, is_local);
          table_body.append(tr);
        });
      }
    });
  }).catch((e) => {
    console.log(e);
  }).finally(() => {
    hide_loading();
  });
}
// ローカル操作 ==============================================================
fsapi.safe_fname = (fname) => {
  return fname.replace(/[\s:\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]/g, '_');
}
fsapi.handles = {};
fsapi.file_list = async (target_path, current_path, dh) => {
  target_path = target_path.replace("\\","/").replace("//","/");
  const target_key = fsapi.safe_fname(target_path);
  current_path = current_path.replace("\\","/").replace("//","/");
  const current_key = fsapi.safe_fname(current_path);
  const path_tree = {};
  const children = {};
  for await (const entry of dh.values()) {
    let path = current_path + '/' + entry.name;
    path = path.replace("\\","/").replace("//","/");
    const key = fsapi.safe_fname(path);
    fsapi.handles[path] = entry;
    if (entry.kind === 'file') {
      const f = await entry.getFile();
      children[key] = {'name':entry.name, 'is_dir':false, 'path':path, 'size':f.size, 'last':f.lastModified, 'local':true};
    }
    else if (entry.kind === 'directory') {
      children[key] = {'name':entry.name, 'is_dir':true, 'path':path, 'size':0, 'last':'', 'local':true};
      if (target_path.indexOf(path)<0) {
        continue;
      }
      const res = await fsapi.file_list(target_path, path, entry);
      if (res && res[0] && res[0]['success']) {
        Object.keys(res[0]['success']).map((key) => {
          path_tree[key] = res[0]['success'][key];
        });
      }
    }
  }
  const current_name = current_path.split('/').pop();
  path_tree[current_key] = {'name':current_name?current_name :"/", 'is_dir':true, 'path':current_path, 'children':children, 'size':0, 'last':'', 'local':true};
  fsapi.handles[current_path] = dh;
  return [{"success": path_tree}]
}
fsapi.opendir = async () => {
  try {
    fsapi.dh = await window.showDirectoryPicker();
  } catch (e) {}
  fsapi.filer("/", true);
}
fsapi.local_exec_cmd = async (opt) => {
  if (opt['mode'] == 'client' && opt['cmd'] == 'file_list') {
    opt['svpath'] = opt['svpath'] ? opt['svpath'] : "/";
    fsapi.handles = {};
    return fsapi.file_list(opt['svpath'], "/", fsapi.dh);
  }
  else if (opt['mode'] == 'client' && opt['cmd'] == 'file_mkdir') {
    const parts = opt['svpath'].split('/');
    const dir = parts.slice(0, -1).join('/');
    const entry = fsapi.handles[dir];
    try {
      await entry.getDirectoryHandle(parts[parts.length-1], {create: true});
    } catch (e) {
      return {"warn": `Failed to create.${opt['svpath']}`};
    }
    return [{"success": {"path": dir}}];
  }
  else if (opt['mode'] == 'client' && (opt['cmd'] == 'file_remove' || opt['cmd'] == 'file_rmdir')) {
    const parts = opt['svpath'].split('/');
    const dir = parts.slice(0, -1).join('/');
    const entry = fsapi.handles[dir?dir:"/"];
    try {
      await entry.removeEntry(parts[parts.length-1], {recursive: false});
    } catch (e) {
      return {"warn": `Failed to delete.${opt['svpath']}`};
    }
    return [{"success": {"path": dir}}];
  }
  else if (opt['mode'] == 'server' && opt['cmd'] == 'list') {
    fsapi.tree(fsapi.left, "/", fsapi.left.find('.tree-menu'))
    return []
  }
  return {"warn": "Unknown command."}
};
fsapi.sv_exec_cmd = async (opt) => {
  return fetch('exec_cmd', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(opt)
  }).then(response => response.json());
};
fsapi.message = (res) => {
  msg = JSON.stringify(res)
  alert(msg.replace(/\\n/g, '\n'));
  hide_loading();
}
$(()=>{
  fetch('get_server_opt', {method: 'GET'}).then(res => res.json()).then(opt => {
    fsapi.initargs = opt;
    fsapi.right.find('.filer_host').val(fsapi.initargs['host']);
    fsapi.right.find('.filer_port').val(fsapi.initargs['port']);
    fsapi.right.find('.filer_password').val(fsapi.initargs['password']);
    fsapi.right.find('.filer_svname').val(fsapi.initargs['svname']);
    fsapi.right.find('.filer_local_data').val(fsapi.initargs['data']);
    fsapi.filer("/", false);
  });
})