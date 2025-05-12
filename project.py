import streamlit as st
from PIL import Image
from ultralytics import YOLO
import os
from datetime import datetime
from fpdf import FPDF
import qrcode

# --- Streamlit Config ---
st.set_page_config(page_title="Blood Group Detection", layout="wide")

# --- Load YOLO Model ---
model_path = r"D:\SEMESTER 4\PYTHON Filnal project\runs\detect\train7\weights\best.pt"
model = YOLO(model_path)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# --- Login System ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login_page():
    st.title("🔐 Login Page")
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username == "admin" and password == "1234":
                st.session_state["logged_in"] = True
                st.success("✅ Login Successful!")
            else:
                st.error("❌ Invalid Credentials!")

def detection_page():  
    st.markdown("<h1 style='color: red;'>🩸 Blood Group Detection</h1>", unsafe_allow_html=True)
    st.divider()

    # --- Step 1: Patient Information First ---
    if 'patient_name' not in st.session_state:
        with st.form("patient_info_form", clear_on_submit=False):
            patient_name = st.text_input("👤 Patient Name")
            patient_age = st.number_input("🎂 Patient Age", min_value=0, max_value=120, step=1)
            patient_gender = st.selectbox("👩‍⚕️ Patient Gender", ["Male", "Female", "Other"])
            next_button = st.form_submit_button("Next ➡️")

        if next_button:
            if not patient_name or patient_age == 0:
                st.error("⚠️ Please fill in all patient information.")
                st.stop()

            st.session_state["patient_name"] = patient_name
            st.session_state["patient_age"] = patient_age
            st.session_state["patient_gender"] = patient_gender
            st.session_state["patient_info_entered"] = True
            st.success("✅ Patient Information Saved. Now upload the blood sample image below.")
    
    # --- Step 2: Upload Blood Sample ---
    if 'patient_info_entered' in st.session_state and st.session_state['patient_info_entered']:
        with st.form("sample_upload_form"):
            uploaded_file = st.file_uploader("📂 Upload Blood Sample Image", type=["jpg", "jpeg", "png"])
            detect_button = st.form_submit_button("🔍 Process")

        if detect_button:
            if not uploaded_file:
                st.error("⚠️ Please upload a blood sample image.")
                st.stop()

            image = Image.open(uploaded_file)
            st.image(image, caption="🖼️ Uploaded Image", use_container_width=True)

            input_path = os.path.join(output_dir, "input.jpg")
            image.save(input_path)

            with st.spinner("Detecting..."):
                results = model(input_path)
                results[0].save(filename=os.path.join(output_dir, "detected.jpg"))

            st.success("✅ Detection Complete")
            st.image(os.path.join(output_dir, "detected.jpg"), caption="🔬 Detection Result", use_container_width=True)

            detected_labels = results[0].names
            class_ids = results[0].boxes.cls.tolist()
            if class_ids:
                detected_labels = [detected_labels[int(cls)] for cls in class_ids]
                unique_labels = set(label.lower() for label in detected_labels)

                st.session_state["unique_labels"] = unique_labels

                blood_group = "Unknown"
                if unique_labels == {"a", "d"}:
                    blood_group = "A+ (A Positive)"
                elif unique_labels == {"a"}:
                    blood_group = "A- (A Negative)"
                elif unique_labels == {"b", "d"}:
                    blood_group = "B+ (B Positive)"
                elif unique_labels == {"b"}:
                    blood_group = "B- (B Negative)"
                elif unique_labels == {"a", "b", "d"}:
                    blood_group = "AB+ (AB Positive)"
                elif unique_labels == {"a", "b"}:
                    blood_group = "AB- (AB Negative)"
                elif unique_labels == {"d"}:
                    blood_group = "O+ (O Positive)"
                elif not unique_labels.intersection({"a", "b", "d"}):
                    blood_group = "O- (O Negative)"

                st.session_state["blood_group"] = blood_group

            else:
                st.warning("⚠ No blood group markers detected.")

            # --- Automatically Generate Report after Detection ---
            if "blood_group" in st.session_state:
                st.divider()
                st.subheader("📝 Professional Hospital Report")

                now = datetime.now()

                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr_data = f"Patient Name: {st.session_state['patient_name']}, Blood Group: {st.session_state['blood_group']}, Date: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_image = qr.make_image(fill='black', back_color='white')
                qr_path = os.path.join(output_dir, "qr_code.png")
                qr_image.save(qr_path)

                pdf = FPDF()
                pdf.add_page()

                pdf.set_font("Arial", 'B', size=16)
                pdf.cell(0, 10, "XYZ Medical Center", ln=True, align="C")
                pdf.set_font("Arial", 'I', size=12)
                pdf.cell(0, 10, "Address: 123 Health St, City, Country", ln=True, align="C")
                pdf.cell(0, 10, "Contact: +123456789 | Email: info@xyzmedical.com", ln=True, align="C")
                pdf.ln(10)

                logo_path = r"D:\SEMESTER 4\PYTHON Filnal project\logo.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=80, y=10, w=50)
                    pdf.ln(30)

                pdf.set_font("Arial", 'B', size=12)
                pdf.cell(0, 10, f"Patient Name: {st.session_state['patient_name']}", ln=True)
                pdf.cell(0, 10, f"Patient Age: {st.session_state['patient_age']} years", ln=True)
                pdf.cell(0, 10, f"Patient Gender: {st.session_state['patient_gender']}", ln=True)
                pdf.ln(5)

                pdf.cell(0, 10, f"Blood Group Detected: {st.session_state['blood_group']}", ln=True)
                pdf.cell(0, 10, f"Detected Components: {', '.join(st.session_state['unique_labels']).upper()}", ln=True)
                pdf.ln(5)

                pdf.cell(0, 10, "Test Methodology:", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, "The blood group detection was performed using YOLOv8 object detection model. The model analyzes the blood sample and identifies key markers associated with different blood groups.")
                pdf.ln(5)

                pdf.multi_cell(0, 10, "Conclusion: Based on the analysis of the blood sample, the detected blood group is provided above. For further analysis or additional tests, please consult with the attending physician.")
                pdf.ln(5)

                pdf.image(qr_path, x=140, y=180, w=50, h=50)
                pdf.ln(5)

                pdf.cell(0, 10, "Doctor's Signature: ___________________", ln=True, align="L")
                pdf.ln(10)

                pdf.set_font("Arial", 'I', size=10)
                pdf.cell(0, 10, "For any inquiries, please contact XYZ Medical Center at +123456789", ln=True, align="C")

                report_path = os.path.join(output_dir, "hospital_blood_group_report_advanced.pdf")
                pdf.output(report_path)

                st.write("### Patient Information")
                st.write(f"*Patient Name:* {st.session_state['patient_name']}")
                st.write(f"*Patient Age:* {st.session_state['patient_age']} years")
                st.write(f"*Patient Gender:* {st.session_state['patient_gender']}")
                st.write(f"*Blood Group:* {st.session_state['blood_group']}")
                st.write(f"*Detected Components:* {', '.join(st.session_state['unique_labels']).upper()}")

                st.write("### Report Summary")
                st.write(f"*Test Methodology:* The blood group detection was performed using YOLOv8 object detection model, which analyzes blood samples to identify key markers for blood groups.")
                st.write(f"*Conclusion:* The detected blood group has been identified as *{st.session_state['blood_group']}*. Further analysis may be required.")

                with open(report_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Advanced PDF Report",
                        data=f,
                        file_name="hospital_blood_group_report_advanced.pdf",
                        mime="application/pdf"
                    )

# --- Main Page Logic ---
if not st.session_state["logged_in"]:
    login_page()
else:
    detection_page()
