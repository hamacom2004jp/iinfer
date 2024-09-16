$(() => {
  // ダークモード対応
  iinfer.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
  // スプリッター初期化
  $('.split-pane').splitPane();
  // copyright表示
  iinfer.copyright();
  // バージョン情報モーダル初期化
  iinfer.init_version_modal();
  // モーダルボタン初期化
  iinfer.init_modal_button();
  // ファイラー画面初期化
  fsapi.onload();
});
