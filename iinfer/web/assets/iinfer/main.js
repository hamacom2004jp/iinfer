const change_dark_mode = (dark_mode) => {
    const html = $('html');
    if(dark_mode) html.attr('data-bs-theme','dark');
    else if(html.attr('data-bs-theme')=='dark') html.removeAttr('data-bs-theme');
    else html.attr('data-bs-theme','dark');
}
const show_loading = () => {
    const elem = $('#loading');
    elem.removeClass('d-none');
}
const hide_loading = () => {
    const elem = $('#loading');
    elem.addClass('d-none');
}
$(() => {
    // ダークモード対応
    change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    // copyright情報取得
    const copyright_func = async () => {
        const cp = await copyright();
        $('.copyright').text(cp);
    };
    copyright_func();
    // コマンド一覧の取得と表示
    list_cmd_func().then(list_cmd_func_then);
    // コマンド一覧の検索
    $('#cmd_kwd').off('change').on('change', (e) => list_cmd_func().then(list_cmd_func_then));
    // パイプライン一覧の取得と表示
    list_pipe_func().then(list_pipe_func_then);
    // パイプライン一覧の検索
    $('#pipe_kwd').off('change').on('change', (e) => list_pipe_func().then(list_pipe_func_then));

    $('#versions_modal').on('shown.bs.modal	', () => {
        // iinferのバージョン情報取得
        const versions_iinfer_func = async () => {
            const vi = await versions_iinfer();
            $('#versions_iinfer').html('');
            vi.forEach((v, i) => {
                v = v.replace(/<([^>]+)>/g, '<a href="$1" target="_blank">$1</a>');
                const div = $('<div class="d-block"></div>');
                $('#versions_iinfer').append(div);
                if(i==0) {
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
            const vu = await versions_used();
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
    })

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
        hide_loading();
    });

    // disable F5 and Ctrl+R
    $(document).on('keydown', (e) => {
        if ((e.which || e.keyCode) == 116) {
            return false;
        } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
            return false;
        }
    });
    /*$(window).on('beforeunload', () => {
        event.preventDefault();
        event.returnValue = 'Check';
    });*/
    const gui_callback = () => {
        const protocol = window.location.protocol.endsWith('s') ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = window.location.port;
        const ws = new WebSocket(`${protocol}://${host}:${port}/gui/callback`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const cmd = data['cmd'];
            const title = data['title'];
            const output = data['output'];
            if (cmd == 'js_console_modal_log_func') {
                const elem = $('#console_modal_log');
                if (typeof output === 'object') {
                    output = JSON.stringify(output);
                }
                const text = elem.val() + output;
                elem.val(text);
                elem.get(0).setSelectionRange(text.length-1, text.length-1);
            }
            else if (cmd == 'js_return_cmd_exec_func') {
                const cmd_modal = $('#cmd_modal');
                cmd_modal.modal('hide');
                view_result_func(title, output);
                hide_loading();
            }
            else if (cmd == 'js_return_pipe_exec_func') {
                const pipe_modal = $('#pipe_modal');
                pipe_modal.modal('hide');
                view_result_func(title, output);
                hide_loading();
            }
            else if (cmd == 'js_return_stream_log_func') {
                const size_th = 1024*1024*5;
                const result_modal = $('#result_modal');
                if (typeof output != 'object') {
                    output = result_modal.find('.modal-body').html()+output;
                }
                view_result_func('stream log', output);
                result_modal.find('.btn_window').click();
            }
        };
    };
    gui_callback();
});

const copyright = async () => {
    const res = await fetch('copyright', {method: 'GET'});
    return await res.text();
}
const versions_iinfer = async () => {
    const res = await fetch('versions_iinfer', {method: 'GET'});
    return await res.json();
}
const versions_used = async () => {
    const res = await fetch('versions_used', {method: 'GET'});
    return await res.json();
}
const get_local_data = async () => {
    const res = await fetch('gui/get_local_data', {method: 'GET'});
    return await res.text();
}
const bbforce_cmd = async () => {
    const res = await fetch('bbforce_cmd', {method: 'GET'});
    return await res.json();
}
