const anno = {};
anno.left_container = $('#left_container');
anno.canvas_container = $('#canvas_container');
/**
 * デプロイリストの取得
 **/
anno.deploy_list = () => {
  // deploy_listの取得
  cmdbox.deploy_list(anno.left_container).then(res => {
    if (!res) return;
    const deploy_names_elem = anno.left_container.find('.deploy_names');
    res['data'].forEach(data => {
      // train_datasetを持っている場合のみ表示
      if (!data['train_dataset']) return;
      deploy_names_elem.append(`<option value="/${data['name']}">${data['name']}</option>`);
    });
    deploy_names_elem.off('change').on('change', () => {
      anno.load_conf(deploy_names_elem.val());
    });
    deploy_names_elem.change();
  }).catch((e) => {
    cmdbox.hide_loading();
    console.log(e);
  });
};
/**
 * キャンバスを初期化
 **/
anno.clear_canvas = () => {
  anno.canvas_container.find('#canvas').html('');
  anno.canvas_container.find('.anno-list').html('');
};
/**
 * ラベルとカラーを初期化
 **/
anno.clear_labels = () => {
  anno.canvas_container.find('#tags_labels .dropdown-labels').remove();
  anno.canvas_container.find('.tag_label').text("");
};
/**
 * conf.jsonの取得
 * @param {string} svpath 読込むフォルダのパス
 * @return {void}
 **/
anno.load_conf = (svpath) => {
  if (!svpath) {
    cmdbox.message('No deployments include train datasets.');
    return;
  }
  // conf.jsonの取得
  cmdbox.file_download(anno.left_container, `${svpath}/conf.json`).then(res => {
    if (!res) return;
    anno.clear_canvas();
    anno.clear_labels();
    const conf = anno.tool.conf = JSON.parse(atob(res['data']));
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
    // ラベルとカラーの追加ボタン
    const tags_labels_elem = anno.canvas_container.find('#tags_labels');
    tags_labels_elem.find('.tool_bot_add_tag').off('click').on('click', (event) => {
      const label = tags_labels_elem.find('.new_label').val();
      const color = tags_labels_elem.find('.new_label_color').val().slice(1);
      if (!label || !color) return;
      anno.add_label(label, color, tags_labels_elem);
      tags_labels_elem.find('.new_label').val('');
      tags_labels_elem.find('.new_label_color').attr('value', `#${cmdbox.randam_color()}`);
      event.stopPropagation();
    });
  });
};
/**
 * label.txtの読込み
 * @param {string} svpath label.txtのパス
 */
anno.load_label = (svpath) => {
  cmdbox.file_download(anno.left_container, svpath).then(res => {
    if (!res) return
    const labels = atob(res['data']).split(/\r?\n/);
    const tags_labels_elem = anno.canvas_container.find('#tags_labels');
    tags_labels_elem.children('.dropdown-labels').remove();
    const anno_list_elem = anno.canvas_container.find('.anno-list');
    const svg_elem = anno.canvas_container.find('svg');
    labels.forEach((label, i) => {
      const color = cmdbox.randam_color();
      anno.add_label(label, color, tags_labels_elem);
      svg_elem.find(`[data-anno-label="${label}"]`).attr('stroke', `#${color}`);
      anno_list_elem.each((i, elem) => {
        const a_elem = $(elem).find(`[data-anno-label="${label}"]`);
        const color_elem = a_elem.find('input[type="color"]');
        color_elem.val(`#${color}`);
      });
    });
  }).finally(() => {
    anno.canvas_container.find('#tags_labels .dropdown-item:first').click();
    cmdbox.hide_loading();
  });
};
/**
 * ラベルの追加
 * @param {string} label ラベル
 * @param {string} color カラーコード
 * @param {$} tags_labels_elem ラベルリストの親要素
 **/
anno.add_label = (label, color, tags_labels_elem) => {
  const li_elem = $(`<li class="dropdown-labels"></li>`);
  const a_elem = $(`<a class="dropdown-item d-flex pt-0 pb-0" href="#" data-label="${label}" data-color="${color}"></a>`);
  const input_elem = $(`<input type="color" value="#${color}" style="width: 20px; height: 20px;"/>`);
  input_elem.change((event) => {
    const input_elem = $(event.currentTarget);
    const a_elem = input_elem.parent();
    input_elem.attr('value', event.currentTarget.value);
    a_elem.attr('data-color', event.currentTarget.value.slice(1));
    anno.tool.label = a_elem.attr('data-label');
    anno.tool.color = a_elem.attr('data-color');
    anno.reflesh_svg();
    anno.canvas_container.find('.tag_label_color').attr('value', `#${anno.tool.color}`);
    const anno_list_elem = anno.canvas_container.find('.anno-list');
    anno_list_elem.each((i, elem) => {
      const a_elem = $(elem).find(`[data-anno-label="${anno.tool.label}"]`);
      const color_elem = a_elem.find('input[type="color"]');
      color_elem.val(`#${anno.tool.color}`);
    });
  });
  const del_elem = $(`<button class="btn ms-auto p-0"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">`
    + `<path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"></path></svg>`);
  del_elem.off('click').on('click', (event) => {
    if (!window.confirm(`Delete label '${label}'?`)) return;
    const li_elem = $(event.currentTarget).parent().parent();
    li_elem.remove();
    const f_a_elem = anno.canvas_container.find(`#tags_labels .dropdown-item:first`);
    anno.tool.label = f_a_elem.attr('data-label');
    anno.tool.color = f_a_elem.attr('data-color');
    anno.tool.label = anno.tool.label ? anno.tool.label : '';
    anno.tool.color = anno.tool.color ? anno.tool.color : cmdbox.randam_color();
    anno.canvas_container.find('.tag_label').text(anno.tool.label);
    anno.canvas_container.find('.tag_label_color').attr('value', `#${anno.tool.color}`);
    anno.reflesh_svg();
    event.stopPropagation();
  });
  a_elem.append(input_elem);
  a_elem.append(`<span class="ms-2 mb-1">${label}</span>`);
  a_elem.append(del_elem);
  li_elem.append(a_elem);
  a_elem.off('click').on('click', (event) => {
    const a_elem = $(event.currentTarget);
    anno.tool.label = a_elem.attr('data-label');
    anno.tool.color = a_elem.attr('data-color');
    anno.canvas_container.find('.tag_label').text(anno.tool.label);
    anno.canvas_container.find('.tag_label_color').attr('value', `#${anno.tool.color}`);
  });
  tags_labels_elem.append(li_elem);
  a_elem.click();
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
  cmdbox.file_download(anno.left_container, svpath).then(res => {
    if (!res) return;
    const colors = atob(res['data']).split(/\r?\n/);
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
          color = cmdbox.randam_color();
        }
        $(ak).attr('data-color', color).find('input').attr('value', `#${color}`);
        const label = $(ak).attr('data-label');
        const anno_list_elem = anno.canvas_container.find('.anno-list');
        anno_list_elem.each((i, elem) => {
          const a_elem = $(elem).find(`[data-anno-label="${label}"]`);
          const color_elem = a_elem.find('input[type="color"]');
          color_elem.val(`#${color}`);
        });
      });
      ref_elem.find('.dropdown-item:first').click();
    }
    set_colors(colors);
    anno.reflesh_svg();
  }).finally(() => {
    anno.canvas_container.find('#tags_labels .dropdown-item:first').click();
    cmdbox.hide_loading();
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
    cmdbox.message('deploy_dir is not set');
    return;
  }
  cmdbox.show_loading();
  anno.blur_comp();
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
  cmdbox.file_upload(anno.left_container, svpath, formData, orverwrite=true, progress_func=(e) => {}, success_func=(target, svpath, data) => {
    cmdbox.hide_loading();
    cmdbox.message(`Saved in. label_file=${svpath}${label_file}, color_file=${svpath}${color_file}`);
  }, error_func=(target, svpath, data) => {
    cmdbox.hide_loading();
  });
};
/**
 * アノテーションの読込
 * @param {string} image_path 画像のパス
 * @param {function} exists_func アノテーションファイルが見つかったときのコールバック関数。引数にSVGの文字列を取る
 * @param {function} notfound_func アノテーションファイルが見つからなかったときのコールバック関数
 **/
