from ultralytics import YOLO
import ultralytics

model = YOLO('yolov8n.pt')  
model.train(data=r"D:\SEMESTER 4\PYTHON Filnal project\Blood Group Detection.v1i.yolov11 (1)\data.yaml", epochs=50, imgsz=640)
results = model('path/to/image.jpg')
results.show()  
results.save()

