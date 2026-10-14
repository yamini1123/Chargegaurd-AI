# app.py
import os
import json
import time
import codecs
import streamlit as st
from agent import process_chargeback
from pdf_generator import create_pdf
from eval_engine import run_benchmark

# Must be the first Streamlit command
st.set_page_config(page_title="ChargeGuard AI", page_icon="🛡️", layout="wide")

# Custom CSS for a premium B2B look
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 2rem; }
    .card { background-color: #F8FAFC; padding: 1.5rem; border-radius: 10px; border: 1px solid #E2E8F0; }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #0F172A; }
    .stButton>button { background-color: #1E3A8A; color: white; border-radius: 8px; padding: 0.5rem 2rem; font-weight: bold; width: 100%;}
    .stButton>button:hover { background-color: #1E40AF; border-color: #1E40AF; }
    </style>
""", unsafe_allow_html=True)

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mock_db.json")

# App Header
st.markdown('<p class="main-header">🛡️ ChargeGuard AI Sentinel</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automated Chargeback Defense & Representment Generation Engine</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡ Live Auto-Responder", "📊 Model Benchmark & ROI"])


def sanitize_llm_markdown(text: str) -> str:
    """Decodes escaped newline strings and scales down giant H1 headers."""
    if not text:
        return ""
    
    # 1. Decode all escaped backslash sequences (e.g. \\n -> \n)
    try:
        # Converts literal '\\n' strings into actual control newlines
        text = text.encode('raw_unicode_escape').decode('unicode_escape')
    except Exception:
        text = text.replace('\\n', '\n').replace(r'\n', '\n')
    
    # 2. Fallback manual replace pass
    text = text.replace('\\n', '\n').replace(r'\n', '\n')
    
    # 3. Prevent giant headers: convert top-level '# ' (H1) and '## ' (H2) to '### ' (H3)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# '):
            line = '### ' + stripped[2:]
        elif stripped.startswith('## '):
            line = '### ' + stripped[3:]
        cleaned_lines.append(line)
        
    return '\n'.join(cleaned_lines)

# ==================== TAB 1: LIVE DEMO ====================
with tab1:

    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            disputes = json.load(f)
            
        st.sidebar.markdown("### 📥 Incoming Webhooks")
        st.sidebar.caption("Select a dispute to review:")
        dispute_ids = [d["dispute_id"] for d in disputes]
        selected_id = st.sidebar.selectbox("", dispute_ids, label_visibility="collapsed")
        
        selected_dispute = next(d for d in disputes if d["dispute_id"] == selected_id)

        col1, col2 = st.columns([1.2, 1])

        # Left Column: Structured Data Presentation (No more raw JSON)
        with col1:
            st.subheader("📋 Dispute Case Details")
            with st.container(border=True):
                st.markdown(f"**Order ID:** `{selected_dispute.get('order_id', 'N/A')}` | **Amount:** `₹{selected_dispute.get('disputed_amount', 0):,.2f}`")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("🔒 Payment Verification")
                    st.write(f"**AVS Match:** {selected_dispute.get('avs_match', 'N/A')}")
                    st.write(f"**CVC Match:** {selected_dispute.get('cvc_match', 'N/A')}")
                    st.write(f"**IP Distance:** {selected_dispute.get('ip_distance_km', 'N/A')} km")
                with c2:
                    st.caption("📦 Fulfillment")
                    st.write(f"**Status:** {selected_dispute.get('delivery_status', 'N/A')}")
                    st.write(f"**Carrier:** {selected_dispute.get('carrier', 'N/A')}")
                
                st.divider()
                st.caption("💬 Customer Support Log")
                st.info(f'"{selected_dispute.get("chat_history", "No chat history available.")}"')

        # Right Column: AI Action Engine
        with col2:
            st.subheader("🤖 AI Decision Engine")
            with st.container(border=True):
                st.markdown("Ready to cross-reference payment, logistics, and communication logs.")
                if st.button("🚀 Analyze Evidence & Generate Response"):
                    
                    # Simulated UI Progress for demo "wow" factor
                    progress_text = "Parsing logistics and payment datasets..."
                    my_bar = st.progress(0, text=progress_text)
                    time.sleep(0.5)
                    my_bar.progress(40, text="Evaluating fraud vectors via Gemini...")
                    time.sleep(0.5)
                    my_bar.progress(80, text="Drafting bank-compliant legal representment...")
                    time.sleep(0.5)
                    my_bar.progress(100, text="Complete!")
                    time.sleep(0.3)
                    my_bar.empty()
                    
                    with st.spinner("Finalizing document..."):
                        result = process_chargeback(selected_dispute)
                        
                        if result['recommendation'] == "FIGHT":
                            st.success(f"**Recommendation:** FIGHT DISPUTE (Confidence: {result['confidence_score']}%)")
                            
                            # Clean and re-format the text safely
                            clean_letter = sanitize_llm_markdown(result['letter_text'])
                            
                            with st.expander("📄 View Drafted Bank Letter", expanded=True):
                                st.markdown(clean_letter)  # Clean, normal font size
                                
                            # Generate PDF using the cleaned letter
                            pdf_path = create_pdf(clean_letter)
                            with open(pdf_path, "rb") as f:
                                st.download_button("📥 Download PDF Packet", f, file_name=f"{selected_id}_Packet.pdf", type="primary")
                        else:
                            st.error(f"**Recommendation:** ACCEPT DISPUTE (Confidence: {result['confidence_score']}%)")
                            st.warning("Decision: True Fraud identified. Auto-submitting this dispute would result in lost processing fees.")
    else:
        st.error("mock_db.json not found! Run python dataset.py first.")

# ==================== TAB 2: BENCHMARK & ROI ====================
with tab2:
    st.markdown("### 📈 Evaluation on Held-Out Test Set (50 Cases)")
    st.caption("Measuring Precision, Recall, and False-Positive Cost Reduction against a naive baseline rule engine.")
    
    if st.button("🚀 Run Live Benchmark Evaluation", key="run_eval"):
        with st.spinner("Evaluating model against 50 held-out edge cases..."):
            metrics = run_benchmark()
            
            # Stylized Metric Layout
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.info(f"**Precision**\n## {metrics['precision']}%")
            with m_col2:
                st.info(f"**Recall**\n## {metrics['recall']}%")
            with m_col3:
                st.info(f"**Accuracy**\n## {metrics['accuracy']}%")
            with m_col4:
                st.success(f"**FPC Saved**\n## ₹{metrics['cost_savings']:,.0f}")
            
            st.divider()
            
            st.markdown("#### 🔍 Confusion Matrix Breakdown")
            cm_col1, cm_col2 = st.columns(2)
            with cm_col1:
                with st.container(border=True):
                    st.markdown(f"✅ **True Positives (Winnable - Fought):** `{metrics['tp']}`")
                    st.markdown(f"❌ **False Positives (True Fraud - Wasted Fee):** `{metrics['fp']}`")
            with cm_col2:
                with st.container(border=True):
                    st.markdown(f"🛡️ **True Negatives (True Fraud - Fee Saved):** `{metrics['tn']}`")
                    st.markdown(f"⚠️ **False Negatives (Winnable - Missed):** `{metrics['fn']}`")
                
            st.divider()
            st.markdown("#### 📜 Detailed Evaluation Log")
            st.dataframe(metrics['results_table'], use_container_width=True, hide_index=True)