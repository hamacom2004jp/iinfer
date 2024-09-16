const anno = {};
anno.left_container = $('#left_container');
anno.canvas_container = $('#canvas_container');
/**
 * デプロイリストの取得
 **/
anno.deploy_list = () => {
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'deploy_list';
  opt['capture_stdout'] = true;
  iinfer.show_loading();
  // deploy_listの取得
  iinfer.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      iinfer.hide_loading();
      iinfer.message(res);
      return;
    }
    if (!res[0]['success']['data']) {
      iinfer.hide_loading();
      return
    }
    const deploy_names_elem = anno.left_container.find('.deploy_names');
    res[0]['success']['data'].forEach(data => {
      // train_datasetを持っている場合のみ表示
      if (!data['train_dataset']) return;
      deploy_names_elem.append(`<option value="/${data['name']}">${data['name']}</option>`);
    });
    deploy_names_elem.off('change').on('change', () => {
      anno.load_conf(deploy_names_elem.val());
    });
    deploy_names_elem.change();
  }).catch((e) => {
    iinfer.hide_loading();
    console.log(e);
  });
};
/**
 * conf.jsonの取得
 * @param {string} svpath 読込むフォルダのパス
 * @return {void}
 **/
anno.load_conf = (svpath) => {
  // conf.jsonの取得
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_download';
  opt['capture_stdout'] = true;
  opt['svpath'] = `${svpath}/conf.json`;
  iinfer.show_loading();
  iinfer.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      iinfer.hide_loading();
      iinfer.message(res);
      return;
    }
    if (!res[0]['success']['data']) return;
    const conf = anno.tool.conf = JSON.parse(atob(res[0]['success']['data']));
    if (conf['label_file'] && conf['deploy_dir']){
      const label_file = conf['label_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
      anno.load_label(`${svpath}${label_file}`);
    }
    if (conf['color_file'] && conf['deploy_dir']){
      const color_file = conf['color_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
      anno.load_color(`${svpath}${color_file}`);
    }
    if (conf['train_dataset'] && conf['deploy_dir']){
      const train_dataset = conf['train_dataset'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
      const current_ul_elem = anno.left_container.find('.tree-menu');
      anno.load_filelist(`${svpath}${train_dataset}`, `${svpath}${train_dataset}`, current_ul_elem);
    }
  }).catch((e) => {
    iinfer.hide_loading();
    console.log(e);
  });
};
/**
 * label.txtの読込み
 * @param {string} svpath label.txtのパス
 */
anno.load_label = (svpath) => {
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_download';
  opt['capture_stdout'] = true;
  opt['svpath'] = `${svpath}`;
  iinfer.show_loading();
  iinfer.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      iinfer.hide_loading();
      iinfer.message(res);
      return;
    }
    if (!res[0]['success']['data']) return;
    const labels = atob(res[0]['success']['data']).split(/\r?\n/);
    const set_labels = (labels) => {
      labels.forEach((label, i) => {
        const color = iinfer.randam_color();
        const li_elem = $(`<li class="dropdown-labels"></li>`);
        const a_elem = $(`<a class="dropdown-item" href="#" data-label="${label}" data-color="${color}"></a>`);
        const input_elem = $(`<input type="color" value="#${color}" style="width: 20px; height: 20px;"/>`);
        input_elem.change((event) => {
          const input_elem = $(event.currentTarget);
          const a_elem = input_elem.parent();
          input_elem.attr('value', event.currentTarget.value);
          a_elem.attr('data-color', event.currentTarget.value.slice(1));
          anno.tool.label = a_elem.attr('data-label');
          anno.tool.color = a_elem.attr('data-color');
          anno.reflesh_svg();
        });
        a_elem.append(input_elem);
        a_elem.append(`<span class="m-2">${label}</span>`);
        li_elem.append(a_elem);
        a_elem.off('click').on('click', (event) => {
          const a_elem = $(event.currentTarget);
          anno.tool.label = a_elem.attr('data-label');
          anno.tool.color = a_elem.attr('data-color');
        });
        anno.canvas_container.find('#tags_labels').append(li_elem);
      });
    }
    anno.canvas_container.find('#tags_labels').children('.dropdown-labels').remove();
    set_labels(labels);
    anno.canvas_container.find('#tags_labels').find('.input-group').off('click').on('click', (event) => {
      event.stopPropagation();
    });
  }).catch((e) => {
    iinfer.hide_loading();
    console.log(e);
  });
};
/**
 * ツールに設定されているラベルを取得
 * @return {Array} ラベルの配列
 **/
