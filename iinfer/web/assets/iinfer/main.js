$(() => {
    // ダークモード対応
    iinfer.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    // コマンド一覧の取得と表示
    list_cmd_func().then(list_cmd_func_then);
    // コマンド一覧の検索
    $('#cmd_kwd').off('change').on('change', (e) => list_cmd_func().then(list_cmd_func_then));
    // パイプライン一覧の取得と表示
    list_pipe_func().then(list_pipe_func_then);
    // パイプライン一覧の検索
    $('#pipe_kwd').off('change').on('change', (e) => list_pipe_func().then(list_pipe_func_then));

    // copyright表示
    iinfer.copyright();
    // バージョン情報モーダル初期化
    iinfer.init_version_modal();
    // モーダルボタン初期化
    iinfer.init_modal_button();

    const gui_callback = () => {
        const protocol = window.location.protocol.endsWith('s:') ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = window.location.port;
        const path = window.location.pathname;
        const ws = new WebSocket(`${protocol}://${host}:${port}${path}/callback`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const cmd = data['cmd'];
            const title = data['title'];
            let output = data['output'];
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
                iinfer.hide_loading();
            }
            else if (cmd == 'js_return_pipe_exec_func') {
                const pipe_modal = $('#pipe_modal');
                pipe_modal.modal('hide');
                view_result_func(title, output);
                iinfer.hide_loading();
            }
            else if (cmd == 'js_return_stream_log_func') {
                const size_th = 1024*1024*5;
                const result_modal = $('#result_modal');
                if (typeof output != 'object') {
                    output = result_modal.find('.modal-body').html() +'<br/>'+ output;
                }
                view_result_func('stream log', output);
                result_modal.find('.btn_window').click();
            }
        };
    };
    gui_callback();
});
const get_local_data = async () => {
    const res = await fetch('gui/get_local_data', {method: 'GET'});
    return await res.text();
}
const bbforce_cmd = async () => {
    const res = await fetch('bbforce_cmd', {method: 'GET'});
    return await res.json();
}