anno.load_anno = (image_path, exists_func, notfound_func) => {
  cmdbox.file_download(anno.left_container, `${image_path}.svg`, error_func=notfound_func).then(res => {
    if (!res) {
      cmdbox.hide_loading();
      return;
    }
    const svg_str = atob(res['data']);
    exists_func(svg_str);
    cmdbox.hide_loading();
  });
};
/**
 * アノテーションの保存
 * @param {string} svpath 保存するフォルダのパス
 * @param {string} image_path 画像のパス
 * @param {$} svg_elem SVG要素
 * @param {bool} nomsg メッセージを表示しない
 * @return {void}
 **/
anno.save_anno = (svpath, image_path, svg_elem, nomsg=false, success_func=undefined) => {
  cmdbox.show_loading();
  anno.blur_comp(svg_elem);
  const svg_str = svg_elem.prop('outerHTML');
  const formData = new FormData();
  image_path = image_path.replace(svpath, '');
  formData.append('files', new Blob([svg_str], {type:"image/svg+xml"}), `${image_path}.svg`);
  cmdbox.file_upload(anno.left_container, svpath, formData, orverwrite=true, (e) => {}, (target, svpath, data) => {
    const fl_svg_elem = anno.left_container.find(`.file-list [data-path='${svpath}${image_path}.svg']`);
    const fl_img_elem = anno.left_container.find(`.file-list [data-path='${svpath}${image_path}']`);
    const svg_src = fl_svg_elem.attr('src');
    const img_src = fl_img_elem.attr('src');
    if (svg_src) {
      // アノテーション画像がすでに存在している場合はリロード
      fl_svg_elem.attr('src', `${svg_src.split('?')[0]}?r=${cmdbox.randam_string(8)}`);
    } else if (img_src) {
      // アノテーション画像が無く元画像が存在している場合はSVGを追加
      const conary = atob(img_src.split('?')[0].split('/').slice(-1)[0]).split('\t');
      const constr = "annotation/get_img/" + btoa(`${conary.slice(0, 4).join('\t')}\t${svpath}${image_path}.svg\t${conary.slice(5, 6)}\t${conary.slice(6, 7)}`);
      const svg_elem = $(`<img src="${constr}?r=${cmdbox.randam_string(8)}" data-path="${svpath}${image_path}.svg" style="position: absolute; left: 0px; top: 0px;"/>`);
      svg_elem.attr('width', fl_img_elem.attr('width')).attr('height', fl_img_elem.attr('height'));
      fl_img_elem.parent().append(svg_elem);
    }
    cmdbox.hide_loading();
    if (!nomsg) cmdbox.message(`Saved in. image_path=${svpath}${image_path}.svg`);
    if (success_func) success_func(`${svpath}${image_path}.svg`);
  }, error_func=(target, svpath, data) => {
    cmdbox.hide_loading();
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
  const path_parts = svpath.split('/');
  // MS COCO Object Detection formatの保存先を設定
  if (path_parts.length <= 3) {
    const clean_menu = (menu_elem, menu_html) => {
      menu_elem.find('span').html(menu_html);
      menu_elem.removeAttr('data-load-type');
      menu_elem.removeAttr('data-load-path');
      menu_elem.removeAttr('data-load-input-path');
      menu_elem.removeAttr('data-load-src');
      menu_elem.off('click');
    };
    clean_menu(anno.left_container.find('.tool_bot_annoload_all_coco'), `Import MS COCO format`);
    clean_menu(anno.left_container.find('.tool_bot_annosave_all_coco'), `Export MS COCO format`);
    clean_menu(anno.left_container.find('.tool_bot_annosave_all_cityscapes'), `Export Cityscapes format`);
  }
  else if (path_parts.length > 3) {
    const deploy_name = path_parts[1];
    const input_name = path_parts[2];
    const subset = path_parts.slice(-1)[0];
    {
      const load_path = `/${deploy_name}/${input_name}/${subset}.json`;
      const load_input_path = `/${deploy_name}/${input_name}`;
      const menu_elem = anno.left_container.find('.tool_bot_annoload_all_coco');
      menu_elem.find('span').html(`Import MS COCO format from "${load_path}" to "${load_input_path}/${subset}"`);
      menu_elem.attr('data-load-type', 'coco');
      menu_elem.attr('data-load-path', load_path);
      menu_elem.attr('data-load-input-path', load_input_path);
      menu_elem.attr('data-load-src', svpath);
      menu_elem.off('click').on('click', () => {
        anno.load_annoall_coco(menu_elem);
      });
    }
    {
      const save_path = `/${deploy_name}/${input_name}/${subset}.json`;
      const menu_elem = anno.left_container.find('.tool_bot_annosave_all_coco');
      menu_elem.find('span').html(`Export MS COCO format to "${save_path}"`);
      menu_elem.attr('data-save-type', 'coco');
      menu_elem.attr('data-save-path', save_path);
      menu_elem.attr('data-save-src', svpath);
      menu_elem.off('click').on('click', () => {
        anno.save_annoall_coco(menu_elem);
      });
    }
    {
      const save_path = `/${deploy_name}/${input_name}/cityscapes.zip`;
      const menu_elem = anno.left_container.find('.tool_bot_annosave_all_cityscapes');
      menu_elem.find('span').html(`Export Cityscapes format to "${save_path}"`);
      menu_elem.attr('data-save-type', 'cityscapes');
      menu_elem.attr('data-save-path', save_path);
      menu_elem.attr('data-save-src', `/${deploy_name}/${input_name}`);
      menu_elem.off('click').on('click', () => {
        anno.save_annoall_cityscapes(menu_elem);
      });
    }
  }
  cmdbox.file_list(anno.left_container, svpath).then(res => {
    current_ul_elem.html('');
    if(!res) {
      cmdbox.hide_loading();
      return;
    }
    const opt = cmdbox.get_server_opt(false, anno.left_container);
    const file_list = Object.entries(res).sort();
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
      const mk_func = (_b, _p, _e) => {return ()=>{
        anno.clear_canvas();
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
    // 下側ペイン
    const file_list_elem = anno.left_container.find('.file-list');
    file_list_elem.html('');
    file_list.forEach(([key, node]) => {
      if(!node['path']) return;
      if(!node['path'].startsWith(svpath)) return;
      if(!node['children']) return;
      const children = node['children'];
      Object.entries(children).forEach(([k, n]) => {
        if(n['is_dir']) return;
        if(!n['mime_type'].startsWith('image')) {
          const card_elem = $(`<div class="card d-inline-block p-1"><div class="card-body p-0" style="position:relative;"></div></div>`);
          card_elem.find('.card-body').append('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark m-2" viewBox="0 0 16 16">'
                                            + '<path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z"/>'
                                            + '</svg>');
          card_elem.find('.card-body').append(`<span class="me-2">${n['name']}</span>`);
          file_list_elem.append(card_elem);
          return;
        }
        // サムネイル画像の表示
        const thum_size = 100;
        const img_name = n['path'].split('/').slice(-1)[0];
        const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${n['path']}\t${opt['scope']}\t${thum_size}`);
        const img_elem = $(`<img src="annotation/get_img/${constr}?r=${cmdbox.randam_string(8)}" data-path="${n['path']}" alt="${img_name}"/>`);
        let card_elem = undefined;
        // SVGファイルの場合は元画像があるかどうかを確認
        if(n['path'].endsWith('.svg')) {
          img_elem.attr('title', img_name.replace(/\.svg$/, ''));
          const simg_elem = file_list_elem.find(`[data-path='${n['path'].replace(/\.svg$/, '')}']`);
          img_elem.css('position', 'absolute').css('left', '0').css('top', '0');
          card_elem = simg_elem.parents('.card');
        } else {
          card_elem = $('<div class="card card-hover d-inline-block p-1"><div class="card-body p-0" style="position:relative;"></div></div>');
          card_elem.off('click').on('click', (event) => {
            file_list_elem.find('.card-selected').removeClass('card-selected');
            $(event.target).addClass('card-selected');
            anno.load_image(n, opt);
          });
          img_elem.addClass('card-thumbnail');
        }
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
        file_list_elem.append(card_elem);
      });
    });
  }).catch((e) => {
    console.log(e);
  }).finally(() => {
    cmdbox.hide_loading();
  });
};
/**
 * キャンバスに画像とアノテーションを表示
 * @param {object} node ノード
 * @param {object} opt オプション
 * @return {void}
 **/
anno.load_image = (node, opt) => {
  anno.canvas_container.find('.image_address').val(node['path']);
  // キャンバス画像の表示
  const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${node['path']}\t${opt['scope']}\t0`);
  const card_elem = $('<div class="card d-inline-block p-1"><div class="card-body p-0"></div></div>');
  anno.dragscroll(card_elem, card_elem.get(0)); // ドラッグスクロールの設定
  const img_elem = $(`<img class="canvas_image" src="annotation/get_img/${constr}" data-path="${node['path']}"/>`);
  img_elem.data('node', node);
  img_elem.data('opt', opt);
  const img = img_elem.off('wheel').get(0);
  anno.canvas_scale = anno.canvas_scale ? anno.canvas_scale : 1.0;
  const canvas_elem = anno.canvas_container.find('#canvas');
  const zoom_label = anno.canvas_container.find('.tool_label_zoom');
  const zoom_bot = anno.canvas_container.find('.tool_bot_zoom');
  const rescale = (canvas_elem, card_elem, img, svg_elem, event) => {
    // zoomボタンを現在のスケールに合わせて表示切り替え
    zoom_bot.find('.bi').hide();
    if (anno.canvas_scale < 1.0) zoom_bot.find('.bi-zoom-out').show();
    else if (anno.canvas_scale > 1.0) zoom_bot.find('.bi-zoom-in').show();
    else zoom_bot.find('.bi-search').show();
    // スケール計算
    if (event && anno.canvas_scale + event.deltaY * -0.001 <= 0.3) return;
    anno.canvas_scale += event ? event.deltaY * -0.001 : 0;
    anno.canvas_scale = Math.min(Math.max(0.3, anno.canvas_scale), 4);
    // 拡大縮小する差分サイズ計算
    const dw = img.naturalWidth * (1-anno.canvas_scale);
    const dh = img.naturalHeight * (1-anno.canvas_scale);
    // マウス位置を中心にしたときの差分位置計算
    const dx = event ? dw * (event.offsetX / (img.naturalWidth*anno.canvas_scale)) : 0;
    const dy = event ? dh * (event.offsetY / (img.naturalHeight*anno.canvas_scale)) : 0;
    // 拡大縮小操作を行う前の位置計算
    anno.canvas_orgLeft = anno.canvas_orgLeft ? anno.canvas_orgLeft : 0;
    anno.canvas_orgTop = anno.canvas_orgTop ? anno.canvas_orgTop : 0;
    // 拡大縮小操作を行った後の位置計算
    const card_left = anno.canvas_orgLeft + dx;
    const card_top = anno.canvas_orgTop + dy;
    // 画像とSVGのサイズ変更
    img.width = img.naturalWidth * anno.canvas_scale;
    img.height = img.naturalHeight * anno.canvas_scale;
    svg_elem.css('width', `${img.width}px`).css('height', `${img.height}px`);
    // 画像とSVGの位置変更
    card_elem.css('left', `${card_left}px`).css('top', `${card_top}px`);
    // ズームボタンラベルに拡大率を表示
    zoom_label.text(`${(anno.canvas_scale * 100).toFixed(0)}%`);
    // 右クリックドラックで移動するときのために位置情報を保存
    card_elem.data({
      "sl": card_left,
      "st": card_top,
    });
  };
  zoom_bot.off('click').on('click', (event) => {
    anno.canvas_scale = 1.0;
    const svg_elem = canvas_elem.find('svg');
    rescale(canvas_elem, card_elem, img, svg_elem, null);
  });
  // 画像が読み込まれたとき
  img_elem.off('load').on('load', () => {
    anno.canvas_orgLeft = 0;
    anno.canvas_orgTop = 0;
    const image_path = anno.canvas_container.find('.image_address').val();
    // アノテーションの読込
    anno.load_anno(image_path, (svg_str) => {
      // アノテーションが見つかった場合
      const svg_elem = $(svg_str);
      svg_elem.css('position','absolute').css('left',`4px`).css('top',`4px`).css('width','').css('height','');
      svg_elem.children().each((i, comp) => {
        $(comp).attr('id', cmdbox.randam_string(16));
      });
      anno.disable_contextmenu(svg_elem); // 右クリックメニューを無効化
      card_elem.find('.card-body').append(svg_elem);
      const svg = svg_elem.get(0);
      anno.svg_mouse_action(svg_elem, svg); // アノテーション画面のマウスアクション
      anno.reflesh_svg();
      anno.load_annolist(svg_elem);
      rescale(canvas_elem, card_elem, img, svg_elem, null);
    }, () => {
      // アノテーションが見つからなかった場合
      const svg_elem = $(`<svg id="svg" xmlns="http://www.w3.org/2000/svg" width="${img.naturalWidth}" height="${img.naturalHeight}" viewBox="0 0 ${img.naturalWidth} ${img.naturalHeight}"/>`);
      svg_elem.css('position','absolute').css('left',`4px`).css('top',`4px`);
      anno.disable_contextmenu(svg_elem); // 右クリックメニューを無効化
      card_elem.find('.card-body').append(svg_elem);
      const svg = svg_elem.get(0);
      anno.svg_mouse_action(svg_elem, svg); // アノテーション画面のマウスアクション
      anno.load_annolist(svg_elem);
      rescale(canvas_elem, card_elem, img, svg_elem, null);
    });
  });
  const canvas = canvas_elem.get(0);
  // 拡大縮小イベント処理
  canvas.onwheel = (event) => {
    if (!event.ctrlKey) return;
    event.stopPropagation();
    event.preventDefault();
    const svg_elem = canvas_elem.find('svg');
    rescale(canvas_elem, card_elem, img, svg_elem, event);
  }  
  card_elem.find('.card-body').append(img_elem);
  canvas_elem.html('');
  canvas_elem.append(card_elem);
};
/**
 * アノテーションリストを再読み込み
 * @param {$} svg_elem SVG要素
 **/
anno.load_annolist = (svg_elem) => {
  const anno_list_elem = anno.canvas_container.find('.anno-list');
  anno_list_elem.html('');
  anno.blur_comp();
  svg_elem.children().each((i, comp) => {
    const comp_elem = $(comp);
    const color = comp_elem.attr('stroke');
    const label = comp_elem.attr('data-anno-label');
    const a_elem = $(anno.canvas_container.find('#anno_item_temp').prop('outerHTML'));
    a_elem.find('input').attr('value', color);
    a_elem.attr('data-anno-id', comp_elem.attr('id'));
    a_elem.attr('data-anno-label', label);
    a_elem.attr('id', null);
    // アノテーションリストをクリックしたときにアノテーションを選択
    a_elem.off('click').on('click', (event) => {
      const a_elem = $(event.currentTarget);
      const svg_elem = anno.canvas_container.find('#canvas svg');
      const comp_elem = svg_elem.find(`#${a_elem.attr('data-anno-id')}`);
      if (comp_elem.length <= 0) return;
      svg_elem.data('selectcomp', comp_elem.get(0));
      svg_elem.append(comp_elem); // 最前面に移動
      anno.blur_comp(svg_elem);
      comp_elem.attr('stroke-width', `5.0`);
      a_elem.css('background-color', 'var(--bs-list-group-action-active-bg)');
    });
    const del_elem = a_elem.find('button');
    // アノテーションリストの削除ボタンをクリックしたときにアノテーションを削除
    del_elem.off('click').on('click', (event) => {
      const a_elem = $(event.currentTarget).parent().parent();
      const comp_elem = svg_elem.find(`#${a_elem.attr('data-anno-id')}`);
      comp_elem.remove();
      a_elem.remove();
      anno.clear_svg_data(svg_elem);
    });
    const strong_elem = a_elem.find('strong');
    strong_elem.text(label);
    a_elem.removeClass('d-none');
    anno_list_elem.append(a_elem);
  });
  if (svg_elem.children().length<=0) {
    const a_elem = $(anno.canvas_container.find('#anno_item_temp').prop('outerHTML'));
    a_elem.find('input').remove();
    a_elem.find('button').remove();
    a_elem.removeClass('d-none');
    anno_list_elem.append(a_elem);
  }
};
/**
 * アノテーション画面のマウスアクション
 * @param {$} svg_elem SVG要素
 * @param {Element} svg SVG要素
 * @return {void}
 */
anno.svg_mouse_action = (svg_elem, svg) => {
  // 多角形の作成
  const mk_poly = (svg, svg_elem, event, add_mode) => {
    let comp = svg_elem.data("lastcomp");
    const point = [~~(event.offsetX / anno.canvas_scale), ~~(event.offsetY / anno.canvas_scale)];
    let points_ary = svg_elem.data("points");
    if (!points_ary) {
      points_ary = [];
      points_ary.push(point);
    }
    points_ary = add_mode ? points_ary : points_ary.slice(0, -1);
    points_ary.push(point);
    const points_str = anno.join_points(points_ary);
    comp = anno.make_polygon_dom(points_str, `#${anno.tool.color}`, '#ffffff', 2, anno.tool.label, comp);
    svg.appendChild(comp);
    svg_elem.data("lastcomp", comp);
    svg_elem.data("points", points_ary);
    if (add_mode && points_ary.length > 2) {
      anno.load_annolist(svg_elem);
    }
  }
  // キャンバス上でマウスを押したとき
  svg.onmousedown = (event) => {
    //event.stopPropagation();
    // 左クリック以外の場合
    if (event.which != 1) return false;
    const comp = event.target;
    const comp_elem = $(event.target);
    // カーソルツールの場合
    if (anno.tool.cursor) {
      const x1 = ~~(event.offsetX / anno.canvas_scale);
      const y1 = ~~(event.offsetY / anno.canvas_scale);
      // 矩形の場合
      if (comp_elem.attr('data-anno-type')=='rect') {
        const x = parseInt(comp_elem.attr('x'));
        const y = parseInt(comp_elem.attr('y'));
        const w = parseInt(comp_elem.attr('width'));
        const h = parseInt(comp_elem.attr('height'));
        let edge = undefined;
        edge = 'center';
        edge = Math.abs(x-x1) < 20 && Math.abs(y-y1) < 20 ? 'left-top' : edge;
        edge = Math.abs(x+w-x1) < 20 && Math.abs(y-y1) < 20 ? 'right-top' : edge;
        edge = Math.abs(x-x1) < 20 && Math.abs(y+h-y1) < 20 ? 'left-bottom' : edge;
        edge = Math.abs(x+w-x1) < 20 && Math.abs(y+h-y1) < 20 ? 'right-bottom' : edge;
        comp_elem.data({
          "edge": edge,
          "x1": x1,
          "y1": y1,
        });
      }
      // 多角形の場合
      else if (comp_elem.attr('data-anno-type')=='polygon') {
        const points_ary = anno.parse_points(comp_elem.attr('points'));
        let edge = -1;
        points_ary.forEach((point, i) => {
          edge = Math.abs(point[0]-x1) < 20 && Math.abs(point[1]-y1) < 20 ? i : edge;
        });
        comp_elem.data({
          "edge": edge,
          "x1": x1,
          "y1": y1,
          "points": points_ary,
        });
      }
      svg_elem.data('selectcomp', comp);
      svg_elem.append(comp_elem); // 最前面に移動
      anno.blur_comp(svg_elem);
      comp_elem.attr('stroke-width', `5.0`);
      const id = comp_elem.attr('id');
      anno.canvas_container.find('.anno-list').find(`[data-anno-id='${id}']`).css('background-color', 'var(--bs-list-group-action-active-bg)');
      return false;
    }
    // 矩形ツールの場合
    if (anno.tool.bbox) {
      svg_elem.data({
        "down": true,
        "lastcomp": null,
        "x1": ~~(event.offsetX / anno.canvas_scale),
        "y1": ~~(event.offsetY / anno.canvas_scale),
      });
      return false;
    }
    // 多角形ツールの場合
    if (anno.tool.polygon) {
      // マウスダウンしていない場合
      if (!svg_elem.data("down")) {
        svg_elem.data({
          "down": true,
          "lastcomp": null,
        });
      }
      mk_poly(svg, svg_elem, event, true);
      return false;
    }
  };
  // キャンバス上でマウスを動かしたとき
  svg.onmousemove = (event) => {
    //event.stopPropagation();
    // 左クリック以外の場合
    if (event.which != 1 && !anno.tool.polygon) return false;
    // カーソルツールの場合
    if (anno.tool.cursor) {
      const comp = svg_elem.data('selectcomp');
      const comp_elem = $(comp ? comp : event.target);
      const x1 = comp_elem.data("x1");
      const y1 = comp_elem.data("y1");
      const x2 = ~~(event.offsetX / anno.canvas_scale);
      const y2 = ~~(event.offsetY / anno.canvas_scale);
      const edge = comp_elem.data('edge');
      // 矩形の場合
      if (comp_elem.attr('data-anno-type')=='rect') {
        const x = parseInt(comp_elem.attr('x'));
        const y = parseInt(comp_elem.attr('y'));
        const w = parseInt(comp_elem.attr('width'));
        const h = parseInt(comp_elem.attr('height'));
        const mw = parseInt(svg_elem.attr('width'));
        const mh = parseInt(svg_elem.attr('height'));
        if (edge == 'center') {
          comp_elem.attr('x', Math.min(Math.max(x+(x2-x1), 0), mw-w));
          comp_elem.attr('y', Math.min(Math.max(y+(y2-y1), 0), mh-h));
        } else if (edge == 'left-top') {
          comp_elem.attr('x', Math.min(Math.max(x+(x2-x1), 0), mw-w));
          comp_elem.attr('y', Math.min(Math.max(y+(y2-y1), 0), mh-h));
          comp_elem.attr('width', Math.max(w-(x2-x1), 20));
          comp_elem.attr('height', Math.max(h-(y2-y1), 20));
        } else if (edge == 'right-top') {
          comp_elem.attr('y', Math.min(Math.max(y+(y2-y1), 0), mh-h));
          comp_elem.attr('width', Math.min(Math.max(w+(x2-x1), 20), mw-x));
          comp_elem.attr('height', Math.max(h-(y2-y1), 20));
        } else if (edge == 'left-bottom') {
          comp_elem.attr('x', Math.min(Math.max(x+(x2-x1), 0), mw-w));
          comp_elem.attr('width', Math.max(w-(x2-x1), 20));
          comp_elem.attr('height', Math.min(Math.max(h+(y2-y1), 20), mh-y));
        } else if (edge == 'right-bottom') {
          comp_elem.attr('width', Math.min(Math.max(w+(x2-x1), 20), mw-x));
          comp_elem.attr('height', Math.min(Math.max(h+(y2-y1), 20), mh-y));
        }
      }
      // 多角形の場合
      if (comp_elem.attr('data-anno-type')=='polygon') {
        const points_ary = [...comp_elem.data('points')];
        const mx = x2 - x1;
        const my = y2 - y1;
        if (points_ary) {
          if (edge < 0) {
            const mw = parseInt(svg_elem.attr('width'));
            const mh = parseInt(svg_elem.attr('height'));
            let over = false;
            points_ary.forEach((point, i) => {
              if (point[0]+mx < 0 || point[0]+mx > mw || point[1]+my < 0 || point[1]+my > mh) {
                over = true;
              }
              points_ary[i] = [point[0]+mx, point[1]+my];
            });
            if (over) return;
            comp_elem.data('points', points_ary);
          } else {
            points_ary[edge] = [x2, y2];
          }
          comp_elem.attr('points', anno.join_points(points_ary));
        }
      }
      comp_elem.data('x1', x2);
      comp_elem.data('y1', y2);
      return false;
    }
    // マウスダウンしていない場合
    if (!svg_elem.data("down")) return;
    // 矩形ツールの場合
    if (anno.tool.bbox) {
      let comp = svg_elem.data("lastcomp");
      const x1 = svg_elem.data("x1");
      const y1 = svg_elem.data("y1");
      const x2 = ~~(event.offsetX / anno.canvas_scale);
      const y2 = ~~(event.offsetY / anno.canvas_scale);
      svg_elem.data("x2", x2);
      svg_elem.data("y2", y2);
      if (comp) comp.remove();
      comp = anno.make_rect_dom(x1, y1, x2, y2, `#${anno.tool.color}`, '#ffffff', 2, anno.tool.label);
      if (comp) {
        svg.appendChild(comp);
        svg_elem.data("lastcomp", comp);
      }
    }
    // 多角形ツールの場合
    if (anno.tool.polygon) {
      mk_poly(svg, svg_elem, event, false);
    }
    return false;
  };
  // キャンバス上でマウスを離したとき、矩形を確定
  svg.onmouseup = (event) => {
    //event.stopPropagation();
    // 左クリック以外の場合
    if (event.which != 1) return false;
    // カーソルツールの場合
    if (anno.tool.cursor) return false;
    // 矩形ツールの場合
    if (anno.tool.bbox) {
      anno.clear_svg_data(svg_elem);
      anno.load_annolist(svg_elem);
    }
    // 矩形ツールの場合
    if (anno.tool.polygon) {
      anno.load_annolist(svg_elem);
    }
    return false;
  };
};
/**
 * アノテーション作業中のデータをクリアする
 * @param {$} svg_elem SVG要素
 **/
anno.clear_svg_data = (svg_elem) => {
  // 多角形ツールの場合
  if (anno.tool.polygon) {
    const comp = svg_elem.data("lastcomp");
    if (comp) {
      // 最後の点を削除
      let points_ary = svg_elem.data("points");
      const comp_elem = $(comp);
      if (points_ary && points_ary.length > 3) {
        points_ary = points_ary.slice(0, -1);
        comp_elem.attr('points', anno.join_points(points_ary));
      } else {
        // 3点以下の場合は要素を削除
        comp_elem.remove();
      }
    };
    anno.load_annolist(svg_elem);
  }
  svg_elem.data({
    "down": false,
    "lastcomp": null,
    "x1": null,
    "y1": null,
    "x2": null,
    "y2": null,
    "points": null
  });
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
  rect.setAttribute('id', cmdbox.randam_string(16));
  rect.setAttribute('x', Math.min(x1, x2));
  rect.setAttribute('y', Math.min(y1, y2));
  rect.setAttribute('width', w);
  rect.setAttribute('height', h);
  rect.setAttribute('fill', `${fill}`);
  rect.setAttribute('stroke', `${stroke}`);
  rect.setAttribute('stroke-width', `${stroke_width}`);
  rect.setAttribute('fill-opacity', `0.5`);
  rect.setAttribute('data-anno-label', `${label}`);
  rect.setAttribute('data-anno-type', `rect`);
  return rect;
};
/**
 * 複数の線を結ぶ直線のDOMを作成
 * @param {string} points_str 点の文字列
 * @param {string} stroke 線の色
 * @param {string} fill 塗りつぶしの色
 * @param {number} stroke_width 線の太さ
 * @param {string} label ラベル
 * @return {Element} 直線のDOM
 **/
anno.make_polylines_dom = (points_str, stroke, fill, stroke_width, label) => {
  const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  polyline.setAttribute('id', cmdbox.randam_string(16));
  polyline.setAttribute('points', points_str);
  polyline.setAttribute('fill', `${fill}`);
  polyline.setAttribute('stroke', `${stroke}`);
  polyline.setAttribute('stroke-width', `${stroke_width}`);
  polyline.setAttribute('fill-opacity', `0.5`);
  polyline.setAttribute('data-anno-label', `${label}`);
  polyline.setAttribute('data-anno-type', `polyline`);
  return polyline;
}
/**
 * 多角形のDOMを作成
 * @param {string} points_str 点の文字列
 * @param {string} stroke 線の色
 * @param {string} fill 塗りつぶしの色
 * @param {number} stroke_width 線の太さ
 * @param {string} label ラベル
 * @param {Element} lastcomp 直前のアノテーション
 * @return {Element} 多角形のDOM
 **/
anno.make_polygon_dom = (points_str, stroke, fill, stroke_width, label, lastcomp=undefined) => {
  const polygon = !lastcomp ? document.createElementNS("http://www.w3.org/2000/svg", "polygon") : lastcomp;
  if (!lastcomp) polygon.setAttribute('id', cmdbox.randam_string(16));
  polygon.setAttribute('points', points_str);
  polygon.setAttribute('fill', `${fill}`);
  polygon.setAttribute('stroke', `${stroke}`);
  polygon.setAttribute('stroke-width', `${stroke_width}`);
  polygon.setAttribute('fill-opacity', `0.5`);
  polygon.setAttribute('data-anno-label', `${label}`);
  polygon.setAttribute('data-anno-type', `polygon`);
  return polygon;
};
/**
 * 点の文字列を配列に変換
 * @param {string} points_str 点の文字列
 * @return {Array} 点の配列
 * @example
 * anno.parse_points('0,0 100,0 100,100 0,100');
 * // => [[0,0],[100,0],[100,100],[0,100]]
 **/
anno.parse_points = (points_str) => {
  try {
    const points = points_str.split(' ');
    const points_ary = [];
    points.forEach((point) => {
      const xy = point.split(',');
      points_ary.push([parseInt(xy[0].trim()), parseInt(xy[1].trim())]);
    });
    return points_ary;
  } catch(e) {
    return [];
  }
};
/**
 * 点の配列を文字列に変換
 * @param {Array} points_ary 点の配列
 * @return {string} 点の文字列
 * @example
 * anno.join_points([[0,0],[100,0],[100,100],[0,100]]);
 * // => '0,0 100,0 100,100 0,100'
 **/
anno.join_points = (points_ary) => {
  try {
    let points_str = '';
    points_ary.forEach((point) => {
      points_str += `${point[0]},${point[1]} `;
    });
    return points_str.trim();
  } catch(e) {
    return '';
  }
};
/**
 * コンポーネントの選択状態を解除
 **/
anno.blur_comp = (svg_elem) => {
  anno.canvas_container.find('.anno-list').find(`a`).css('background-color', '');
  svg_elem = svg_elem ? svg_elem : anno.canvas_container.find('#svg');
  svg_elem.find('[stroke-width]').attr('stroke-width', '2');
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
      "x": event.clientX,
      "y": event.clientY,
      "startleft": target_elem.data("sl"),//ドラッグ開始時点の位置
      "starttop": target_elem.data("st"),
    });
    return false;
  };
  target.onmousemove = (event) => {
    if (!target_elem.data("down")) return;
    if (event.which != 3) return false;
    event.stopPropagation();
    let move_x = target_elem.data("x") - event.clientX;
    let move_y = target_elem.data("y") - event.clientY;
    move_x = target_elem.data("startleft") - move_x;
    move_y = target_elem.data("starttop") - move_y;
    //move_x = move_x<0 ? 0 : move_x;
    //move_y = move_y<0 ? 0 : move_y;
    target_elem.css('left', `${move_x}px`).data("sl", move_x);
    target_elem.css('top', `${move_y}px`).data("st", move_y);
    anno.canvas_orgLeft = move_x;
    anno.canvas_orgTop = move_y;
    return false;
  };
  target.onmouseup = (event) => {
    if (event.which != 3) return false;
    event.stopPropagation();
    target_elem.data({
      "down": false,
      "x": null,
      "y": null,
    });
    return false;
  };
};
anno.load_annoall_coco = (menu_elem) => {
  const load_type = menu_elem.attr('data-load-type');
  const load_src = menu_elem.attr('data-load-src');
  const deploy_dir = anno.left_container.find('.deploy_names').val();
  const conf = anno.tool.conf;
  const load_path = menu_elem.attr('data-load-path');
  const load_input_path = menu_elem.attr('data-load-input-path');
  if (!load_type || !load_path || !load_input_path || !conf) {
    cmdbox.message('Annotation import error.');
    return;
  }
  if (!window.confirm('Caution!!: Please check the following points.\n'
    +`This operation generates an SVG file based on the annotation data in the “${load_path}” file.\n`
    +'The SVG file records the result of annotating the image.\n'
    +'If an SVG file with the same name already exists, it will be overwritten.\n'
    +'\nShall we continue?')) return;
  cmdbox.show_loading();
  cmdbox.progress(0, 1, 0, `Loading “${load_path}” file.`, true, true);
  cmdbox.file_download(anno.left_container, load_path).then(async res => {
    if (!res) {
      cmdbox.hide_loading();
      return;
    }
    const anno_json = JSON.parse(atob(res['data']));
    const labels = anno_json['categories'];
    const images = anno_json['images'];
    const annotaions = anno_json['annotations'];

    // ラベル＆カラーの再読み込み
    const colors = anno.get_tool_colors();
    const tags_labels_elem = anno.canvas_container.find('#tags_labels');
    tags_labels_elem.children('.dropdown-labels').remove();
    for (let i=0; i<labels.length; i++) {
      if (i >= colors.length) colors.push(cmdbox.randam_color());
      anno.add_label(labels[i]['name'], colors[i], tags_labels_elem);
    }
    anno.canvas_container.find('#tags_labels').find('.dropdown-item:first').click();
    // 画像ファイルの存在チェック
    for(let i=0; i<images.length; i++) {
      const img = images[i];
      cmdbox.show_loading();
      cmdbox.progress(0, images.length, i, `Check image “${img['file_name']}” file.`, true, false);
      const res = await cmdbox.file_list(anno.left_container, `${load_input_path}/${img['file_name']}`);
      if (!res) return;
    }
    cmdbox.show_loading();
    // アノテーションファイル内に定義されている画像単位で処理
    let cnt = 0;
    for(const img of images) {
      // 画像に設定されているアノテーションリストを取得
      const annos = annotaions.filter(row => row['image_id']==img['id']);
      if (annos.length <= 0) continue;
      // アノテーションリストからSVGエレメントを作成
      $('#anno_svg').remove();
      const svg_elem = $(`<svg id="anno_svg" xmlns="http://www.w3.org/2000/svg" width="${img['width']}" height="${img['height']}" viewBox="0 0 ${img['width']} ${img['height']}"/>`);
      for(const anno_obj of annos) {
        const label = labels.find(row => row['id']==anno_obj['category_id']);
        const color = colors[labels.indexOf(label)];
        const bbox = anno_obj['bbox'];
        const segs = anno_obj['segmentation'];
        // segの場合
        if (segs && segs.length > 0) {
          const points = [];
          for (const seg of segs) {
            for (let j=0; j<seg.length; j+=2) points.push([seg[j], seg[j+1]]);
          }
          const comp = anno.make_polylines_dom(anno.join_points(points), `#${color}`, '#ffffff', 2, label['name']);
          svg_elem.append($(comp));
        }
        // bboxの場合
        else if (bbox && bbox.length >= 4) {
          const comp = anno.make_rect_dom(bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3], `#${color}`, '#ffffff', 2, label['name']);
          svg_elem.append($(comp));
        }
      }
      cmdbox.show_loading();
      anno.save_anno(deploy_dir, `${load_input_path}/${img['file_name']}`, svg_elem, true, (svg_path) => {
        cmdbox.progress(0, images.length, ++cnt, `Generate and save svg file. “${svg_path}”.`, true, false);
        if(cnt >= images.length) {
          cmdbox.hide_loading();
          cmdbox.message(`Import complate. load_path=${load_path}, last_save_svg=${svg_path}`);
          const current_ul_elem = anno.left_container.find('.tree-menu');
          anno.clear_canvas();
          anno.load_filelist(load_input_path, load_src, current_ul_elem);
        }
      });
    }
  });
};
/**
 * 選択中のフォルダ内のSVGファイルを元にアノテーションファイルを生成して保存
 * @param {$} menu_elem メニュー要素
 **/
anno.save_annoall_coco = (menu_elem) => {
  const save_type = menu_elem.attr('data-save-type');
  const save_src = menu_elem.attr('data-save-src');
  const deploy_dir = anno.left_container.find('.deploy_names').val();
  const conf = anno.tool.conf;
  if (!save_type || !save_src || !conf) {
    cmdbox.message('Annotation export error.');
    return;
  }
  const save_path = menu_elem.attr('data-save-path').replace(deploy_dir, '');
  const labels = anno.get_tool_labels();
  if (labels.length <= 0) {
    cmdbox.message('The label is not set.');
    return;
  }
  if (!window.confirm('Caution!!: Please check the following points.\n'
                    +'1.Save the label before performing this operation.\n'
                    +'2.Save the annotation before performing this operation.\n'
                    +'3.If an annotation file has already been saved, it will be overwritten.\n'
                    +'\nShall we continue?')) return;
  cmdbox.progress(0, 1, 0, 'Loading file list..', true, true);
  cmdbox.file_list(anno.left_container, save_src).then(res => {
    if(!res) {
      cmdbox.hide_loading();
      return;
    }
    const opt = cmdbox.get_server_opt(false, anno.left_container);
    const file_list = Object.entries(res).sort();
    file_list.forEach(async ([key, node]) => {
      if(!node['path']) return;
      if(!node['path'].startsWith(save_src)) return;
      if(!node['children']) return;
      const coco = {};
      coco['info'] = {
        "description": `Dataset from "${node['path']}"`,
        "url": window.location.href,
        "version": "1.0",
        "year": new Date().getFullYear(),
        "contributor": `${$('.copyright').text()}`,
        "date_created": cmdbox.toDateStr(new Date()),
      };
      coco['licenses'] = [{
        "id": 0,
        "name": "Unknown",
        "url": ""
      }];
      coco['categories'] = labels.map((label, i) => {
        return {
          "id": i,
          "name": label,
          "supercategory": ""
        };
      });
      coco['images'] = [];
      coco['annotations'] = [];

      // 選択中のディレクトリ内のファイル一覧からSVGファイルを取得
      const children = Object.entries(node['children']);
      if (children.length <= 0) {
        cmdbox.hide_loading();
        cmdbox.message('Not found SVG files.');
        return;
      }
      let progress_max = children.length;
      let progress_count = 0;
      const progress_text = `Loading SVG files..`;
      cmdbox.progress(0, progress_max, progress_count, progress_text, true, false);
      for (const [k, n] of children) {
        progress_count++;
        cmdbox.progress(0, progress_max, progress_count, progress_text, true, false);
        if(n['is_dir']) return;
        if(!n['path'].endsWith('.svg')) continue;
        // SVGファイルの読込
        const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${n['path']}\t${opt['scope']}\t0.0`);
        const svg_str = await (await fetch(`annotation/get_img/${constr}?r=${cmdbox.randam_string(8)}`)).text();
        const svg_elem = $(svg_str);
        // 画像情報を取得
        const img_id = coco['images'].length;
        coco['images'].push({
          "id": img_id,
          "file_name": `${node['name']}/${n['name'].replace(/\.svg$/, '')}`,
          "height": parseInt(svg_elem.attr('height')),
          "width": parseInt(svg_elem.attr('width')),
          "license": 0,
          "flickr_url": "",
          "coco_url": "",
          "date_captured": n['last']
        });
        // svgからcoco形式のアノテーションを取得
        svg_elem.children().each((i, comp) => {
          const comp_elem = $(comp);
          const cate_id = labels.indexOf(comp_elem.attr('data-anno-label'));
          // 矩形の場合
          if (comp_elem.attr('data-anno-type')=='rect') {
            const x = parseInt(comp_elem.attr('x'));
            const y = parseInt(comp_elem.attr('y'));
            const w = parseInt(comp_elem.attr('width'));
            const h = parseInt(comp_elem.attr('height'));
            coco['annotations'].push({
              "id": coco['annotations'].length,
              "image_id": img_id,
              "category_id": cate_id,
              "segmentation": [],
              "bbox": [x, y, w, h],
              "area": w * h,
              "iscrowd": 0
            });
          }
          // 多角形の場合
          if (comp_elem.attr('data-anno-type')=='polygon') {
            const points_ary = anno.parse_points(comp_elem.attr('points'));
            const x_ary = points_ary.map((point) => point[0]);
            const y_ary = points_ary.map((point) => point[1]);
            const x = Math.min(...x_ary);
            const y = Math.min(...y_ary);
            const w = Math.max(...x_ary) - x;
            const h = Math.max(...y_ary) - y;
            coco['annotations'].push({
              "id": coco['annotations'].length,
              "image_id": img_id,
              "category_id": cate_id,
              "segmentation": [points_ary.flat()],
              "bbox": [x, y, w, h],
              "area": w * h,
              "iscrowd": 0
            });
          }
        });
        svg_elem.remove();
      }
      if (coco['annotations'].length > 0) {
        cmdbox.progress(0, 1, 0, `Writing annotation file. ${save_path}`, true, true);
        // cocoファイルの保存
        const formData = new FormData();
        formData.append('files', new Blob([JSON.stringify(coco)], {type:"application/json"}), save_path);
        cmdbox.file_upload(anno.left_container, deploy_dir, formData, orverwrite=true, progress_func=(e) => {}, success_func=(target, svpath, data) => {
          cmdbox.hide_loading();
          cmdbox.message(`Saved in. save_path=${deploy_dir}${save_path}`);
        }, error_func=(target, svpath, data) => {
          cmdbox.hide_loading();
        });
      } else {
        cmdbox.hide_loading();
        cmdbox.message('Not found annotation data.');
      }
    });
  });
};
/**
 * 選択中のフォルダ内のSVGファイルを元にアノテーションファイルを生成して保存
 * @param {$} menu_elem メニュー要素
 **/
anno.save_annoall_cityscapes = (menu_elem) => {
  const save_type = menu_elem.attr('data-save-type');
  const save_src = menu_elem.attr('data-save-src');
  const save_path = menu_elem.attr('data-save-path');
  const deploy_dir = anno.left_container.find('.deploy_names').val();
  const conf = anno.tool.conf;
  if (!save_type || !save_src || !conf) {
    cmdbox.message('Annotation save error.');
    return;
  }
  const labels = anno.get_tool_labels();
  if (labels.length <= 0) {
    cmdbox.message('The label is not set.');
    return;
  }
  if (!window.confirm('Caution:\n'
                    +'1.Save the label before performing this operation.\n'
                    +'2.Save the annotation before performing this operation.\n'
                    +'3.If an annotation file has already been saved, it will be overwritten.\n'
                    +'\nShall we continue?')) return;

  cmdbox.show_loading();
  cmdbox.progress(0, 1, 0, 'Cleaning workdir..', true, true);
  // 既存の作業ディレクトリを削除
  cmdbox.file_rmdir(anno.left_container, save_path.replace(/\.zip$/, ''), (res) => {}).then(res => {
    cmdbox.progress(0, 1, 0, 'Loading file list..', true, true);
    cmdbox.file_list(anno.left_container, save_src).then(res => {
      return Object.entries(res).sort();
    }).then(file_list => {
      //const sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
      //anno.promises.push(sleep(15*1000));
      const opt = cmdbox.get_server_opt(false, anno.left_container);
      const promises = [];
      const archive_file_list = [];
      file_list.forEach(([key, node]) => {
        if(!node['path']) return;
        if(!node['path'].startsWith(save_src)) return;
        if(!node['children']) return;
        const children = Object.entries(node['children']);
        let progress_max = children.length;
        let progress_count = 0;
        children.forEach(([k, n]) => {
          progress_count++;
          cmdbox.progress(0, progress_max, progress_count, 'Loading SVG files..', true, false);
          if(!n['is_dir']) return;
          const subset = n['name'];
          // 二階層目（train, val, test）のディレクトリ内を取得
          const prom = cmdbox.file_list(anno.left_container, n['path']).then(async res => {
            const file_list = Object.entries(res).sort();
            progress_max += file_list.length;
            for (const [key, node] of file_list) {
              progress_count++;
              cmdbox.progress(0, progress_max, progress_count, 'Loading SVG files..', true, false);
              if(!node['path']) continue;
              if(!node['path'].startsWith(save_src)) continue;
              if(!node['children']) continue;
              // ファイル一覧からSVGファイルを取得
              const children = Object.entries(node['children']);
              if (children.length <= 0) continue;
              progress_max += children.length;
              for (const [k, n] of children) {
                progress_count++;
                cmdbox.progress(0, progress_max, progress_count, 'Generating mask images..', true, false);
                if(n['is_dir']) continue;
                if(!n['mime_type'].startsWith('image')) continue;
                if(!n['path'].endsWith('.svg')) {
                  // SVG以外の画像ファイルの場合はコピー
                  const to_ext = n['name'].split('.').pop();
                  const to_path = save_path.replace(/\.zip$/, `/images/${subset}/${subset}_${n['name'].replace(/\.[^\.]+$/, '_leftImg8bit')}.${to_ext}`);
                  cmdbox.progress(0, progress_max, progress_count, 'Copy work image..', true, false);
                  await cmdbox.file_copy(anno.left_container, n['path'], to_path, orverwrite=true);
                  archive_file_list.push(to_path);
                  continue;
                }
                // SVGファイルの読込
                const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${n['path']}\t${opt['scope']}\t0.0`);
                cmdbox.progress(0, progress_max, progress_count, 'Loading SVG files..', true, false);
                const res = await fetch(`annotation/get_img/${constr}?r=${cmdbox.randam_string(8)}`);
                const svg_str = await res.text();
                const svg_elem = $(svg_str);
                // SVGからPNGを生成
                svg_elem.attr('id', null);
                svg_elem.attr('stroke-width', '2.0');
                svg_elem.children().each((i, comp) => {
                  const comp_elem = $(comp);
                  const index = labels.indexOf(comp_elem.attr('data-anno-label'));
                  const color = cmdbox.make_color4id(index); // ラベルに対応する色を取得
                  comp_elem.attr('stroke', `#${color}`);
                  comp_elem.attr('stroke-width', `2.0`);
                  comp_elem.attr('fill', `#${color}`);
                  comp_elem.attr('fill-opacity', `1`);
                });
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.width = parseInt(svg_elem.attr('width'));
                canvas.height = parseInt(svg_elem.attr('height'));
                // SVGを同期的に読込む
                cmdbox.progress(0, progress_max, progress_count, 'Generating mask images..', true, false);
                const img = await cmdbox.load_img_sync('data:image/svg+xml;charset=utf-8;base64,' + btoa(svg_elem.prop('outerHTML')));
                svg_elem.remove();
                context.drawImage(img, 0, 0, canvas.width, canvas.height);
                // canvasからblobを生成
                canvas.toBlob(async (blob) => {
                  const formData = new FormData();
                  const upload_path = save_path.replace(/\.zip$/, `/annotations/${subset}/${subset}_${n['name'].replace(/\.svg$/, '_gtFine_labelIds.png')}`);
                  formData.append('files', blob, upload_path.replace(save_src, ''));
                  archive_file_list.push(upload_path);
                  // 生成したpng画像をアップロード
                  cmdbox.progress(0, progress_max, progress_count, 'Writing mask images..', true, false);
                  cmdbox.file_upload(anno.left_container, save_src, formData, orverwrite=true, progress_func=(e) => {
                  }, success_func=(target, svpath, data) => {
                    $(canvas).remove();
                  }, error_func=(target, svpath, data) => {
                    $(canvas).remove();
                  }, async_fg=false);
                }, 'image/png');
              }
            }
          });
          promises.push(prom);
        });
      });
      Promise.all(promises).then(() => {
        const opt = cmdbox.get_server_opt(false, anno.left_container);
        const thum_size = 0.0;
        const constr = btoa(`${opt['host']}\t${opt['port']}\t${opt['svname']}\t${opt['password']}\t${save_path}\t${opt['scope']}\t${thum_size}`);
        cmdbox.progress(0, 1, 0, 'Archiving mask images..', true, true);
        fetch(`annotation/archive/${constr}`, {
          method:"POST",
          body:JSON.stringify(archive_file_list),
          headers:{"Content-Type":"application/json"}
        }).then(res => {
          cmdbox.progress(0, 1, 0, 'Cleaning mask images..', true, true);
          const rmdir_path = save_path.replace(/\.zip$/, '');
          cmdbox.file_rmdir(anno.left_container, rmdir_path, (res) => {
            //cmdbox.message(`Failed remove mask images. ${rmdir_path}`);
          }).then(res => {
            cmdbox.hide_loading();
            cmdbox.message(`Saved complate. ${save_path}`);
          }).finally(() => {
            cmdbox.hide_loading();
          });
        });
      });
    });
  });
};
anno.tool = {};
/**
 * ツールの初期化
 **/