anno.get_tool_labels = () => {
  const labels = [];
  anno.canvas_container.find('#tags_labels .dropdown-item').each((i, ak) => {
    labels.push(ak.dataset['label']);
  });
  return labels;
};
/**
 * color.txtの読込み
 * @param {string} svpath color.txtのパス
 **/
anno.load_color = (svpath) => {
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_download';
  opt['capture_stdout'] = true;
  opt['svpath'] = `${svpath}`;
  iinfer.show_loading();
  iinfer.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      iinfer.hide_loading();
      iinfer.message(res);
      return;
    }
    if (!res[0]['success']['data']) return;
    const colors = atob(res[0]['success']['data']).split(/\r?\n/);
    const set_colors = (colors) => {
      const ref_elem = anno.canvas_container.find('#tags_labels');
      ref_elem.find('.dropdown-item').each((i, ak) => {
        if (colors.length <= i) return;
        let color = colors[i].split(',');
        if (color.length == 3) {
          color = color.map((c) => {
            c = parseInt(c);
            c = c < 0 ? 0 : c;
            c = c > 255 ? 255 : c;
            return c.toString(16).padStart(2, '0');
          }).join('');
        } else {
          color = iinfer.randam_color();
        }
        $(ak).attr('data-color', color).find('input').attr('value', `#${color}`);
      });
    }
    set_colors(colors);
    anno.canvas_container.find('#tags_labels .dropdown-item:first').click();
    anno.reflesh_svg();
  }).catch((e) => {
    iinfer.hide_loading();
    console.log(e);
  });
};
/**
 * ツールに設定されているカラーを取得
 * @return {Array} カラーの配列
 **/
anno.get_tool_colors = () => {
  const colors = [];
  anno.canvas_container.find('#tags_labels .dropdown-item').each((i, ak) => {
    colors.push(ak.dataset['color']);
  });
  return colors;
};
/**
 * label.txtとcolor.txtを保存
 * @param {string} svpath 保存するフォルダのパス
 */
