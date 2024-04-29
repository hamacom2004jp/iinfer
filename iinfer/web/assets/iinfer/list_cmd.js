// 保存済みコマンドファイル一覧の取得
list_cmd_func = async () => {
    $('#cmd_items').html('');
    kwd = $('#cmd_kwd').val();
    py_list_cmd = await eel.list_cmd(kwd?`*${kwd}*`:'*')();
    $.each(py_list_cmd, (i, row) => {
        elem = $($('#cmd_template').html());
        elem.find('.cmd_title').text(row['title']);
        elem.find('.cmd_mode').text(row['mode']);
        elem.find('.cmd_cmd').text(row['cmd']);
        $('#cmd_items').append(elem);
    });
    $('#cmd_items').append($($('#cmd_add').html()));
}
// コマンドファイルの取得が出来た時の処理
list_cmd_func_then = () => {
    // 配列をoptionタグに変換
    mkopt = (arr) => {
        var opt = '';
        for (var i = 0; arr && i < arr.length; i++) {
            opt += `<option value="${arr[i]}">${arr[i]}</option>`;
        }
        return opt;
    }
    // コマンドカードクリック時の処理（モーダルダイアログを開く）
    cmd_card_func = async (e) => {
        py_get_mode_opt = await eel.get_mode_opt()();
        cmd_modal = $('#cmd_modal');
        cmd_modal.find('[name="mode"]').html(mkopt(py_get_mode_opt));
        // モード変更時の処理（モードに対するコマンド一覧を取得）
        mode_change = async () => {
            mode = cmd_modal.find('[name="mode"]').val();
            py_get_cmd_opt = await eel.get_cmd_opt(mode)();
            cmd_modal.find('[name="cmd"]').html(mkopt(py_get_cmd_opt));
        }
        cmd_modal.find('[name="mode"]').off('change');
        cmd_modal.find('[name="mode"]').change(mode_change);
        cmd_modal.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
        row_content = cmd_modal.find('.row_content');
        row_content.html('');
        // コマンド変更時の処理（コマンドに対するオプション一覧を取得）
        cmd_change = async () => {
            mode = cmd_modal.find('[name="mode"]').val();
            cmd = cmd_modal.find('[name="cmd"]').val();
            py_get_opt_opt = await eel.get_opt_opt(mode, cmd)();
            row_content.html('');
            // オプション一覧をフォームに追加
            add_form_func = (i, row, next_elem) => {
                target_name = row['opt'];
                if(!row['choise']) {
                    elem = $(cmd_modal.find('.row_content_template_str').html());
                    if (next_elem) next_elem.after(elem);
                    else row_content.append(elem);
                    input_elem = elem.find('.row_content_template_input');
                    input_elem.removeClass('row_content_template_input');
                    input_elem.val(row['default']);
                }
                else {
                    elem = $(cmd_modal.find('.row_content_template_choice').html());
                    if (next_elem) next_elem.after(elem);
                    else row_content.append(elem);
                    input_elem = elem.find('.row_content_template_select');
                    input_elem.removeClass('row_content_template_select');
                    input_elem.html(mkopt(row['choise']));
                    input_elem.val(`${row['default']}`);
                }
                index = 0;
                if (cmd_modal.find(`[name="${target_name}"]`).length > 0) {
                    index = 0;
                    $.each(cmd_modal.find(`[name="${target_name}"][param_data_index]`), (i, val) => {
                        v = Number($(val).attr('param_data_index'));
                        if (index <= v) index = v + 1;
                    });
                }
                input_elem.attr('name', target_name);
                input_elem.attr('id', target_name + index);
                input_elem.attr('param_data_index', index);
                input_elem.attr('required', row['required']);
                input_elem.attr('param_data_type', row['type']);
                input_elem.attr('param_data_multi', row['multi']);
                // ファイルタイプの場合はファイラーモーダルを開くボタンを追加
                if(row['type']=='file'){
                    btn = $('<button class="btn btn-secondary" type="button">file</button>');
                    input_elem.parent().append(btn);
                    mk_func = (tid, tn) => {
                        // tid, tnの値を残すためにクロージャーにする
                        return () => {
                            current_path = $(`[id="${tid}"]`).val();
                            filer_modal_func(tid, tn, current_path);
                        }
                    }
                    btn.click(mk_func(input_elem.attr('id'), input_elem.attr('name')));
                }
                // マルチの場合は追加ボタンを追加
                if(row['multi']){
                    btn_a = $('<button class="btn btn-secondary add_buton" type="button"></button>');
                    btn_a.append('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus" viewBox="0 0 16 16">'
                                +'<path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>'
                                +'</svg>');
                    input_elem.parent().append(btn_a);
                    mk_func = (row, next_elem) => {
                        // row, next_elemの値を残すためにクロージャーにする
                        return () => {add_form_func(0, row, next_elem);}
                    }
                    btn_a.click(mk_func(row, input_elem.parent().parent()));
                    // 2個目以降は削除ボタンを追加
                    if (cmd_modal.find(`[name="${target_name}"]`).length > 1) {
                        mk_func = (del_elem, row) => {
                            // del_elemの値を残すためにクロージャーにする
                            return () => del_elem.remove();
                        }
                        btn_t = $('<button class="btn btn-secondary" type="button"></button>');
                        btn_t.append('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">'
                                +'<path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>'
                                +'<path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>'
                                +'</svg>');
                        input_elem.parent().append(btn_t);
                        btn_t.click(mk_func(input_elem.parent().parent(), row));
                    }
                }
                title = elem.find('.row_content_template_title');
                title.html('');
                if (row['required']) {
                    title.append('<span class="text-danger">*</span>');
                }
                title.append(`<span>${row['opt']}</span>`);
                if (row['hide']) {
                    elem.addClass('row_content_hide');
                } else {
                    title.addClass('text-decoration-underline');
                }
            }
            $.each(py_get_opt_opt, add_form_func);
            row_content.find('.row_content_hide').hide();
            // 高度なオプションを表示するリンクを追加
            if (row_content.children().is('.row_content_hide')) {
                show_link = $('<div class="text-center card-hover"><a href="#">[ advanced options ]</a></div>');
                show_link.click(() => row_content.find('.row_content_hide').toggle());
                row_content.append(show_link);
            }
        }
        //row_content.find('is-invalid, is-valid').removeClass('is-invalid').removeClass('is-valid');
        cmd_modal.find('[name="cmd"]').off('change');
        cmd_modal.find('[name="cmd"]').change(cmd_change);
        modal_title = $(e.currentTarget).find('.cmd_title').text();
        if(modal_title != '') {
            // コマンドファイルの読み込み
            py_load_cmd = await eel.load_cmd(modal_title)();
            cmd_modal.find('[name="mode"]').val(py_load_cmd['mode']);
            await mode_change();
            cmd_modal.find('[name="cmd"]').val(py_load_cmd['cmd']);
            await cmd_change();
            $.each(py_load_cmd, (key, val) => {
                if (typeof val === 'boolean') {
                    val = val.toString();
                }
                // フォームに値をセット
                if(Array.isArray(val)){
                    $.each(val, (i, v) => {
                        e = cmd_modal.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                        $(e).click();
                    });
                    cmd_modal.find(`[name="${key}"]`).each((i, e) => {
                        if (val[i] && val[i]!="" || i==0) $(e).val(val[i]);
                        else $(e).parent().parent().remove();
                    });
                } else {
                    cmd_modal.find(`[name="${key}"]`).val(val);
                }
            });
            $('#cmd_del').show();
            cmd_modal.find('[name="title"]').attr('readonly', true);
            cmd_modal.find('[name="mode"]').css('pointer-events', 'none').css('background-color', '#e9ecef');
            cmd_modal.find('[name="cmd"]').css('pointer-events', 'none').css('background-color', '#e9ecef');
            cmd_modal.find('[name="name"]').attr('readonly', true);
        } else {
            // 新規コマンドファイルの作成
            modal_title = 'New Command';
            await mode_change();
            $('#cmd_del').hide();
            cmd_modal.find('[name="title"]').val('');
            cmd_modal.find('[name="title"]').attr('readonly', false);
            cmd_modal.find('[name="mode"]').css('pointer-events', 'auto').css('background-color', 'transparent');
            cmd_modal.find('[name="cmd"]').css('pointer-events', 'auto').css('background-color', 'transparent');
            cmd_modal.find('[name="name"]').attr('readonly', false);
        }
        cmd_modal.find('.modal-title').text(`Command : ${modal_title}`);
        cmd_modal.find('.row_content_hide').hide();
        cmd_modal.modal('show');
    }
    $('.cmd_card').off('click').on('click', cmd_card_func);
    // コマンドフォームからパラメータを取得
    get_param = (modal_elem) => {
        modal_elem.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
        var opt = {};
        var title = modal_elem.find('[name="title"]').val();
        opt["mode"] = modal_elem.find('[name="mode"]').val();
        opt["cmd"] = modal_elem.find('[name="cmd"]').val();
        if(!opt["mode"]) delete opt["mode"];
        if(!opt["cmd"]) delete opt["cmd"];
        opt["title"] = title;
        isFloat = (i) => {
            try {
                n = Number(i);
                return n % 1 !== 0;
            } catch(e) {
                return false;
            }
        }
        isInt = (i) => {
            try {
                n = Number(i);
                return n % 1 === 0;
            } catch(e) {
                return false;
            }
        }
        // フォームの入力値をチェック（不正な値があればフォームに'is-invalid'クラスを付加する）
        modal_elem.find('.row_content, .row_content_common').find('input, select').each((i, elem) => {
            data_name = $(elem).attr('name');
            data_val = $(elem).val();
            data_type = $(elem).attr('param_data_type');
            data_multi = $(elem).attr('param_data_multi');
            if ($(elem).attr('required') && (!data_val || data_val=='')) {
                $(elem).addClass('is-invalid');
            } else if (data_type=='int') {
                if(data_val && data_val!='') {
                    if(!isInt(data_val)) $(elem).addClass('is-invalid');
                    else {
                        $(elem).removeClass('is-invalid');
                        $(elem).addClass('is-valid');
                        data_val = parseInt(data_val);
                    }
                } else {
                    $(elem).removeClass('is-invalid');
                    $(elem).addClass('is-valid');
                }
            } else if (data_type=='float') {
                if(data_val && data_val!='') {
                    if(!isFloat(data_val) && !isInt(data_val)) $(elem).addClass('is-invalid');
                    else {
                        $(elem).removeClass('is-invalid');
                        $(elem).addClass('is-valid');
                        data_val = parseFloat(data_val);
                    }
                } else {
                    $(elem).removeClass('is-invalid');
                    $(elem).addClass('is-valid');
                }
            } else if (data_type=='bool') {
                if(data_val!='true' && data_val!='false') $(elem).addClass('is-invalid');
                else {
                    data_val = data_val=='true';
                    $(elem).removeClass('is-invalid');
                    $(elem).addClass('is-valid');
                }
            } else {
                $(elem).removeClass('is-invalid');
                $(elem).addClass('is-valid');
            }
            if(data_multi=='true'){
                if(!opt[data_name]) opt[data_name] = [];
                if(data_val && data_val!='') opt[data_name].push(data_val);
                else if(data_val==false) opt[data_name].push(data_val);
            } else {
                if(data_val && data_val!='') opt[data_name] = data_val;
                else if(data_val==false) opt[data_name] = data_val;
            }
        });
        return [title, opt];
    }
    // コマンドファイルの保存
    $('#cmd_save').off('click').on('click', async () => {
        cmd_modal = $('#cmd_modal');
        var [title, opt] = get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        $('#loading').removeClass('d-none');
        result = await eel.save_cmd(title, opt)();
        await list_cmd_func();
        $('.cmd_card').off('click').on('click', cmd_card_func);
        if (result['success']) alert(result['success']);
        else if (result['warn']) alert(result['warn']);
        $('#loading').addClass('d-none');
    });
    // コマンドファイルの削除
    $('#cmd_del').off('click').on('click', async () => {
        cmd_modal = $('#cmd_modal');
        var title = cmd_modal.find('[name="title"]').val();
        $('#loading').removeClass('d-none');
        if (window.confirm(`delete "${title}"?`)) {
            await eel.del_cmd(title)();
            cmd_modal.modal('hide');
            await list_cmd_func();
            $('.cmd_card').off('click').on('click', cmd_card_func);
        }
        $('#loading').addClass('d-none');
    });
    // コマンドファイルの実行
    $('#cmd_exec').off('click').on('click', async () => {
        cmd_modal = $('#cmd_modal');
        var [title, opt] = get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        $('#loading').removeClass('d-none');
        // コマンドの実行
        eel.exec_cmd(title, opt)().then((result) => {});
    });
    // RAW表示の実行
    $('#cmd_raw').off('click').on('click', async () => {
        cmd_modal = $('#cmd_modal');
        var [title, opt] = get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        $('#loading').removeClass('d-none');
        // コマンドの実行
        eel.raw_cmd(title, opt)().then((result) => {
            view_raw_func(title, result);
            $('#loading').addClass('d-none');
        });
    });
};