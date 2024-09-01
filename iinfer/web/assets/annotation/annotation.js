// データセットフォルダを選択して表示する
const open_datasetfolder_func = (target_id) => {
  // ファイル選択後に値を設定する
  const set_open_dir_func = (current_path, opt) => {
    right_container = $('#right_container');
    right_container.find('.filer_host').val(opt['host']);
    right_container.find('.filer_port').val(opt['port']);
    right_container.find('.filer_password').val(opt['password']);
    right_container.find('.filer_svname').val(opt['svname']);
    right_container.find('.filer_local_data').val(opt['local_data']);
    right_container.find('.filer_address').val(current_path);
    right_container.find('.filer_server_bot').text(opt['svname']);
    hide_loading();
  };
  fmodal.filer_modal_func(target_id, 'DataSet Folder', $(`#${target_id}`).val(), true, false, set_open_dir_func);
};