// captureファイルを選択して表示する
const open_capture_func = (target_id) => {
    // ファイル選択後に結果画面を開く
    const view_capture_func = (current_path) => {
        eel.load_capture(current_path)().then((result) =>{
            view_result_func(current_path, result);
            hide_loading();
        });
    };
    filer_modal_func(target_id, 'capture', '', view_capture_func);
};