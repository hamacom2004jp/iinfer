// ファイラーモーダル
filer_modal_func = async (target_id, modal_title, current_path, call_back_func) => {
    const filer_modal = $('#filer_modal');
    filer_modal.find('.modal-title').text(modal_title);
    filer_modal.find('.modal-body').html('<ul class="tree-menu overflow-auto border col-4"></ul><div class="file-list overflow-auto col-8"></div>');
    filer_modal.find('.tree-menu').css('height', 'calc(100vh - 180px)');
    filer_modal.find('.file-list').css('height', 'calc(100vh - 180px)');
    //filer_modal.find('.tree-menu').resizable({ghost:true});
    filer_modal.find('.filer_address_bot').off('click').on('click', async () => {
        const c_path = filer_modal.find('.filer_address').val();
        const key = c_path.replace(/[\s\:\\\/\,\.\#\$\%\^\&\!\@\*\(\)\{\}\[\]\'\"\`]/g, `_`);
        const current_node = $(`#${key}`);
        if (current_node.length <= 0) {
            alert(`invalid path:${key}`);
            return;
        }
        await reload_tree(target_id, filer_modal.find('.tree-menu'), c_path, filer_modal.find('.file-list'));
    });

    const reload_tree = async (target_id, current_node, current_path, file_list_elem) => {
        //dict(name=part, is_dir=path.is_dir(), path=str(path), children=children)
        const py_list_tree = await list_tree(current_path);
        current_node.html('');
        Object.entries(py_list_tree).forEach(([key, node]) => {
            if(!node['is_dir']) return;
            let li_elem = $(`#${key}`);
            const font_color = "color:rgba(var(--bs-link-color-rgb),var(--bs-link-opacity,1));font-size:initial;";
            if (li_elem.length > 0) {
                li_elem.html(`<a href="#" class="folder-open" style="${font_color}">${node['name']}</a>`);
            } else {
                li_elem = $(`<li id="${key}"><a href="#" class="folder-open" style="${font_color}">${node['name']}</a></li>`);
                current_node.append(li_elem);
            }
            const mk_func = (target_id, current_node, current_path) => {
                // 左側ペインのフォルダを選択した時の処理
                return () => reload_tree(target_id, current_node, current_path);
            }
            li_elem.find('a').off('click').on('click', mk_func(target_id, current_node, node['path']));
            if(node['children']) {
                const ul_elem = $('<ul/>');
                li_elem.append(ul_elem);
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(!n['is_dir']) return;
                    const li = $(`<li id="${k}"><a href="#" class="folder-close" style="${font_color}">${n['name']}</a></li>`);
                    li.find('a').click(mk_func(target_id, ul_elem, n['path']));
                    ul_elem.append(li);
                });
            }
        });
        const py_list_tree_keys = Object.keys(py_list_tree);
        if (py_list_tree_keys.length > 0) {
            const node = py_list_tree[py_list_tree_keys[py_list_tree_keys.length-1]];
            const table = $('<table class="table table-bordered table-hover table-sm"></table>');
            filer_modal.find('.file-list').html('');
            filer_modal.find('.file-list').append(table);
            const table_head = $('<thead></thead>');
            table_head.append($('<tr><th scope="col">-</th><th scope="col">name</th><th scope="col">size</th><th scope="col">last</th></tr>'));
            table.append(table_head);
            const table_body = $('<tbody></tbody>');
            table.append(table_body);
            filer_modal.find('.filer_address').val(node['path']);
            if(node['children']) {
                const mk_file_func = (target_id, current_node, current_path) => {
                    // 右側ペインのフォルダを選択した時の処理
                    return () => reload_tree(target_id, current_node, current_path);
                }
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(!n['is_dir']) return;
                    const tr_elem = $('<tr/>');
                    table_body.append(tr_elem);
                    const td = $(`<td><a href="#" class="folder-close">${n['name']}</a></td>`);
                    td.find('a').click(mk_file_func(target_id, $(`#${k}`), n['path']));
                    tr_elem.append($('<td><img src="assets/tree-menu/image/folder-close.png"></td>'));
                    tr_elem.append(td);
                    tr_elem.append($(`<td>${n['size']}</td>`));
                    tr_elem.append($(`<td>${n['last']}</td>`));
                });
                const mk_dir_func = (target_id, current_node, current_path) => {
                    // 右側ペインのファイルを選択した時の処理
                    return () => {
                        $(`[id="${target_id}"]`).val(current_path);
                        filer_modal.modal('hide');
                        if(call_back_func) call_back_func(current_path);
                    }
                }
                Object.entries(node['children']).forEach(([k, n]) => {
                    if(n['is_dir']) return;
                    const tr_elem = $('<tr/>');
                    table_body.append(tr_elem);
                    const td = $(`<td><a href="#" class="folder-close">${n['name']}</a></td>`);
                    td.find('a').click(mk_dir_func(target_id, $(`#${k}`), n['path']));
                    tr_elem.append($('<td><img src="/assets/tree-menu/image/file.png"></td>'));
                    tr_elem.append(td);
                    tr_elem.append($(`<td>${n['size']}</td>`));
                    tr_elem.append($(`<td>${n['last']}</td>`));
                });
            }
        }
    }
    await reload_tree(target_id, filer_modal.find('.tree-menu'), current_path, filer_modal.find('.file-list'));
    filer_modal.modal('show');
};

const list_tree = async (current_path) => {
    const formData = new FormData();
    formData.append('current_path', current_path);
    const res = await fetch('gui/list_tree', {method: 'POST', body: formData});
    return await res.json();
}