anno.init_tool_button = () => {
  const toggle_func = (elem) => {
    anno.canvas_container.find('.tool_bot').removeClass('active');
    anno.blur_comp();
    $(elem).addClass('active');
  }
  // 選択ツール
  anno.canvas_container.find('.tool_bot_cursor').off('click').on('click', () => {
    anno.tool.cursor = true;
    anno.tool.bbox = false;
    anno.tool.polygon = false;
    toggle_func('.tool_bot_cursor');
  });
  anno.canvas_container.find('.tool_bot_cursor').click();
  // 矩形ツール
  anno.canvas_container.find('.tool_bot_bbox').off('click').on('click', () => {
    if (anno.canvas_container.find('.tag_label').text() == '') return;
    anno.tool.cursor = false;
    anno.tool.bbox = true;
    anno.tool.polygon = false;
    toggle_func('.tool_bot_bbox');
  });
  // 多角形ツール
  anno.canvas_container.find('.tool_bot_polygon').off('click').on('click', () => {
    if (anno.canvas_container.find('.tag_label').text() == '') return;
    anno.tool.cursor = false;
    anno.tool.bbox = false;
    anno.tool.polygon = true;
    toggle_func('.tool_bot_polygon');
  });
  // ラベル再読み込みツール
  anno.canvas_container.find('.tool_bot_reload').off('click').on('click', () => {
    const svpath = anno.left_container.find('.deploy_names').val();
    const conf = anno.tool.conf;
    if (conf['label_file'] && conf['deploy_dir']){
      const label_file = conf['label_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
      anno.load_label(`${svpath}${label_file}`);
    }
    if (conf['color_file'] && conf['deploy_dir']){
      const color_file = conf['color_file'].replace(conf['deploy_dir'], '').replace(/\\/, '/');
      anno.load_color(`${svpath}${color_file}`);
    }
  });
  // ラベル保存ツール
  anno.canvas_container.find('.tool_bot_save').off('click').on('click', () => {
    const svpath = anno.left_container.find('.deploy_names').val();
    if (!svpath) return;
    anno.save_label_color(svpath);
  });
  // 画像前へツール
  anno.canvas_container.find('.tool_bot_imgprev').off('click').on('click', () => {
    const cimg_elem = anno.left_container.find('.file-list .card-selected');
    const simg_elem = anno.left_container.find('.file-list .card-thumbnail');
    simg_elem.each((i, elem) => {
      const cdata_path = cimg_elem.attr('data-path');
      const sdata_path = $(elem).attr('data-path');
      if (sdata_path == cdata_path || sdata_path+'.svg' == cdata_path) {
        if (i > 0) {
          const prev_elem = $(simg_elem[i-1]);
          prev_elem.click();
        }
      }
    });
  });
  // 画像次へツール
  anno.canvas_container.find('.tool_bot_imgnext').off('click').on('click', () => {
    const cimg_elem = anno.left_container.find('.file-list .card-selected');
    const simg_elem = anno.left_container.find('.file-list .card-thumbnail');
    simg_elem.each((i, elem) => {
      const cdata_path = cimg_elem.attr('data-path');
      const sdata_path = $(elem).attr('data-path');
      if (sdata_path == cdata_path || sdata_path+'.svg' == cdata_path) {
        if (i < simg_elem.length-1) {
          const next_elem = $(simg_elem[i+1]);
          next_elem.click();
        }
      }
    });
  });
  // アノテーション再読み込みツール
  anno.canvas_container.find('.tool_bot_annoreload').off('click').on('click', () => {
    const img_elem = anno.canvas_container.find('#canvas .canvas_image');
    const node = img_elem.data('node');
    const opt = img_elem.data('opt');
    if (!node || !opt) return;
    anno.load_image(node, opt);
  });
  // アノテーション保存ツール
  anno.canvas_container.find('.tool_bot_annosave').off('click').on('click', () => {
    const svpath = anno.left_container.find('.deploy_names').val();
    const image_path = anno.canvas_container.find('.image_address').val();
    if (!svpath || !image_path) return;
    anno.save_anno(svpath, image_path, anno.canvas_container.find('#canvas svg'));
  });
  // キーボード操作
  document.onkeydown = (event) => {
    const svg_elem = anno.canvas_container.find('#canvas svg');
    if (event.key == 'Delete') {
      const comp = svg_elem.data('selectcomp');
      if(comp) comp.remove();
      anno.load_annolist(svg_elem);
    }
    if (event.key == 'Escape') {
      anno.clear_svg_data(svg_elem);
    }
  };
};
/**
 * ページ読み込み時の処理
 */
anno.onload = () => {
  cmdbox.show_loading();
  cmdbox.get_server_opt(true, anno.left_container).then((opt) => {
    cmdbox.load_server_list(anno.left_container, (opt) => anno.deploy_list(), true, false);
  });
  anno.init_tool_button();
};
