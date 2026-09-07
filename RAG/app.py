# import streamlit as st
# from rag import ask_question

# # ---------------- Page Config ---------------- #
# st.set_page_config(
#     page_title="Financial RAG Assistant",
#     page_icon="📊",
#     layout="wide"
# )

# # ---------------- Sidebar ---------------- #
# with st.sidebar:
#     st.title("📊 Finance RAG")

#     st.markdown("---")

#     st.subheader("📁 Loaded Sheets")
#     st.write("✅ Historical FS")
#     st.write("✅ WACC")
#     st.write("✅ DCF")
#     st.write("✅ Comparable Pricing")

#     st.markdown("---")

#     st.subheader("🛠 Tech Stack")
#     st.write("• Python")
#     st.write("• Streamlit")
#     st.write("• FAISS")
#     st.write("• HuggingFace Embeddings")
#     st.write("• Gemini 2.5 Flash")

#     st.markdown("---")

#     if st.button("🗑 Clear Chat"):
#         st.session_state.messages = []
#         st.rerun()

# # ---------------- Header ---------------- #
# st.title("📊 Financial Modelling & Valuation AI Assistant")

# st.caption(
#     "Chat with an Excel Financial Model using Retrieval-Augmented Generation (RAG)"
# )

# st.info(
#     """
# **Example Questions**

# • What is WACC?

# • Explain the DCF valuation.

# • How is Enterprise Value calculated?

# • Which companies are used for comparable valuation?

# • What assumptions drive the forecast?
# """
# )

# # ---------------- Chat History ---------------- #
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:

#     avatar = "🧑" if message["role"] == "user" else "🤖"

#     with st.chat_message(message["role"], avatar=avatar):
#         st.markdown(message["content"])

# # ---------------- User Input ---------------- #
# question = st.chat_input("Ask anything about the financial model...")

# if question:

#     # Display User Message
#     st.session_state.messages.append(
#         {
#             "role": "user",
#             "content": question
#         }
#     )

#     with st.chat_message("user", avatar="🧑"):
#         st.markdown(question)

#     # AI Response
#     with st.chat_message("assistant", avatar="🤖"):

#         with st.spinner("Searching financial model..."):

#             answer = ask_question(question)

#         st.markdown(answer)

#     st.session_state.messages.append(
#         {
#             "role": "assistant",
#             "content": answer
#         }
#     )

# # ---------------- Footer ---------------- #
# st.markdown("---")

# st.caption(
#     "Built using Python • FAISS • HuggingFace • Gemini • Streamlit"
# )

import os
import re
import tempfile

import streamlit as st

from rag import ask_question
from ingest import ingest_excel
from vector_store import build_vector_store


# ---------------- Metric Extraction ---------------- #

def extract_metrics(answer):

    metrics = {}

    patterns = {
        "WACC": r"WACC.*?([0-9]+\.?[0-9]*%?)",
        "Enterprise Value": r"Enterprise Value.*?([0-9,]+\.?[0-9]*)",
        "Equity Value": r"Equity Value.*?([0-9,]+\.?[0-9]*)",
        "Value per Share": r"Value per Share.*?([0-9,]+\.?[0-9]*)"
    }

    for key, pattern in patterns.items():

        match = re.search(pattern, answer, re.IGNORECASE)

        if match:

            value = match.group(1)

            if key == "WACC":

                try:

                    if "%" not in value:

                        num = float(value)

                        if num < 1:
                            value = f"{num * 100:.2f}%"

                except:
                    pass

            metrics[key] = value

    return metrics


# ---------------- Page Config ---------------- #

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📊",
    layout="wide"
)


# ---------------- Session State ---------------- #

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_index" not in st.session_state:
    st.session_state.active_index = "faiss_index"

if "loaded_sheets" not in st.session_state:
    st.session_state.loaded_sheets = [
        "Historical FS",
        "WACC",
        "DCF",
        "Comparable Pricing"
    ]

if "uploaded_done" not in st.session_state:
    st.session_state.uploaded_done = False


# ---------------- Sidebar ---------------- #

