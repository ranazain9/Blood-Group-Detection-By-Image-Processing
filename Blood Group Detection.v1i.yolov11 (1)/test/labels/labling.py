import cv2
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # update path if needed

# Folder with images
image_folder = "images/"
output_folder = "labels/"

os.makedirs(output_folder, exist_ok=True)

for image_name in os.listdir(image_folder):
    if image_name.endswith(('.jpg', '.png')):
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)
        h, w, _ = image.shape

        # OCR text box detection
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        label_lines = []
        for i in range(len(data['text'])):
            text = data['text'][i]
            conf = int(data['conf'][i])

            if conf > 60:
                x, y, box_w, box_h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                x_center = (x + box_w / 2) / w
                y_center = (y + box_h / 2) / h
                width = box_w / w
                height = box_h / h

                # Class ID logic (example)
                if text.upper() == 'A':
                    class_id = 0
                elif text.upper() == 'B':
                    class_id = 1
                elif text == '+':
                    class_id = 2
                else:
                    continue  # skip unknowns

                label_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Save YOLO label file
        if label_lines:
            label_file = os.path.join(output_folder, image_name.replace('.jpg', '.txt').replace('.png', '.txt'))
            with open(label_file, 'w') as f:
                f.write("\n".join(label_lines))
