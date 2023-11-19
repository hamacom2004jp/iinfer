from PIL import Image
import numpy as np
import onnxruntime as rt


def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:Image):
    image_data, _, image_obj = preprocess_img(image, img_width, img_height)

    results = session.run(["Softmax:0"], {"images:0": image_data})[0]

    output_scores, output_classes = [], []
    result = reversed(results[0].argsort()[-5:])
    for r in result:
        output_classes.append(r)
        output_scores.append(results[0][r])

    return dict(output_scores=output_scores, output_classes=output_classes), image_obj

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

def preprocess_img(image:Image, model_img_width:int, model_img_height:int):
    boxed_image = resize_img(image, model_img_width, model_img_height)
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)
    image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
    return image_data, image_size, image