with st.sidebar:

    st.title("📊 Finance RAG")

    uploaded_file = st.file_uploader(
        "Upload Financial Model",
        type=["xlsx"]
    )

    if uploaded_file is not None and not st.session_state.uploaded_done:

        with st.spinner("Processing Workbook..."):

            temp_dir = tempfile.mkdtemp()

            excel_path = os.path.join(
                temp_dir,
                uploaded_file.name
            )

            with open(excel_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            sheets = ingest_excel(
                excel_path,
                output_folder="uploaded_docs"
            )

            build_vector_store(
                docs_folder="uploaded_docs",
                index_folder="uploaded_index"
            )

            st.session_state.active_index = "uploaded_index"
            st.session_state.loaded_sheets = sheets
            st.session_state.uploaded_done = True

        st.success("Workbook Loaded Successfully")

    st.markdown("---")

    st.subheader("📁 Loaded Sheets")

    for sheet in st.session_state.loaded_sheets:
        st.write(f"✅ {sheet}")

    st.markdown("---")

    st.subheader("🛠 Tech Stack")

    st.write("• Python")
    st.write("• Streamlit")
    st.write("• FAISS")
    st.write("• HuggingFace")
    st.write("• Gemini")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []
        st.rerun()

# ---------------- Header ---------------- #

st.title("📊 Financial Modelling & Valuation AI Assistant")

st.caption(
    "Chat with an Excel Financial Model using Retrieval-Augmented Generation (RAG)"
)

st.info(
"""
### Example Questions

• What is WACC?

• Explain the DCF Valuation.

• How is Enterprise Value calculated?

• Which companies are used for Comparable Valuation?

• What assumptions drive the forecast?
"""
)


# ---------------- Chat History ---------------- #

for message in st.session_state.messages:

    avatar = "🧑" if message["role"] == "user" else "🤖"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )


# ---------------- User Input ---------------- #

question = st.chat_input(
    "Ask anything about the financial model..."
)

if question:

    # Save User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message(
        "user",
        avatar="🧑"
    ):

        st.markdown(question)

    # Assistant

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner(
            "Analyzing Financial Model..."
        ):

            result = ask_question(
                question,
                index_folder=st.session_state.active_index
            )

        # -------- KPI Cards -------- #

        metrics = extract_metrics(
            result["answer"]
        )

        if metrics:

            cols = st.columns(
                len(metrics)
            )

            for col, (name, value) in zip(
                cols,
                metrics.items()
            ):

                col.metric(
                    label=name,
                    value=value
                )

        # -------- AI Answer -------- #

        st.markdown(
            result["answer"]
        )

        # -------- Sources -------- #

        if result["sources"]:

            st.markdown("---")

            st.markdown(
                "### 📄 Sources Used"
            )

            cols = st.columns(
                len(result["sources"])
            )

            for col, source in zip(
                cols,
                result["sources"]
            ):

                source = (
                    source
                    .replace(".txt", "")
                    .replace("_", " ")
                )

                col.success(source)

    # Save Assistant Message

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"]
        }
    )
# ---------------- Footer ---------------- #

st.markdown("---")

st.caption(
    "Built using Python • Streamlit • FAISS • HuggingFace • Gemini"
)


# ---------------- Upload Controls ---------------- #

with st.sidebar:

    st.markdown("---")

    if st.session_state.active_index == "uploaded_index":

        st.success("🟢 Using Uploaded Financial Model")

        if st.button("🗑 Remove Uploaded Workbook"):

            # Reset to default model
            st.session_state.active_index = "faiss_index"

            st.session_state.loaded_sheets = [
                "Historical FS",
                "WACC",
                "DCF",
                "Comparable Pricing"
            ]

            st.session_state.uploaded_done = False

            # Delete uploaded docs
            if os.path.exists("uploaded_docs"):

                for file in os.listdir("uploaded_docs"):

                    os.remove(
                        os.path.join(
                            "uploaded_docs",
                            file
                        )
                    )

            # Delete uploaded index
            if os.path.exists("uploaded_index"):

                for file in os.listdir("uploaded_index"):

                    os.remove(
                        os.path.join(
                            "uploaded_index",
                            file
                        )
                    )

                os.rmdir("uploaded_index")

            st.success("Default Financial Model Restored")

            st.rerun()

    else:

        st.info("📘 Using Default Financial Model")