import os

import streamlit as st
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
from StoreLocator import locatestore
from APICalling import Generatetxt


def prompt(title, ocr_text):
    return f"""
    {title}

    {ocr_text}

    Your task:

    Ignore patient details, hospital information, doctor details, dates, registration numbers, addresses, phone numbers, and other unrelated text.

    Extract ONLY the medicine names from the OCR text.

    For each medicine:
    1. Identify the brand medicine.
    2. Find its Jan Aushadhi equivalent.
    3. Find the approximate MRP.
    4. Find the Jan Aushadhi price.
    5. Calculate savings amount.
    6. Calculate savings percentage.

    Return only the medicines in the specified format.
    """


def get_api_key():
    env_key = os.getenv("APIKEY")
    if env_key:
        return env_key

    try:
        return st.secrets["APIKEY"]
    except Exception:
        return None


@st.cache_resource
def load_model():
    return PaddleOCR(
        use_angle_cls=True,
        lang="en",
        enable_mkldnn=False,
    )

st.set_page_config(
    page_title="MedSave AI",
)

st.title("MedSave AI")
st.subheader("Find Generetic Medicine")

api_key = get_api_key()
if not api_key:
    st.warning(
        "AI generation is disabled because the API key is not configured. "
        "Set APIKEY in your environment or Streamlit secrets."
    )

but = st.radio(
    label="Choose a option",
    options=["Upload Prescribsion", "Upload Single Medicine", "Type Manually"],
)

if but in ("Upload Prescribsion", "Upload Single Medicine"):
    upload_label = "Upload Prescribsion" if but == "Upload Prescribsion" else "Upload Medicine"
    file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png", "webp"])

    if file:
        image = Image.open(file)
        st.image(image, caption="Uploaded Image")

        max_size = 1200
        image.thumbnail((max_size, max_size))
        image_np = np.array(image)

        with st.spinner("Loading OCR model..."):
            ocr = load_model()

        with st.spinner("Extracting text..."):
            result = ocr.predict(image_np)

        final_res = []
        for page in result:
            final_res.extend(page.get("rec_texts", []))

        ocr_text = " ".join(final_res).strip()

        if not ocr_text:
            st.error("No readable text was found in the uploaded image.")
        else:
            if api_key:
                try:
                    with st.spinner("Analyzing medicine..."):
                        response = Generatetxt(
                            prompt(
                                "The following text has been extracted from a medicine strip using OCR.",
                                ocr_text,
                            ),
                            api_key=api_key,
                        )
                    st.text_area("AI Result", response, height=300)

                except Exception as exc:
                    st.error(f"AI generation failed: {exc}")
            else:
                st.error("Add APIKEY to use AI text generation.")
locatestore()