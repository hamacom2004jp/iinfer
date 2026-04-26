.. -*- coding: utf-8 -*-

**************************************
Command Reference ( postprocess mode )
**************************************

List of postprocess mode commands.

postprocess ( cls_judge ) : ``cmdbox -m postprocess -c cls_judge <Option>``
===========================================================================

- Perform image classification judgment using the inference result.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--ok_score_th <ok_score_th>","","Class scores greater than this value are judged as ok."
    "--ok_classes <ok_classes>","","Specify the class index to include in the ok class. Multiple specifications are possible."
    "--ok_labels <ok_labels>","","Specify the class label to include in the ok class. Multiple specifications are possible."
    "--ng_score_th <ng_score_th>","","Class scores greater than this value are judged as ng."
    "--ng_classes <ng_classes>","","Specify the class index to include in the ng class. Multiple specifications are possible."
    "--ng_labels <ng_labels>","","Specify the class label to include in the ng class. Multiple specifications are possible."
    "--ext_score_th <ext_score_th>","","Class scores greater than this value are judged as gray."
    "--ext_classes <ext_classes>","","Specify the class index to include in the gray class. Multiple specifications are possible."
    "--ext_labels <ext_labels>","","Specify the class label to include in the gray class. Multiple specifications are possible."
    "--nodraw <nodraw>","","Do not draw bboxes, etc. on the inference result image."
    "-P, --output_preview <output_preview>","","Display the judgment result image with `cv2.imshow`."
    "--output_image <output_image>","","Specify the destination file for saving the post-processing result image."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( cmd ) : ``cmdbox -m postprocess -c cmd <Option>``
===============================================================

- Set the inference result to an environment variable and execute an arbitrary command.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--cmdline <cmdline>","required","Specifies the command to execute. The environment variables set are `outputs` , `output_image`. The value is the file path of the temporary file."
    "--output_image_ext <output_image_ext>","required","Specifies the format of the output image.Acceptable image types are `bmp` , `png`, and `jpeg`."
    "--output_maxsize <output_maxsize>","required","Specifies the maximum size of the command execution results to be captured."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( csv ) : ``cmdbox -m postprocess -c csv <Option>``
===============================================================

- Convert the inference result to a CSV file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--out_headers <out_headers>","","Specify the headers to output. Multiple specifications are possible."
    "--noheader <noheader>","","Do not output the header row."
    "--output_csv <output_csv>","","Save the contents in csv. If this is specified, no standard output will be performed."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( det_clip ) : ``cmdbox -m postprocess -c det_clip <Option>``
=========================================================================

- Cut out the detected area in ObjectDetection and output it in caprute format csv.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--image_type <image_type>","","Specify the type of image to output."
    "--clip_margin <clip_margin>","","The number of pixels to provide margin around the bbox inspected. However, if there is a margin outside the original image, as much margin as possible is obtained."
    "--output_csv <output_csv>","","Save the contents in csv. If this is specified, no standard output will be performed."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( det_face_store ) : ``cmdbox -m postprocess -c det_face_store <Option>``
=====================================================================================

- Cut out the face feature data detected by Face Detection and Recognition and generate a face recognition store file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--image_type <image_type>","","Specify the type of image to output."
    "--face_threshold <face_threshold>","","If the face score is below the threshold, it will not be included in the face feature store."
    "--clip_margin <clip_margin>","","The number of pixels to provide margin around the bbox inspected. However, if there is a margin outside the original image, as much margin as possible is obtained."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( det_filter ) : ``cmdbox -m postprocess -c det_filter <Option>``
=============================================================================

- Filter the detected area in ObjectDetection.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--score_th <score_th>","","Remove bboxes with class scores less"
    "--width_th <width_th>","","Remove bboxes with a width less than this length."
    "--height_th <height_th>","","Remove bboxes with a height less than this length."
    "--classes <classes>","","Remove bboxes other than this class. Multiple specifications are possible."
    "--labels <labels>","","Remove bboxes other than this label. Multiple specifications are possible."
    "--nodraw <nodraw>","","Do not draw bboxes, etc. on the inference result image."
    "-P, --output_preview <output_preview>","","Display the judgment result image with `cv2.imshow`."
    "--output_image <output_image>","","Specify the destination file for saving the post-processing result image."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( det_judge ) : ``cmdbox -m postprocess -c det_judge <Option>``
