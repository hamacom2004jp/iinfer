const webcap = {}
/** 初期化処理 */
webcap.init = () => {
  /** webcapが可能なpipelineの読込み */
  list_pipe(null).then(async (result) => {
    const pipeline_elem = $('#pipeline');
    for (const pipe of result) {
      if (!pipe || pipe.pipe_cmd.length == 0) continue;
      // pipe_cmdの最初の要素にwebcapコマンドがあるか確認
      const webcap_cmd = await load_cmd(pipe.pipe_cmd[0]);
      const outputs_key_str = webcap_cmd.outputs_key ? webcap_cmd.outputs_key.join(',') : "";
      if (!webcap_cmd || webcap_cmd.mode != 'web' || webcap_cmd.cmd != 'webcap') continue;
      url = `webcap/pub_img/${webcap_cmd.listen_webcap_port}`
      if (webcap_cmd.access_url) url = webcap_cmd.access_url;
      // pipe_cmdの最後の要素にshowimgコマンドがあるか確認
      const showimg_cmd = await load_cmd(pipe.pipe_cmd[pipe.pipe_cmd.length - 1]);
      if (!showimg_cmd || showimg_cmd.mode != 'postprocess' || showimg_cmd.cmd != 'showimg') continue;
      const capture_fps = webcap_cmd.capture_fps;
      const capture_frame_width = webcap_cmd.capture_frame_width;
      const capture_frame_height = webcap_cmd.capture_frame_height;
      const elem = $(`<li class="dropdown-submenu"><span class="ps-2 ${pipe.title}"/><a class="d-inline ps-2 dropdown-item" href="#" `
        + `onclick="webcap.change_pipeline('${pipe.title}', '${url}', '${outputs_key_str}', '${capture_fps}', '${capture_frame_width}', '${capture_frame_height}');">${pipe.title}</a></li>`);
      pipeline_elem.append(elem);
      webcap.change_pipeline(pipe.title, url, outputs_key_str, capture_fps, capture_frame_width, capture_frame_height);
    }
    if (pipeline_elem.find('.dropdown-submenu').length <= 0) {
      const elem = $(`<li class="dropdown-submenu"><a class="dropdown-item" href="#">&lt; Not found webcap to showimg pipeline &gt;</a></li>`);
      pipeline_elem.append(elem);
      webcap.change_pipeline(null, null, "", 10, 640, 480);
    }
    cmdbox.hide_loading();
  });
  $('#rec_error').off('click').on('click', () => {
    cmdbox.message('Please select pipeline and Camera.');
  });
  /** 使用可能なカメラ一覧の読込み */
  const camera_selection = async () => {
    if (!('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices)) {
      cmdbox.message('No camera found.');
      return;
    }
    try {
      await navigator.mediaDevices.getUserMedia({video: true});
    }
    catch (e) {
      cmdbox.message('No camera found.');
      return;
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
    const camera_elem = $('#camera');
    webcap.camera = {};
    videoDevices.map(videoDevice => {
      if (!videoDevice.deviceId) return;
      const elem = $(`<li class="dropdown-submenu"><span class="ps-2 ${videoDevice.deviceId}"/><a class="d-inline ps-2 dropdown-item" href="#" onclick="webcap.change_camera('${videoDevice.deviceId}', '${videoDevice.label}');">${videoDevice.label}</a></li>`);
      camera_elem.append(elem);
    });
    camera_elem.find('.dropdown-submenu .dropdown-item:first').click();
  };
  camera_selection();
  $('#rec_movie').hide();
  $('#rec_image').hide();
  webcap.recode_mode=='movie' && $('#rec_movie').show();
  webcap.recode_mode=='image' && $('#rec_image').show();
  /** イベントハンドラの設定 */
  webcap.container_elem = $('#img_container');
  webcap.video_elem = $('#video');
  webcap.video = webcap.video_elem.get(0);
  webcap.buffer_elem = $('#buffer');
  webcap.buffer = webcap.buffer_elem.get(0);
  webcap.buffer_2d = webcap.buffer.getContext('2d')
  webcap.canvas_elem = $('#canvas');
  webcap.canvas = webcap.canvas_elem.get(0);
  webcap.canvas_2d = webcap.canvas.getContext('2d')
  webcap.recode_mode = 'movie';
  $('#dropdown_rec_mov').off('click').on('click', () => {
    webcap.recode_mode = 'movie';
    $('#dropdown_rec_mov').text('* Movie Mode');
    $('#dropdown_rec_img').text('Image Mode');
    $('#rec_movie').show();
    $('#rec_image').hide();
  });
  $('#dropdown_rec_img').off('click').on('click', () => {
    webcap.recode_mode = 'image';
    $('#dropdown_rec_mov').text('Movie Mode');
    $('#dropdown_rec_img').text('* Image Mode');
    $('#rec_movie').hide();
    $('#rec_image').show();
  });
  $('#rec_movie').off('click').on('click', webcap.rec_start);
  $('#rec_image').off('click').on('click', webcap.rec_start);
  $('#pause').off('click').on('click', webcap.rec_stop);
  $(window).resize(async () => {
    await webcap.resize();
  });
  webcap.video_elem.on('play', webcap.rec);
};
/** カメラの設定を取得 */
webcap.get_camera_const = async () => {
  if (!webcap.camera) webcap.camera = {};
  const constraints = {
    video: {
      deviceId: {
        exact: webcap.camera.deviceId
      },
      width: webcap.pipeline.capture_frame_width,
      height: webcap.pipeline.capture_frame_height
    },
    audio: false,
  };
  try {
    await navigator.mediaDevices.getUserMedia(constraints);
  } catch (e) {
    cmdbox.message(`Error: ${e}\nCould not connect to camera.`);
  }
  return constraints;
};
/** カメラの切り替え */
webcap.change_camera = (deviceId, label) => {
  webcap.video.pause();
  webcap.video.srcObject = null
  webcap.camera.deviceId = deviceId;
  webcap.camera.label = label;
  const camera_elem = $('#camera');
  camera_elem.find('.dropdown-submenu span').html("&nbsp;");
  camera_elem.find(`.${deviceId}`).text("*");
  webcap.stream();
};
/** カメラ映像取得 */
webcap.stream = async () => {
  const constraints = await webcap.resize();
  webcap.video.srcObject = await navigator.mediaDevices.getUserMedia(constraints);
  const track = webcap.video.srcObject.getVideoTracks()[0];
  webcap.video_settings = track.getSettings();
  webcap.video.play();
};
/** windowサイズ変更ハンドラ */
webcap.resize = async () => {
  const constraints = await webcap.get_camera_const();
  const width = parseInt(webcap.container_elem.width() - 10);
  const height = parseInt(webcap.container_elem.height() - 10);
  webcap.video_elem.attr('height', height).attr('width', width);
  webcap.buffer_elem.attr('height', height).attr('width', width);
  webcap.canvas_elem.attr('height', height).attr('width', width);
  return constraints;
};
/** pipelineの切り替え */
webcap.change_pipeline = (title, url, outputs_key_str, capture_fps, capture_frame_width, capture_frame_height) => {
  if (!webcap.pipeline) webcap.pipeline = {};
  webcap.pipeline.title = title;
  webcap.pipeline.url = url;
  webcap.pipeline.is_rec = false;
  webcap.pipeline.outputs_key_str = outputs_key_str;
  webcap.pipeline.capture_fps = capture_fps;
  webcap.pipeline.capture_frame_width = capture_frame_width;
  webcap.pipeline.capture_frame_height = capture_frame_height;
  webcap.get_camera_const()
  if (!title) {
    $('#rec_movie').hide();
    $('#rec_image').hide();
    $('#pause').hide();
    $('#rec_error').show();
    $('#navi_title').text(`WebCap`);
    return;
  }
  $('#pause').hide();
  webcap.recode_mode=='movie' && $('#rec_movie').show();
  webcap.recode_mode=='image' && $('#rec_image').show();
  $('#rec_error').hide();
  $('#navi_title').text(`WebCap ( ${title} )`);
  const pipeline_elem = $('#pipeline');
  pipeline_elem.find('.dropdown-submenu span').html("&nbsp;");
  pipeline_elem.find(`.${title}`).text("*");
  fetch(webcap.pipeline.url, {method: "GET", mode:'cors'});
};
/** カメラ映像をwebcapに送信開始 */
webcap.rec_start = () => {
  if (!webcap.pipeline || webcap.pipeline.length <= 0) {
    cmdbox.message('Please select pipeline.');
    return;
  }
  if (webcap.pipeline.is_rec) return;
  $('#rec_movie').hide();
  $('#rec_image').hide();
  $('#pause').show();
  webcap.pipeline.is_rec = true;
  cmdbox.show_loading();
};
/** カメラ映像をwebcapに送信停止 */
webcap.rec_stop = () => {
  webcap.recode_mode=='movie' && $('#rec_movie').show();
  webcap.recode_mode=='image' && $('#rec_image').show();
  $('#pause').hide();
  cmdbox.hide_loading();
  webcap.pipeline.is_rec = false;
};
/** アスペクト比計算 */
webcap.calc_aspect = (video_width, video_height, canvas_width, canvas_height) => {
  const videoAspectRatio = video_width / video_height;
  const canvasAspectRatio = canvas_width / canvas_height;
  let renderableHeight, renderableWidth, xStart, yStart;
  const padding = 10;
  if(videoAspectRatio < canvasAspectRatio) {
    renderableHeight = canvas_height - padding;
    renderableWidth = videoAspectRatio * renderableHeight - padding;
    xStart = (canvas_width - renderableWidth) / 2;
    yStart = 0;
  } else {
    renderableWidth = canvas_width - padding;
    renderableHeight = renderableWidth / videoAspectRatio - padding;
    xStart = 0;
    yStart = (canvas_height - renderableHeight) / 2;
  }
  return [xStart, yStart, renderableWidth, renderableHeight];
};
/** カメラ映像をwebcapに送信 */
webcap.rec = () => {
  if (!webcap.video.srcObject) {
    return;
  }
  const aspect = webcap.calc_aspect(webcap.video_settings.width, webcap.video_settings.height, webcap.canvas.width, webcap.canvas.height);
  // バッファにvideoの内容を描画
  webcap.buffer_2d.drawImage(webcap.video, aspect[0], aspect[1], aspect[2], aspect[3]);
  if (!webcap.pipeline || !webcap.pipeline.is_rec) {
    // 録画前の場合はバッファの内容をそのまま描画
    webcap.canvas_2d.drawImage(webcap.video, aspect[0], aspect[1], aspect[2], aspect[3]);
    if (!webcap.pipeline.capture_fps) {
      window.setTimeout(webcap.rec, 1000 / 10);
    } else {
      window.setTimeout(webcap.rec, 1000 / webcap.pipeline.capture_fps);
    }
    return;
  }
  // 画像送信
  const capimg = webcap.buffer.toDataURL('image/jpeg');
  const formData = new FormData();
  const blob = new Blob([capimg], {type:"application/octet-stream"});
  formData.append('files', blob);
  fetch(webcap.pipeline.url, {method: "POST", mode:'cors', body: formData}).then((res) => {
    cmdbox.hide_loading();
    if (!res.ok) {
      cmdbox.message(`Error: ${res.status} ${res.statusText}\nCould not connect to webcap process.`);
      webcap.rec_stop();
    }
  }).catch((e) => {
    cmdbox.message(`Error: ${e} ${webcap.pipeline.url}`);
    webcap.rec_stop();
  }).finally(() => {
    if (webcap.recode_mode == 'image') {
      webcap.rec_stop();
    }
    window.setTimeout(webcap.rec, 1000 / webcap.pipeline.capture_fps);
  });
};
/** callbackを表示 */
webcap.callback_reconnectInterval_handler = null;
webcap.callback_ping_handler = null;
webcap.callback = async () => {
  if (webcap.callback_reconnectInterval_handler) {
    clearInterval(webcap.callback_reconnectInterval_handler);
  }
  if (webcap.callback_ping_handler) {
    clearInterval(webcap.callback_ping_handler);
  }
  const protocol = window.location.protocol.endsWith('s:') ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = window.location.port;
  const path = window.location.pathname;
  const ws = new WebSocket(`${protocol}//${host}:${port}${path}/sub_img`);
  const target_elem = $('#out_container');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const img_url = data['img_url'];
    const img_id = data['img_id'];
    const outputs_key = data['outputs_key'];
    const outputs = data['success'];
    if (img_url) {
      const img = new Image();
      img.onload = () => {
        webcap.canvas_2d.drawImage(img, 0, 0, webcap.canvas.width, webcap.canvas.height);
      }
      img.src = img_url;
    }
    if (outputs) {
      const elem = $("#out_container");
      elem.html('');
      const table = $('<table class="table table-bordered table-hover table-sm"></table>');
      const table_body = $('<tbody></tbody>');
      table.append(table_body);
      elem.append(table);
      let filter_outputs = {},  dst_outputs = {}
      filter_output(outputs, outputs_key, filter_outputs);
      if (webcap.pipeline.outputs_key_str) {
        filter_output(filter_outputs, webcap.pipeline.outputs_key_str.split(','), dst_outputs);
      } else {
        dst_outputs = filter_outputs;
      }
      Object.keys(dst_outputs).forEach((key) => {
        const val = dst_outputs[key];
        if (!val) return;
        table_body.append(`<tr class="table_title fs-5" style="overflow-wrap:break-word;word-break:break-all;"><th>${key}</th><td>${val}</td></tr>`);
      });
      table_body.find('tr:first').addClass('fs-1').removeClass('fs-5');
    }
  };
  ws.onopen = () => {
    const ping = () => {ws.send('ping');};
    const timout = webcap.pipeline && webcap.pipeline.capture_fps ? 1000 / webcap.pipeline.capture_fps : 1000;
    webcap.callback_ping_handler = setInterval(() => {ping();}, timout);
  };
  ws.onerror = (e) => {
    console.error(`Websocket error: ${e}`);
    clearInterval(webcap.callback_ping_handler);
  };
  ws.onclose = () => {
    clearInterval(cmdbox.gui_callback_ping_handler);
    webcap.callback_reconnectInterval_handler = setInterval(() => {
      webcap.callback();
    }, 3000);
  };
  const filter_output = (src, keys, dst) => {
    for (const key of keys) {
      if (src[key]) {
        dst[key] = src[key];
        continue;
      }
      if (typeof src !== 'object') continue;
      Object.keys(src).forEach((k) => {
        if (typeof src[k] !== 'object') return;
        filter_output(src[k], keys, dst);
      });
    }
  }
}
$(() => {
  cmdbox.show_loading();
  // ダークモード対応
  cmdbox.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
  // copyright表示
  cmdbox.copyright();
  // バージョン情報モーダル初期化
  cmdbox.init_version_modal();
  // モーダルボタン初期化
  cmdbox.init_modal_button();
  // webcapモード初期化
  webcap.init();
  // 推論結果受信
  webcap.callback();
});
