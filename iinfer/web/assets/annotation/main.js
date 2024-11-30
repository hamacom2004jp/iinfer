
$(() => {
  // ダークモード対応
  cmdbox.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
  // スプリッター初期化
  $('.split-pane').splitPane();
  // copyright表示
  cmdbox.copyright();
  // バージョン情報モーダル初期化
  cmdbox.init_version_modal();
  // モーダルボタン初期化
  cmdbox.init_modal_button();
  // アノテーション画面初期化
  anno.onload();
});
