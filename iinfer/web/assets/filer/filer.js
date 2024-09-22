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
    iinfer.show_loading();
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
    iinfer.file_upload(fsapi.right, svpath, formData, orverwrite=false, progress_func=(e) => {
      fsapi.progress(0, e.total, e.loaded, '', true, e.total==e.loaded);
    }, success_func=(target, svpath, data) => {
      fsapi.tree(target, svpath, target.find('.tree-menu'), false);
    }, error_func=(target, svpath, data) => {
      fsapi.tree(target, svpath, target.find('.tree-menu'), false);
    });
  }
  // ファイルダウンロード ==============================================================
  const download = (event) => {
    if (!fsapi.left.find('.filer_address').val()) {
      iinfer.message({warn: 'Please select a local directory before downloading.'});
      return;
    }
    iinfer.show_loading();
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
        jobs.push(iinfer.sv_exec_cmd(opt).then(async res => {
          if(!res[0] || !res[0]['success']) {
            fsapi.download_now ++;
            fsapi.progress(0, list_downloads.length, fsapi.download_now, '', true, false)
            iinfer.message(res);
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
            const dir_path = file_path_parts.slice(0, -1).join('/');
            const down_dir = fsapi.handles[dir_path?dir_path:"/"];
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
        iinfer.hide_loading();
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
    iinfer.load_server_list(fsapi.right, (opt) => {
      fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
    });
    //fsapi.load_server_list();
  }
  fsapi.left.find('.filer_local_bot').off('click').on('click', (event) => {
    fsapi.opendir();
  });
}
// ツリー表示 ================================================================
fsapi.tree = (target, svpath, current_ul_elem, is_local) => {
  iinfer.show_loading();
  opt = iinfer.get_server_opt(false, fsapi.right);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_list';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  const exec_cmd = is_local ? fsapi.local_exec_cmd : iinfer.sv_exec_cmd;
  exec_cmd(opt).then(res => {
    current_ul_elem.html('');
    if(!res[0] || !res[0]['success']) {
      iinfer.message(res);
      target.find('.file-list').html('');
      return;
    }
    const list_tree = Object.entries(res[0]['success']).sort();
    iinfer.hide_loading();
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
                    + '<thead><tr><th scope="col">-</th><th scope="col">name</th><th scope="col">mime</th><th scope="col">size</th><th scope="col">last</th></tr></thead>'
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
            iinfer.show_loading();
            const opt = iinfer.get_server_opt(false, fsapi.right);
            opt['mode'] = 'client';
            opt['cmd'] = remote;
            opt['capture_stdout'] = true;
            opt['svpath'] = _p;
            const exec_cmd = _l ? fsapi.local_exec_cmd : iinfer.sv_exec_cmd;
            exec_cmd(opt).then(res => {
              if(!res[0] || !res[0]['success']) {
                iinfer.message(res);
                return;
              }
              iinfer.hide_loading();
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
          iinfer.show_loading();
          const opt = iinfer.get_server_opt(false, fsapi.right);
          opt['mode'] = 'client';
          opt['cmd'] = 'file_download';
          opt['capture_stdout'] = true;
          opt['svpath'] = _p;
          iinfer.sv_exec_cmd(opt).then(res => {
            if(!res[0] || !res[0]['success']) {
              iinfer.message(res);
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
            iinfer.show_loading();
            const opt = iinfer.get_server_opt(false, fsapi.right);
            opt['mode'] = 'client';
            opt['cmd'] = 'file_mkdir';
            opt['capture_stdout'] = true;
            opt['svpath'] = `${_p=="/"?"":_p}/${prompt_text}`.replace("//","/");
            const exec_cmd = _l ? fsapi.local_exec_cmd : iinfer.sv_exec_cmd;
            exec_cmd(opt).then(res => {
              if(!res[0] || !res[0]['success']) {
                iinfer.message(res);
                return;
              }
              iinfer.hide_loading();
              fsapi.tree(_t, res[0]['success']['path'], _e, _l);
            });
          }
        }};
        // ビューアー関数の生成
        mk_view = (_p, _mime, _size, _l) => {return ()=>{
          if (_size.indexOf('G') >= 0 || _size.indexOf('T') >= 0) {
            iinfer.message({warn: `The file size is too large to view. (${_size})`});
            return;
          }
          else if (_size.indexOf('M') >= 0 && parseInt(_size.replace('M','')) > 5) {
            iinfer.message({warn: `The file size is too large to view. (${_size} > 5M)`});
            return;
          }
          iinfer.show_loading();
          const opt = iinfer.get_server_opt(false, fsapi.right);
          opt['mode'] = 'client';
          opt['cmd'] = 'file_download';
          opt['capture_stdout'] = true;
          opt['svpath'] = _p;
          const exec_cmd = _l ? fsapi.local_exec_cmd : iinfer.sv_exec_cmd;
          exec_cmd(opt).then(res => {
            if(!res[0] || !res[0]['success']) {
              iinfer.message(res);
              return;
            }
            fsapi.viewer(_p, res[0]['success']['data'], _mime);
            iinfer.hide_loading();
          });
        }};
        // ファイルリストの生成
        const mk_tr = (_t, _p, _e, _n, _l) => {
          const png = _n["is_dir"] ? 'folder-close.png' : 'file.png';
          const mime = _n['mime_type'] ? _n['mime_type'] : '-';
          const dt = _n["is_dir"] ? '-' : iinfer.toDateStr(new Date(_n["last"]));
          const tr = $('<tr>'
              + `<td><img src="assets/tree-menu/image/${png}"></td>`
              + '<td>'
                + '<div class="droudown">'
                  + `<a class="dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">${_n['name']}</a>`
                  + '<ul class="dropdown-menu"/>'
                + '</div>'
              + '</td>'
              + `<td class="mime_type">${mime}</td>`
              + `<td class="file_size text-end">${iinfer.calc_size(_n['size'])}</td>`
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
            tr.find('.dropdown-menu').append('<li><a class="dropdown-item view" href="#">View</a></li>');
          }
          tr.find('.open').off('click').on('click', mk_tree(_t, _p, _e, _l));
          tr.find('.delete').off('click').on('click', mk_delete(_p, _e, _n["is_dir"], _l));
          tr.find('.mkdir').off('click').on('click', mk_mkdir(_t, _p, _e, _n["is_dir"], _l));
          tr.find('.view').off('click').on('click', mk_view(_p, tr.find('.mime_type').text(), tr.find('.file_size').text(), _l));
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
    iinfer.hide_loading();
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
      children[key] = {'name':entry.name, 'is_dir':false, 'path':path, 'mime_type':f.type, 'size':f.size, 'last':f.lastModified, 'local':true};
    }
    else if (entry.kind === 'directory') {
      children[key] = {'name':entry.name, 'is_dir':true, 'path':path, 'size':0, 'last':'', 'local':true};
      if (!target_path.startsWith(path)) {
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
  else if (opt['mode'] == 'client' && opt['cmd'] == 'file_download') {
    path = opt['svpath'];
    const entry = fsapi.handles[path];
    try {
      file = await entry.getFile();
      const reader = new FileReader();
      reader.readAsDataURL(file);
      return new Promise((resolve) => {
        reader.onload = () => {
          txt = reader.result.substring(reader.result.indexOf(',')+1);
          resolve([{"success": {"svpath": path, "data": txt}}]);
        };
      });
    } catch (e) {
      return {"warn": `Failed to view.${opt['svpath']}`};
    }
  }
  return {"warn": "Unknown command."}
};
fsapi.viewer = (title, data, mime) => {
  const viewer = $('#viewer_modal');
  viewer.find('.modal-title').text(title);
  const viewer_body = viewer.find('.modal-body');
  viewer_body.html('');
  if (mime.indexOf('image') >= 0) {
    const img = $('<img class="img-fluid" />');
    img.attr('src', `data:${mime};base64,${data}`);
    viewer_body.append(img);
  } else {
    cls = '';
    cls = mime == 'application/json' ? 'language-json' : cls;
    cls = mime == 'text/html' ? 'language-html' : cls;
    cls = mime == 'text/x-python' ? 'language-python' : cls;
    const pre = $(`<pre><code class="${cls}"></code></pre>`);
    viewer_body.append(pre);
    const txt = atob(data);
    const istxt = iinfer.is_text(new TextEncoder().encode(txt));
    if (istxt) {
      // 文字コード判定
      const codes = Encoding.stringToCode(txt);
      let detectedEncoding = Encoding.detect(codes);
      detectedEncoding = detectedEncoding?detectedEncoding:'SJIS'
      // 文字コード変換
      const unicodeString = Encoding.convert(codes, {
        to: 'UNICODE',
        from: detectedEncoding,
        type: 'string'
      });
      pre.find('code').text(unicodeString.replace(/\r/g, ''));
      viewer.find('.modal-title').text(`${title} ( ${detectedEncoding} -> UNICODE )`);
    } else {
      pre.find('code').text('< This file is not text or image data. >');
    }
  }
  hljs.initHighlightingOnLoad();
  viewer.modal('show');
}
fsapi.onload = () => {
  iinfer.get_server_opt(true, fsapi.right).then((opt) => {
    fsapi.filer("/", false);
  });
  hljs.addPlugin({
    'after:highlightElement': ({el, result}) => {
        el.innerHTML = result.value.replace(/^/gm,'<span class="row-number"></span>');
    }
  });
}
