import streamlit as st
import sys
import os
import asyncio

# Add backend to path so we can import its modules seamlessly
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import backend logic
from backend.services.local_image_gen import generate_fashion_image_b64
from backend.services.image_generator import get_style_attributes

st.set_page_config(page_title="AI Fashion Studio", page_icon="👗", layout="wide")

st.title("✨ AI Fashion Studio")
st.markdown("Generate custom fashion designs instantly using our AI.")

# Initialize session state for image
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "style_tags" not in st.session_state:
    st.session_state.style_tags = None

with st.form("design_form"):
    prompt = st.text_area(
        "Describe your dream outfit:",
        placeholder="A midnight blue silk evening gown with silver embroidery, elegant..."
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        submit_btn = st.form_submit_button("Generate Design 🎨", use_container_width=True)

if submit_btn and prompt:
    if len(prompt.strip()) < 5:
        st.warning("Please provide a more detailed description (at least 5 characters).")
    else:
        with st.spinner("Our AI is creating your design..."):
            try:
                # Run the async generation function
                image_b64 = asyncio.run(asyncio.to_thread(
                    generate_fashion_image_b64,
                    prompt,
                    512, 768
                ))
                
                # Strip the data URI prefix to get raw base64
                if image_b64.startswith("data:image"):
                    image_b64 = image_b64.split(",")[1]
                
                # Get style tags
                try:
                    tags = get_style_attributes(prompt)
                except Exception:
                    tags = {}
                
                st.session_state.generated_image = image_b64
                st.session_state.style_tags = tags
                
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

# Display results
if st.session_state.generated_image:
    st.divider()
    st.subheader("Your Custom Design")
    
    col_img, col_details = st.columns([1, 1])
    
    with col_img:
        import base64
        image_bytes = base64.b64decode(st.session_state.generated_image)
        st.image(image_bytes, use_container_width=True)
        
    with col_details:
        st.markdown("### Design Attributes")
        tags = st.session_state.style_tags
        
        if tags and isinstance(tags, dict):
            if "category" in tags:
                st.markdown(f"**Category:** {tags['category'].title()}")
            if "colors" in tags and tags["colors"]:
                st.markdown(f"**Colors:** {', '.join(tags['colors']).title()}")
            if "style" in tags and tags["style"]:
                st.markdown(f"**Style:** {', '.join(tags['style']).title()}")
        else:
            st.markdown("No specific attributes detected.")
            
        st.info("💡 **Tip:** This Streamlit app connects directly to the core AI generation engine of the Ai-Fashion platform.")
