if uploaded_file:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Save uploaded image temporarily
    input_path = os.path.join(output_dir, "input.jpg")
    image.save(input_path)

    if st.button("🔍 Process"):
        # Run YOLOv8 detection
        with st.spinner("Detecting..."):
            results = model(input_path)
            results[0].save(filename=os.path.join(output_dir, "detected.jpg"))

        # Show result
        st.success("Detection Complete ✅")
        st.image(os.path.join(output_dir, "detected.jpg"), caption="Detected Blood Group", use_container_width=True)

        # Show detected classes
        try:
            class_names = results[0].names
            boxes = results[0].boxes
            class_ids = boxes.cls.tolist()

            if class_ids:
                detected_labels = [class_names[int(cls)] for cls in class_ids]
                detected_str = ", ".join(set(detected_labels))
                st.info(f"🩸 Detected Blood Group(s): **{detected_str}**")

                # Logic to determine blood group
                labels = set(label.lower() for label in detected_labels)
                if labels == {"a", "d"}:
                    st.success("Final Blood Group: 🅰️+")
                elif labels == {"a"}:
                    st.success("Final Blood Group: 🅰️-")
                elif labels == {"b", "d"}:
                    st.success("Final Blood Group: 🅱️+")
                elif labels == {"b"}:
                    st.success("Final Blood Group: 🅱️-")
                elif labels == {"a", "b", "d"}:
                    st.success("Final Blood Group: AB+")
                elif labels == {"a", "b"}:
                    st.success("Final Blood Group: AB-")
                elif labels == {"d"}:
                    st.success("Final Blood Group: 🅾️+")
                elif not labels.intersection({"a", "b", "d"}):
                    st.success("Final Blood Group: 🅾️-")
                else:
                    st.warning("Unknown combination.")
            else:
                st.warning("No blood group detected.")
        except Exception as e:
            st.error(f"Error processing results: {e}")
