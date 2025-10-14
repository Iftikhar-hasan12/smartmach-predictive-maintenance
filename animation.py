import streamlit as st
import time

def show_loading_animation(animation_type="single", engine_id=None, total_engines=None):
    """
    Show loading animation without affecting main logic
    
    Parameters:
    - animation_type: "single" for single engine, "all" for all engines
    - engine_id: For single engine loading
    - total_engines: For all engines loading
    """
    
    if animation_type == "single":
        # Single engine loading animation
        with st.spinner(f'🔍 Analyzing Engine {engine_id}...'):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress for better UX
            for i in range(100):
                progress_bar.progress(i + 1)
                
                # Update status text with different stages
                if i < 25:
                    status_text.text("📊 Loading engine data...")
                elif i < 50:
                    status_text.text("🤖 Making RUL prediction...")
                elif i < 75:
                    status_text.text("📡 Analyzing sensor health...")
                else:
                    status_text.text("✅ Generating report...")
                
                time.sleep(0.02)  # Adjust speed as needed
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
    
    elif animation_type == "all":
        # All engines loading animation
        with st.spinner('🔍 Analyzing all engines... This may take a while'):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress for all engines
            for i in range(100):
                progress_bar.progress(i + 1)
                
                # Update status text with different stages
                if i < 20:
                    status_text.text("🔄 Initializing engine analysis...")
                elif i < 40:
                    status_text.text("📈 Processing engine data...")
                elif i < 60:
                    status_text.text("🤖 Running RUL predictions...")
                elif i < 80:
                    status_text.text("📊 Calculating health scores...")
                else:
                    status_text.text("✅ Compiling final report...")
                
                time.sleep(0.1)  # Slightly slower for all engines
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

def show_quick_loading(message="Processing..."):
    """Quick loading spinner without progress bar"""
    return st.spinner(message)