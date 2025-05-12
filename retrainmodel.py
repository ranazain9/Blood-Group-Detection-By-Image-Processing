from ultralytics import YOLO

# Load the last trained model (e.g., best.pt or last.pt)
model = YOLO(r"D:\SEMESTER 4\PYTHON Filnal project\runs\detect\train7\weights\last.pt")  # Adjust the path to your last.pt

# Resume training from the last checkpoint
model.train(data=r"D:\SEMESTER 4\PYTHON Filnal project\Blood Group Detection.v1i.yolov11 (1)\data.yaml",
    resume=True,
    epochs=50,
    imgsz=640
)

results = model('path/to/image.jpg')
results.show()  # or results.save()
