from vp4onnx.app import common
import onnxruntime as rt

def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:bytes):
    image_data, image_size, image_obj = common.preprocess_img(image, img_width, img_height)

    input_name = session.get_inputs()[0].name           # 'image'
    input_name_img_shape = session.get_inputs()[1].name # 'image_shape'
    output_name_boxes = session.get_outputs()[0].name   # 'boxes'
    output_name_scores = session.get_outputs()[1].name  # 'scores'
    output_name_indices = session.get_outputs()[2].name # 'indices'

    outputs_index = session.run([output_name_boxes, output_name_scores, output_name_indices],
                                {input_name: image_data, input_name_img_shape: image_size})
    output_boxes, output_scores, output_classes = [], [], []
    for idx in outputs_index[2]:
        output_classes.append(idx[1])
        output_scores.append(outputs_index[1][tuple(idx)])
        output_boxes.append(outputs_index[0][idx[0], idx[2]])

    output_image = common.draw_boxes(image_obj, output_boxes, output_scores, output_classes)

    return dict(output_boxes=output_boxes, output_scores=output_scores, output_classes=output_classes), output_image
