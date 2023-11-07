from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np
import onnxruntime as rt


def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:bytes):
    image_data, image_size, image_obj = preprocess_img(image, img_width, img_height)

    input_name = session.get_inputs()[0].name           # 'image'
    input_name_img_shape = session.get_inputs()[1].name # 'image_shape'
    output_name_boxes = session.get_outputs()[0].name   # 'boxes'
    output_name_scores = session.get_outputs()[1].name  # 'scores'
    output_name_indices = session.get_outputs()[2].name # 'indices'

    boxes, scores, indices = session.run([output_name_boxes, output_name_scores, output_name_indices],
                                {input_name: image_data, input_name_img_shape: image_size})
    output_boxes, output_scores, output_classes = [], [], []
    for idx in indices[0]:
        output_classes.append(idx[1])
        output_scores.append(scores[tuple(idx)])
        output_boxes.append(boxes[idx[0], idx[2]])

    output_image = draw_boxes(image_obj, output_boxes, output_scores, output_classes)

    return dict(output_boxes=output_boxes, output_scores=output_scores, output_classes=output_classes), output_image

def resize_img(image:Image, to_w, to_h):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    scale = min(to_w/iw, to_h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', (to_w, to_h), (128,128,128))
    new_image.paste(image, ((to_w-nw)//2, (to_h-nh)//2))
    return new_image

def preprocess_img(img:bytes, model_img_width:int, model_img_height:int):
    image = Image.open(BytesIO(img))
    boxed_image = resize_img(image, model_img_width, model_img_height)
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.transpose(image_data, [2, 0, 1])
    image_data = np.expand_dims(image_data, 0)
    image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
    return image_data, image_size, image

def draw_boxes(image:Image, boxes:list[list[float]], scores:list[float], classes:list[int], labels:list[str] = None, colors = None):
    draw = ImageDraw.Draw(image)
    for box, score, cl in zip(boxes, scores, classes):
        x, y, w, h = box
        top = max(0, np.floor(x + 0.5).astype(int))
        left = max(0, np.floor(y + 0.5).astype(int))
        right = min(image.width, np.floor(x + w + 0.5).astype(int))
        bottom = min(image.height, np.floor(y + h + 0.5).astype(int))
        color = colors[cl] if colors is not None else (255, 0, 0)
        draw.rectangle(((top, left), (right, bottom)), outline=color)

        label = labels[cl] if labels is not None else str(cl)
        draw.text((top, left), label, fill=(0, 0, 0))
    
    return image