anno.save_label_color = (svpath) => {
  const conf = anno.tool.conf;
  if (!conf['deploy_dir']) {
    iinfer.message('deploy_dir is not set');
    return;
  }
  iinfer.show_loading();
  const conf_file = `${conf['deploy_dir']}/conf.json`;
  const opt = iinfer.get_server_opt(false, anno.left_container);
  let label_file = null;
  let color_file = null;
  if (!conf['label_file']) {
    label_file = '/label.txt';
    conf['label_file'] = `${conf['deploy_dir']}${label_file}`;
  }
  else label_file = conf['label_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
  if (!conf['color_file']) {
    color_file = '/color.txt';
    conf['color_file'] = `${conf['deploy_dir']}${color_file}`;
  }
  else color_file = conf['color_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
  const labels = anno.get_tool_labels();
  const colors = anno.get_tool_colors();
  colors.forEach((c, i) => {
    colors[i] = `${parseInt(c.slice(0, 2), 16)},${parseInt(c.slice(2, 4), 16)},${parseInt(c.slice(4, 6), 16)}`;
  });
  const formData = new FormData();
  formData.append('files', new Blob([labels.join('\n')], {type:"text/plain"}), label_file);
  formData.append('files', new Blob([colors.join('\n')], {type:"text/plain"}), color_file);
  formData.append('files', new Blob([JSON.stringify(conf,null,4)], {type:"text/plain"}), '/conf.json');
  iinfer.file_upload(anno.left_container, svpath, formData, orverwrite=true, progress_func=(e) => {}, success_func=(target, svpath, data) => {
    iinfer.hide_loading();
    iinfer.message(`Saved in. label_file=${svpath}${label_file}, color_file=${svpath}${color_file}`);
  }, error_func=(target, svpath, data) => {
    iinfer.hide_loading();
  });
};
/**
 * アノテーションの読込
 * @param {string} image_path 画像のパス
 * @param {function} exists_func アノテーションファイルが見つかったときのコールバック関数。引数にSVGの文字列を取る
 * @param {function} notfound_func アノテーションファイルが見つからなかったときのコールバック関数
 **/
anno.load_anno = (image_path, exists_func, notfound_func) => {
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_download';
  opt['capture_stdout'] = true;
  opt['svpath'] = `${image_path}.svg`;
  iinfer.show_loading();
  iinfer.sv_exec_cmd(opt).then(res => {
    if(!res[0] || !res[0]['success']) {
      notfound_func();
      return;
    }
    if (!res[0]['success']['data']) return;
    const svg_str = atob(res[0]['success']['data']);
    exists_func(svg_str);
  }).catch((e) => {
    console.log(e);
  }).finally(() => {
    iinfer.hide_loading();
  });
};
/**
 * アノテーションの保存
 * @param {string} svpath 保存するフォルダのパス
 * @param {string} image_path 画像のパス
 * @param {$} svg_elem SVG要素
 * @return {void}
 **/
anno.save_anno = (svpath, image_path, svg_elem) => {
  const svg_str = svg_elem.prop('outerHTML');
  const formData = new FormData();
  image_path = image_path.replace(svpath, '');
  formData.append('files', new Blob([svg_str], {type:"image/svg+xml"}), `${image_path}.svg`);
  iinfer.file_upload(anno.left_container, svpath, formData, orverwrite=true, progress_func=(e) => {}, success_func=(target, svpath, data) => {
    iinfer.hide_loading();
    iinfer.message(`Saved in. image_path=${svpath}${image_path}.svg`);
  }, error_func=(target, svpath, data) => {
    iinfer.hide_loading();
  });
};
/**
 * toolのラベルとカラーに合わせてSVGをリフレッシュ
 **/
anno.reflesh_svg = () => {
  const labels = anno.get_tool_labels();
  const colors = anno.get_tool_colors();

  anno.canvas_container.find(`#canvas svg [data-anno-label]`).each((i, comp) => {
    const anno_label = $(comp).attr('data-anno-label');
    let index = -1;
    labels.forEach((label, i) => {
      if (anno_label == labels[i]) {
        index = i;
        return;
      }
    });
    if (index >= 0) {
      $(comp).attr('stroke', `#${colors[index]}`);
      return;
    }
    // ラベルに無いアノテーションを削除マーク
    $(comp).attr('fill-opacity', `1`);
    $(comp).attr('title', `Label not found. '${anno_label}'`);
    //$(comp).remove();
  });
};
/**
 * ファイルリストの取得
 * @param {string} basepath データセットのパス
 * @param {string} svpath 読込むフォルダのパス
 * @param {$} current_ul_elem ツリーメニューの要素
 */
anno.load_filelist = (basepath, svpath, current_ul_elem) => {
  const opt = iinfer.get_server_opt(false, anno.left_container);
  opt['mode'] = 'client';
  opt['cmd'] = 'file_list';
  opt['capture_stdout'] = true;
  opt['svpath'] = svpath;
  iinfer.show_loading();
  iinfer.sv_exec_cmd(opt).then(res => {
    current_ul_elem.html('');
    if(!res[0] || !res[0]['success']) {
      iinfer.hide_loading();
      iinfer.message(res);
      return;
    }
    const file_list = Object.entries(res[0]['success']).sort();
    // 上側ペイン
    file_list.forEach(([key, node]) => {
      if(!node['is_dir']) return;
      if(!node['path'].startsWith(basepath)) return;
      const children = node['children'];
      let current_li_elem = anno.left_container.find(`#${key}`);
      if (current_li_elem.length > 0) {
        current_li_elem.find('.folder-close').remove();
      } else {
        current_li_elem = $(`<li id="${key}" data_path="${node['path']}"/>`);
        current_ul_elem.append(current_li_elem);
      }
      const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
      const current_a_elem = $(`<a href="#" class="folder-open" style="${font_color}" draggable="false">${node['name']}</a>`);
      current_li_elem.append(current_a_elem);
      mk_func = (_b, _p, _e) => {return ()=>{
        anno.load_filelist(_b, _p, _e);
        event.stopPropagation();
      }}
      current_a_elem.off('click').on('click', mk_func(basepath, node['path'], current_ul_elem));
      Object.keys(children).map((k, i) => {
        const n = children[k];
        if(!n['is_dir']) return;
        const ul_elem = $('<ul class="tree_ul"/>').append(`<li id="${k}" data_path="${n['path']}"><a href="#" class="folder-close" style="${font_color}" draggable="false">${n['name']}</a></li>`);
        current_li_elem.append(ul_elem);
        anno.left_container.find(`#${k}`).off('click').on('click', mk_func(basepath, n['path'], current_ul_elem));
      });
    });
    const file_list_elem = anno.left_container.find('.file-list');
    file_list_elem.html('');
    file_list.forEach(([key, node]) => {
      if(!node['path']) return;
      if(!node['path'].startsWith(svpath)) return;
      if(!node['children']) return;
      const children = node['children'];
      Object.entries(children).forEach(([k, n]) => {
        if(n['is_dir']) return;
        // サムネイル画像の表示
        const thum_size = 100;
        const card_elem = $('<div class="card card-hover d-inline-block p-1"><div class="card-body p-0"></div></div>');
        const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${n['path']}\t${thum_size}`);
        const img_elem = $(`<img src="annotation/get_img/${constr}"/>`);
        img_elem.off('load').on('load', (event) => {
          const img = event.currentTarget;
          if (img.width > img.height) {
            img.width = thum_size;
            img.height = thum_size * img.naturalHeight / img.naturalWidth;
          } else {
            img.height = thum_size;
            img.width = thum_size * img.naturalWidth / img.naturalHeight;
          }
        });
        card_elem.find('.card-body').append(img_elem);
        card_elem.off('click').on('click', () => anno.load_image(n, opt));
        file_list_elem.append(card_elem);
      });
    });
  }).catch((e) => {
    console.log(e);
  }).finally(() => {
    iinfer.hide_loading();
  });
};
/**
 * 画像の表示
 * @param {object} node ノード
 * @param {object} opt オプション
 * @return {void}
 **/
anno.load_image = (node, opt) => {
  anno.canvas_container.find('.image_address').val(node['path']);
  // キャンバス画像の表示
  const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${node['path']}\t0`);
  const card_elem = $('<div class="card d-inline-block p-1"><div class="card-body p-0"></div></div>');
  anno.dragscroll(card_elem, card_elem.get(0)); // ドラッグスクロールの設定
  const img_elem = $(`<img src="annotation/get_img/${constr}"/>`);
  const img = img_elem.off('wheel').get(0);
  let svg_elem, svg;
  img_elem.off('load').on('load', () => {
    const image_path = anno.canvas_container.find('.image_address').val();
    anno.load_anno(image_path, (svg_str) => {
      svg_elem = $(svg_str);
      svg_elem.css('position','absolute').css('left',`4px`).css('top',`4px`);
      anno.disable_contextmenu(svg_elem); // 右クリックメニューを無効化
      svg_elem.children().each((i, comp) => {
        anno.comp_mouse_action(comp); // アノテーションのマウスアクション
      });
      card_elem.find('.card-body').append(svg_elem);
      svg = svg_elem.get(0);
      anno.svg_mouse_action(svg_elem, svg); // アノテーション画面のマウスアクション
    }, () => {
      svg_elem = $(`<svg id="svg" xmlns="http://www.w3.org/2000/svg" width="${img.naturalWidth}" height="${img.naturalHeight}" viewBox="0 0 ${img.naturalWidth} ${img.naturalHeight}"/>`);
      svg_elem.css('position','absolute').css('left',`4px`).css('top',`4px`);
      anno.disable_contextmenu(svg_elem); // 右クリックメニューを無効化
      card_elem.find('.card-body').append(svg_elem);
      svg = svg_elem.get(0);
      anno.svg_mouse_action(svg_elem, svg); // アノテーション画面のマウスアクション
    });
  });
  const canvas_elem = anno.canvas_container.find('#canvas');
  const canvas = canvas_elem.get(0);
  anno.canvas_scale = 1.0;
  // 拡大縮小イベント処理
  canvas.onwheel = (event) => {
    event.stopPropagation();
    anno.canvas_scale += event.deltaY * -0.001;
    anno.canvas_scale = Math.min(Math.max(0.125, anno.canvas_scale), 4);
    img.width = img.naturalWidth * anno.canvas_scale;
    svg_elem.css('width', `${img.width}px`).css('height', `${img.height}px`);
  }  
  card_elem.find('.card-body').append(img_elem);
  canvas_elem.html('');
  canvas_elem.append(card_elem);
};
/**
 * アノテーション画面のマウスアクション
 * @param {$} svg_elem SVG要素
 * @param {Element} svg SVG要素
 * @return {void}
 */
anno.svg_mouse_action = (svg_elem, svg) => {
  // キャンバス上でマウスを押したとき、開始座標を記録
  svg.onmousedown = (event) => {
    if (event.which != 1) return false;
    event.stopPropagation();
    // カーソルツールの場合
    if (anno.tool.cursor) {
      svg_elem.children().attr('stroke-width', `2.0`);
      return false;
    }
    // 矩形ツールの場合
    if (anno.tool.bbox) {
      svg_elem.data({
        "down": true,
        "move": false,
        "lastcomp": null,
        "x1": event.offsetX / anno.canvas_scale,
        "y1": event.offsetY / anno.canvas_scale,
      });
      return false;
    }
  };
  // キャンバス上でマウスを動かしたとき、矩形を描画
  svg.onmousemove = (event) => {
    if (!svg_elem.data("down")) return;
    if (event.which != 1) return false;
    if (anno.tool.cursor) return false; // カーソルツールの場合は何もしない
    event.stopPropagation();
    let comp = svg_elem.data("lastcomp");
    const x1 = svg_elem.data("x1");
    const y1 = svg_elem.data("y1");
    const x2 = ~~(event.offsetX / anno.canvas_scale);
    const y2 = ~~(event.offsetY / anno.canvas_scale);
    svg_elem.data("x2", x2);
    svg_elem.data("y2", y2);
    try {
      comp.remove();
      svg.removeChild(comp);
    } catch(e) {}
    comp = anno.make_rect_dom(x1, y1, x2, y2, `#${anno.tool.color}`, '#ffffff', 2, anno.tool.label);
    if (comp) {
      svg.appendChild(comp);
      svg_elem.data("lastcomp", comp);
      anno.comp_mouse_action(comp);
    }
    return false;
  };
  // キャンバス上でマウスを離したとき、矩形を確定
  svg.onmouseup = (event) => {
    if (event.which != 1) return false;
    if (anno.tool.cursor) return false; // カーソルツールの場合は何もしない
    event.stopPropagation();
    //const comp = svg_elem.data("comp");
    //if (comp) {
    //  anno.dragscroll($(comp), comp); // ドラッグスクロールの設定
    //}
    svg_elem.data("down", false);
    svg_elem.data("lastcomp", null);
    return false;
  };
};
/**
 * アノテーションのマウスアクション
 * @param {Element} comp アノテーションのDOM
 **/
anno.comp_mouse_action = (comp) => {
  if (!comp) return;
  comp.onmousedown = (event) => {
    if (event.which != 1) return false;
    event.stopPropagation();
    const comp_elem = $(event.currentTarget);
    // カーソルツールの場合
    if (anno.tool.cursor) {
      comp_elem.data({
        "x1": ~~(event.offsetX / anno.canvas_scale),
        "y1": ~~(event.offsetY / anno.canvas_scale),
      });
      comp_elem.attr('fill-opacity', `1.0`);
      const svg_elem = anno.canvas_container.find('#canvas svg');
      svg_elem.children().attr('stroke-width', `2.0`);
      svg_elem.data('selectcomp', event.currentTarget);
      svg_elem.append(comp_elem); // 最前面に移動
      comp_elem.attr('stroke-width', `5.0`);
      return false;
    }
  };
  comp.onmousemove = (event) => {
    if (event.which != 1) return false;
    //event.stopPropagation();
    const comp_elem = $(event.currentTarget);
    const x1 = comp_elem.data("x1");
    const y1 = comp_elem.data("y1");
    const x2 = ~~(event.offsetX / anno.canvas_scale);
    const y2 = ~~(event.offsetY / anno.canvas_scale);
    // カーソルツールの場合
    if (anno.tool.cursor) {
      const x = parseInt(comp_elem.attr('x'));
      const y = parseInt(comp_elem.attr('y'));
      const w = parseInt(comp_elem.attr('width'));
      const h = parseInt(comp_elem.attr('height'));
      const mw = parseInt(comp_elem.parent().attr('width'));
      const mh = parseInt(comp_elem.parent().attr('height'));
      comp_elem.attr('x', Math.min(Math.max(x+x2-x1, 0), mw-w));
      comp_elem.attr('y', Math.min(Math.max(y+y2-y1, 0), mh-h));
      comp_elem.data({
        "x1": x2,
        "y1": y2,
      });
      return false;
    }
  };
  comp.onmouseup = (event) => {
    if (event.which != 1) return false;
    //event.stopPropagation();
    const comp_elem = $(event.currentTarget);
    // カーソルツールの場合
    if (anno.tool.cursor) {
      comp_elem.attr('fill-opacity', `0.5`);
      return false;
    }
  };
};
/**
 * 矩形のDOMを作成
 * @param {number} x1 開始点のx座標
 * @param {number} y1 開始点のy座標
 * @param {number} x2 終了点のx座標
 * @param {number} y2 終了点のy座標
 * @param {string} stroke 線の色
 * @param {string} fill 塗りつぶしの色
 * @param {number} stroke_width 線の太さ
 * @param {string} label ラベル
 * @return {Element} 矩形のDOM
 **/
anno.make_rect_dom = (x1, y1, x2, y2, stroke, fill, stroke_width, label) => {
  const w = Math.abs(x2-x1);
  const h = Math.abs(y2-y1);
  if (w <= 0 || h <= 0) return null;
  const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  rect.setAttribute('x', Math.min(x1, x2));
  rect.setAttribute('y', Math.min(y1, y2));
  rect.setAttribute('width', w);
  rect.setAttribute('height', h);
  rect.setAttribute('fill', `${fill}`);
  rect.setAttribute('stroke', `${stroke}`);
  rect.setAttribute('stroke-width', `${stroke_width}`);
  rect.setAttribute('fill-opacity', `0.5`);
  rect.setAttribute('data-anno-label', `${label}`);
  rect.setAttribute('data_anno-type', `rect`);
  return rect;
};
/**
 * 右クリックメニューを無効化
 * @param {string} elem 無効化する要素
 * @return {void}
 **/
anno.disable_contextmenu = (elem) => {
  elem.off('contextmenu').on('contextmenu', () => {return false;});
};
/**
 * ドラッグスクロールを設定
 * @param {$} target_elem ドラッグスクロールを設定する要素
 * @param {Element} target ドラッグスクロールを設定する要素
 * @return {void}
 **/
anno.dragscroll = (target_elem, target) => {
  target.onmousedown = (event) => {
    if (event.which != 3) return false;
    event.stopPropagation();
    if (!target_elem.data("sl")) target_elem.data("sl", 0);
    if (!target_elem.data("st")) target_elem.data("st", 0);
    target_elem.data({
      "down": true,
      "move": false,
      "x": event.clientX,
      "y": event.clientY,
      "scrollleft": target_elem.data("sl"),
      "scrolltop": target_elem.data("st"),
    });
    return false;
  };
  target.onmousemove = (event) => {
    if (!target_elem.data("down")) return;
    if (event.which != 3) return false;
    event.stopPropagation();
    let move_x = target_elem.data("x") - event.clientX;
    let move_y = target_elem.data("y") - event.clientY;
    move_x = target_elem.data("scrollleft") - move_x;
    move_y = target_elem.data("scrolltop") - move_y;
    move_x = move_x<0 ? 0 : move_x;
    move_y = move_y<0 ? 0 : move_y;
    target_elem.css('left', move_x + 'px').data("sl", move_x);
    target_elem.css('top', move_y + 'px').data("st", move_y);
    return false;
  };
  target.onmouseup = (event) => {
    if (event.which != 3) return false;
    event.stopPropagation();
    target_elem.data("down", false);
    return false;
  };
};
anno.tool = {};
/**
 * ツールの初期化
 **/
anno.init_tool_button = () => {
  const toggle_func = (elem) => {
    anno.canvas_container.find('.tool_bot').removeClass('active');
    $(elem).addClass('active');
  }
  anno.canvas_container.find('.tool_bot_cursor').off('click').on('click', () => {
    anno.tool.cursor = true;
    anno.tool.bbox = false;
    anno.tool.polygon = false;
    toggle_func('.tool_bot_cursor');
  });
  anno.canvas_container.find('.tool_bot_cursor').click();
  anno.canvas_container.find('.tool_bot_bbox').off('click').on('click', () => {
    anno.tool.cursor = false;
    anno.tool.bbox = true;
    anno.tool.polygon = false;
    toggle_func('.tool_bot_bbox');
  });
  anno.canvas_container.find('.tool_bot_polygon').off('click').on('click', () => {
    anno.tool.cursor = false;
    anno.tool.bbox = false;
    anno.tool.polygon = true;
    toggle_func('.tool_bot_polygon');
  });
  anno.canvas_container.find('.tool_bot_reload').off('click').on('click', () => {
    anno.left_container.find('.deploy_names').change();
  });
  anno.canvas_container.find('.tool_bot_save').off('click').on('click', () => {
    const svpath = anno.left_container.find('.deploy_names').val();
    if (!svpath) return;
    anno.save_label_color(svpath);
  });
  anno.canvas_container.find('.tool_bot_annosave').off('click').on('click', () => {
    const svpath = anno.left_container.find('.deploy_names').val();
    const image_path = anno.canvas_container.find('.image_address').val();
    if (!svpath || !image_path) return;
    anno.save_anno(svpath, image_path, anno.canvas_container.find('#canvas svg'));
  });
  document.onkeydown = (event) => {
    if (event.key == 'Delete') {
      const svg_elem = anno.canvas_container.find('#canvas svg');
      const comp = svg_elem.data('selectcomp');
      if(comp) comp.remove();
    }
  };
};
/**
 * ページ読み込み時の処理
 */
anno.onload = () => {
  iinfer.show_loading();
  iinfer.get_server_opt(true, anno.left_container).then((opt) => {
    iinfer.load_server_list(anno.left_container, (opt) => anno.deploy_list(), true);
  });
  anno.init_tool_button();
};
