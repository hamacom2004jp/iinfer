change_dark_mode = (dark_mode) => {
    html = $(`html`);
    if(dark_mode) html.attr(`data-bs-theme`,`dark`);
    else if(html.attr(`data-bs-theme`)==`dark`) html.removeAttr(`data-bs-theme`);
    else html.attr(`data-bs-theme`,`dark`);
}
$(() => {
    // ダークモード対応
    change_dark_mode(window.matchMedia(`(prefers-color-scheme: dark)`).matches);
    // copyright情報取得
    copyright_func = async () => {
        copyright = await eel.copyright()();
        $(`.copyright`).text(copyright);
    };
    copyright_func();
    // コマンド一覧の取得と表示
    list_cmd_func().then(list_cmd_func_then);
    // コマンド一覧の検索
    $('#cmd_kwd').off(`change`).on(`change`, (e) => list_cmd_func().then(list_cmd_func_then));
    // パイプライン一覧の取得と表示
    list_pipe_func().then(list_pipe_func_then);
    // パイプライン一覧の検索
    $('#pipe_kwd').off(`change`).on(`change`, (e) => list_pipe_func().then(list_pipe_func_then));

    $(`#versions_modal`).on(`shown.bs.modal	`, () => {
        // iinferのバージョン情報取得
        versions_iinfer_func = async () => {
            versions_iinfer = await eel.versions_iinfer()();
            $(`#versions_iinfer`).html(``);
            $.each(versions_iinfer, (i, v) => {
                v = v.replace(/<([^>]+)>/g, `<a href="$1" target="_blank">$1</a>`);
                div = $(`<div class="d-block"></div>`);
                $(`#versions_iinfer`).append(div);
                if(i==0) {
                    div.addClass(`m-3`);
                    div.append(`<h4>${v}</h4>`);
                } else {
                    div.addClass(`ms-5 me-5`);
                    div.append(`<h6>${v}</h6>`);
                }
            });
        };
        versions_iinfer_func();
        // usedのバージョン情報取得
        versions_used_func = async () => {
            versions_used = await eel.versions_used()();
            $(`#versions_used`).html(``);
            div = $(`<div class="overflow-auto" style="height:calc(100vh - 260px);"></div>`);
            table = $(`<table class="table table-bordered table-hover table-sm"></table>`);
            table_head = $(`<thead class="table-dark bg-dark"></thead>`);
            table_body = $(`<tbody></tbody>`);
            table.append(table_head);
            table.append(table_body);
            div.append(table);
            $(`#versions_used`).append(div);
            $.each(versions_used, (i, row) => {
                tr = $(`<tr></tr>`);
                $.each(row, (j, cel) => {
                    td = $(`<td></td>`).text(cel);
                    tr.append(td);
                });
                if(i==0) table_head.append(tr);
                else table_body.append(tr);
            });
        };
        versions_used_func();
    })

    // modal setting
    $(`.modal-dialog`).draggable({cursor:"move",cancel:".modal-body"});
    $(`#filer_modal .modal-dialog`).draggable({cursor:"move",cancel:".modal-body, .filer_address"});
    $(`.btn_window_stack`).off(`click`).on('click', () => {
        $(`.btn_window_stack`).css(`margin-left`, `0px`).hide();
        $(`.btn_window`).css(`margin-left`, `auto`).show();
        $(`.btn_window_stack`).parents(`.modal-dialog`).removeClass(`modal-fullscreen`);
    });
    $(`.btn_window`).off(`click`).on('click', () => {
        $(`.btn_window_stack`).css(`margin-left`, `auto`).show();
        $(`.btn_window`).css(`margin-left`, `0px`).hide();
        $(`.btn_window_stack`).parents(`.modal-dialog`).addClass(`modal-fullscreen`);
    });
    $(`.btn_window_stack`).css(`margin-left`, `0px`).hide();
    $(`.btn_window`).css(`margin-left`, `auto`).show();
    $(`.bbforce`).off(`click`).on('click', async () => {
        if ($(`#loading`).find(`.bbforce`).hasClass(`pipe_executed`) && 
            window.confirm(`Executing this action in pipeline will stop the gui mode itself. Are you sure?`)) {
            await eel.bbforce_cmd()();
            $(`#loading`).addClass(`d-none`);
            window.close();
            return;
        }
        await eel.bbforce_cmd()();
        $(`#loading`).addClass(`d-none`);
    });

    // disable F5 and Ctrl+R
    $(document).on(`keydown`, (e) => {
        if ((e.which || e.keyCode) == 116) {
            return false;
        } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
            return false;
        }
    });
    $(window).on("beforeunload", () => {
        event.preventDefault();
        event.returnValue = `Check`;
    });
    eel.expose(js_console_modal_log_func);
    function js_console_modal_log_func(line) {
        elem = $(`#console_modal_log`);
        text = elem.val() + line;
        elem.val(text);
        elem.get(0).setSelectionRange(text.length-1, text.length-1);
    };
    eel.expose(js_return_cmd_exec_func);
    function js_return_cmd_exec_func(title, result) {
        cmd_modal = $(`#cmd_modal`);
        cmd_modal.modal(`hide`);
        view_result_func(title, result);
        $(`#loading`).addClass(`d-none`);
    }
    eel.expose(js_return_pipe_exec_func);
    function js_return_pipe_exec_func(title, result) {
        pipe_modal = $(`#pipe_modal`);
        pipe_modal.modal(`hide`);
        view_result_func(title, result);
        $(`#loading`).addClass(`d-none`);
    }
    
});
