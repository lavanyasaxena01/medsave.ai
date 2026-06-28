import os
import streamlit as st
import easyocr
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
    project_dir = os.path.dirname(__file__)
    model_dir = os.path.join(project_dir, ".easyocr_models")
    user_network_dir = os.path.join(project_dir, ".easyocr_user_network")

    try:
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(user_network_dir, exist_ok=True)
        return easyocr.Reader(
            ["en"],
            gpu=False,
            model_storage_directory=model_dir,
            user_network_directory=user_network_dir,
        )
    except PermissionError:
        backup_dir = os.path.join(project_dir, ".easyocr_models_backup")
        backup_user_dir = os.path.join(project_dir, ".easyocr_user_network_backup")
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(backup_user_dir, exist_ok=True)
        return easyocr.Reader(
            ["en"],
            gpu=False,
            model_storage_directory=backup_dir,
            user_network_directory=backup_user_dir,
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
            result = ocr.readtext(image_np, detail=0, paragraph=True)

        ocr_text = result.strip() if isinstance(result, str) else " ".join(result).strip()

        if not ocr_text:
            st.error("No readable text was found.")
        else:
            if api_key:
                response = Generatetxt(
                    prompt(
                        "The following text has been extracted from a medicine strip using OCR.",
                        ocr_text,
                    ),
                    api_key=api_key,
                )
                st.text_area("AI Result", response, height=300)

            else:
                st.error("APIKEY not configured.")

elif but == "Type Manually":

    medicine = st.text_input("Enter Medicine Name")

    if st.button("Search"):

        if medicine.strip() == "":
            st.warning("Please enter a medicine name.")

        else:

            response = Generatetxt(
                f"""
Medicine Name: {medicine}

Find:
1. Generic Name
2. Jan Aushadhi Equivalent
3. Brand Price
4. Jan Aushadhi Price
5. Savings
6. Savings Percentage
""",
                api_key=api_key,
            )

            st.text_area("Result", response, height=300)

locatestore()