===========================================================================

- Perform judgment using the detected area in ObjectDetection.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--ok_score_th <ok_score_th>","","Class scores greater than this value are judged as ok."
    "--ok_classes <ok_classes>","","Specify the class index to include in the ok class. Multiple specifications are possible."
    "--ok_labels <ok_labels>","","Specify the class label to include in the ok class. Multiple specifications are possible."
    "--ng_score_th <ng_score_th>","","Class scores greater than this value are judged as ng."
    "--ng_classes <ng_classes>","","Specify the class index to include in the ng class. Multiple specifications are possible."
    "--ng_labels <ng_labels>","","Specify the class label to include in the ng class. Multiple specifications are possible."
    "--ext_score_th <ext_score_th>","","Class scores greater than this value are judged as gray."
    "--ext_classes <ext_classes>","","Specify the class index to include in the gray class. Multiple specifications are possible."
    "--ext_labels <ext_labels>","","Specify the class label to include in the gray class. Multiple specifications are possible."
    "--nodraw <nodraw>","","Do not draw bboxes, etc. on the inference result image."
    "-P, --output_preview <output_preview>","","Display the judgment result image with `cv2.imshow`."
    "--output_image <output_image>","","Specify the destination file for saving the post-processing result image."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( httpreq ) : ``cmdbox -m postprocess -c httpreq <Option>``
=======================================================================

- Send the inference result to the specified HTTP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--json_without_img <json_without_img>","","Send JSON without including images when sending JSON."
    "--fileup_name <fileup_name>","required","Specify the parameter name when posting the image of the inference result. If omitted, `file` is used."
    "--outputs_url <outputs_url>","required","Specify the URL to POST the JSON of the inference result."
    "--output_image_url <output_image_url>","","Specify the URL to POST the image of the inference result."
    "--output_image_ext <output_image_ext>","","Specifies the format of the image of the inference result.You can specify `bmp` , `png`, or `jpeg`."
    "--output_image_prefix <output_image_prefix>","","Specifies the prefix of the inferred result image. If omitted, `output_` is used."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( seg_bbox ) : ``cmdbox -m postprocess -c seg_bbox <Option>``
=========================================================================

- Convert the detected area in SemanticSegmentation to bbox.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--del_segments <del_segments>","","Remove the segmentation mask from the result. This reduces the result capacity."
    "--nodraw <nodraw>","","Do not draw bboxes, etc. on the inference result image."
    "--nodraw_bbox <nodraw_bbox>","","Do not draw bboxes on the inference result image."
    "--nodraw_rbbox <nodraw_rbbox>","","Do not draw rotated bboxes on the inference result image."
    "-P, --output_preview <output_preview>","","Display the judgment result image with `cv2.imshow`."
    "--output_image <output_image>","","Specify the destination file for saving the post-processing result image."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( seg_filter ) : ``cmdbox -m postprocess -c seg_filter <Option>``
=============================================================================

- Filter the detected area in SemanticSegmentation.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--del_segments <del_segments>","","Remove the segmentation mask from the result. This reduces the result capacity."
    "--logits_th <logits_th>","","Pixels with class scores less than this value are removed."
    "--classes <classes>","","Remove areas other than this class. Multiple specifications are possible."
    "--labels <labels>","","Remove areas other than this label. Multiple specifications are possible."
    "--nodraw <nodraw>","","Do not draw masks on the inference result image."
    "--del_logits <del_logits>","","Remove the segmentation score from the result. This reduces the result capacity."
    "-P, --output_preview <output_preview>","","Display the judgment result image with `cv2.imshow`."
    "--output_image <output_image>","","Specify the destination file for saving the post-processing result image."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

postprocess ( showimg ) : ``cmdbox -m postprocess -c showimg <Option>``
=======================================================================

- Forward the inference results to showimg.html.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i, --input_file <input_file>","","Specify the inference result to be post-processed by file."
    "--stdin <stdin>","","Read the inference result to be post-processed from standard input."
    "--host <host>","","Specify the service host of the Redis server."
    "--port <port>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--maxrecsize <maxrecsize>","","Specifies the maximum record size of inference results to be stored on the Redis server."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
