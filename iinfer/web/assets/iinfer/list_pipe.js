// 保存済みパイプラインファイル一覧の取得
list_pipe_func = async () => {
    $('#pipe_items').html('');
    kwd = $('#pipe_kwd').val();
    py_list_pipe = await eel.list_pipe(kwd?`*${kwd}*`:'*')();
    $.each(py_list_pipe, (i, row) => {
        elem = $($('#pipe_template').html());
        elem.find('.pipe_title').text(row['title']);
        elem.find('.pipe_desc').text(row['description']);
        $('#pipe_items').append(elem);
    });
    $('#pipe_items').append($($('#pipe_add').html()));
}
list_pipe_func_then = () => {
    // パイプラインカードクリック時の処理（モーダルダイアログを開く）
    pipe_card_func = async (e) => {
        pipe_modal = $('#pipe_modal');
        pipe_modal.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
        row_content = pipe_modal.find('.row_content');
        row_content.html('');
        modal_title = $(e.currentTarget).find('.pipe_title').text();
        cmd_select_template_func = (add_buton, py_list_cmd) => {
            cmd_select_template = $(pipe_modal.find('.cmd_select_template').html());
            row_content = pipe_modal.find('.row_content');
            if(row_content.find('.cmd_select_item').length > 0) {
                add_buton.parents('.cmd_select_item').after(cmd_select_template);
            } else {
                row_content.append(cmd_select_template);
                cmd_select_template.find('[name="pipe_cmd"]').attr('required', true);
                cmd_select_template.find('.del_buton').hide();
            }
            pipe_cmd_select = cmd_select_template.find('[name="pipe_cmd"]');
            pipe_cmd_select.append('<option></option>');
            $.each(py_list_cmd, (i, cmd) => {
                option = $('<option></option>');
                pipe_cmd_select.append(option);
                option.attr('value', cmd['title']);
                option.text(`${cmd['title']}(mode=${cmd['mode']}, cmd=${cmd['cmd']})`);
            });
            cmd_select_template.find('.add_buton').click((e) => {
                cmd_select_template_func($(e.currentTarget), py_list_cmd);
            });
            cmd_select_template.find('.del_buton').click((e) => {
                $(e.currentTarget).parents('.cmd_select_item').remove();
            });
            return cmd_select_template;
        }
        if(modal_title != '') {
            // パイプラインファイルの読み込み
            py_list_cmd = await eel.list_cmd(null)();
            cmd_select = cmd_select_template_func(pipe_modal.find('.add_buton'), py_list_cmd)
            py_load_pipe = await eel.load_pipe(modal_title)();
            $.each(py_load_pipe, (key, val) => {
                if (typeof val === 'boolean') {
                    val = val.toString();
                }
                // フォームに値をセット
                if(Array.isArray(val)){
                    $.each(val, (i, v) => {
                        e = pipe_modal.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                        $(e).click();
                    });
                    pipe_modal.find(`[name="${key}"]`).each((i, e) => {
                        if (val[i] && val[i]!="" || i==0) $(e).val(val[i]);
                        else $(e).parent().find('.del_buton').click();
                    });
                } else {
                    pipe_modal.find(`[name="${key}"]`).val(val);
                }
            });
            $('#cmd_del').show();
            pipe_modal.find('[name="title"]').attr('readonly', true);
        } else {
            // 新規パイプラインファイルの作成
            modal_title = 'New Pipeline';
            $('#cmd_del').hide();
            pipe_modal.find('[name="title"]').val('');
            pipe_modal.find('[name="title"]').attr('readonly', false);
            pipe_modal.find('[name="description"]').val('');
            py_list_cmd = await eel.list_cmd(null)();
            cmd_select = cmd_select_template_func(pipe_modal.find('.add_buton'), py_list_cmd)
        }
        pipe_modal.find('.modal-title').text(`Pipeline : ${modal_title}`);
        pipe_modal.modal('show');
    }
    $('.pipe_card').off('click').on('click', pipe_card_func);
    // パイプラインファイルの保存
    $('#pipe_save').off('click').on('click', async () => {
        pipe_modal = $('#pipe_modal');
        var [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        show_loading();
        result = await eel.save_pipe(title, opt)();
        await list_pipe_func();
        $('.pipe_card').off('click').on('click', pipe_card_func);
        if (result['success']) alert(result['success']);
        else if (result['warn']) alert(result['warn']);
        hide_loading();
    });
    // パイプラインファイルの削除
    $('#pipe_del').off('click').on('click', async () => {
        pipe_modal = $('#pipe_modal');
        var title = pipe_modal.find('[name="title"]').val();
        show_loading();
        if (window.confirm(`delete "${title}"?`)) {
            await eel.del_pipe(title)();
            pipe_modal.modal('hide');
            await list_pipe_func();
            $('.pipe_card').off('click').on('click', pipe_card_func);
        }
        hide_loading();
    });
    // パイプラインファイルの実行
    $('#pipe_exec').off('click').on('click', async () => {
        pipe_modal = $('#pipe_modal');
        var [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content').find('.is-invalid').length > 0) {
            return;
        }
        show_loading();
        // コマンドの実行
        $('#loading').find('.bbforce').addClass('pipe_executed');
        eel.exec_pipe(title, opt)().then((result) => {});
    });
    // RAW表示の実行
    $('#pipe_raw').off('click').on('click', async () => {
        pipe_modal = $('#pipe_modal');
        var [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content').find('.is-invalid').length > 0) {
            return;
        }
        show_loading();
        // コマンドの実行
        eel.raw_pipe(title, opt)().then((result) => {
            view_raw_func(title, result);
            hide_loading();
        });
    });
};