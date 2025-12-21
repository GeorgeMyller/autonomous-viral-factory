import streamlit as st
import sys
import os
import time
from autonomous_crew import AutonomousViralFactory

# Disable CrewAI Telemetry to fix "signal only works in main thread" error
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["CREWAI_TRACING_ENABLED"] = "false"

# Page Config
st.set_page_config(
    page_title="Autonomous Viral Factory",
    page_icon="🎬",
    layout="wide"
)

# Title and Description
st.title("🎬 Autonomous Viral Factory")
st.markdown("Generate viral shorts from YouTube trends automatically.")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    niche_topic = st.text_input("Niche / Topic", value="Artificial Intelligence News")
    
    st.divider()
    
    st.subheader("Brain (LLM)")
    llm_provider = st.selectbox("Provider", ["openai", "gemini", "ollama"], index=0)
    
    default_models = {
        "openai": "gpt-4o",
        "gemini": "gemini-2.0-flash",
        "ollama": "qwen3:14b"
    }
    
    # Dynamic model selection based on provider
    if llm_provider == "ollama":
        # Try to fetch available Ollama models
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                ollama_models = [m["name"] for m in response.json().get("models", [])]
                if ollama_models:
                    # Use selectbox with key - Streamlit manages state automatically
                    # Initialize default in session state if needed
                    if "selected_ollama_model" not in st.session_state:
                        if default_models["ollama"] in ollama_models:
                            st.session_state.selected_ollama_model = default_models["ollama"]
                        else:
                            st.session_state.selected_ollama_model = ollama_models[0]
                    
                    # Get default index for initial render
                    try:
                        default_idx = ollama_models.index(st.session_state.selected_ollama_model)
                    except ValueError:
                        default_idx = 0
                    
                    # Simple selectbox - let Streamlit handle state via return value
                    model_name = st.selectbox(
                        "Select Ollama Model", 
                        options=ollama_models, 
                        index=default_idx
                    )
                    # Store selection for next run
                    st.session_state.selected_ollama_model = model_name
                else:
                    st.warning("No models found. Run `ollama pull <model>` first.")
                    model_name = st.text_input("Model Name", value=default_models["ollama"])
            else:
                st.warning("Could not connect to Ollama.")
                model_name = st.text_input("Model Name", value=default_models["ollama"])
        except requests.exceptions.RequestException:
            st.warning("Ollama is not running. Start with `ollama serve`.")
            model_name = st.text_input("Model Name", value=default_models["ollama"])
        
        st.caption("Ensure Ollama is running (`ollama serve`).")
    elif llm_provider == "gemini":
        model_name = st.text_input("Model Name", value=default_models.get(llm_provider, "gemini-2.0-flash"))
        st.caption("Ensure `GOOGLE_API_KEY` is in `.env`.")
    else:
        model_name = st.text_input("Model Name", value=default_models.get(llm_provider, "gpt-4o"))

    st.info("The agent will scout trends, analyze transcripts, and create a clip.")

# Main Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Operations")
    start_btn = st.button("🚀 Start Factory", type="primary")
    
    status_container = st.container()
    
    if start_btn:
        with st.status("Factory is running...", expanded=True) as status:
            st.write("Initializing agents...")
            
            # Capture stdout using a simple wrapper or just let it print to terminal
            # Ideally we would capture logs, but for now let's just run it.
            # We can use st.empty() to show progress if we modify crew to yield updates.
            # For this MVC, we'll just run it and show the result.
            
            try:
                factory = AutonomousViralFactory(llm_provider=llm_provider, model_name=model_name)
                st.write(f"🔎 Scouting trends using **{llm_provider}** ({model_name})...")
                # We could break down factory.run() into steps if we refactored, 
                # but let's run the whole thing.
                
                result, log_file = factory.run(niche_topic)
                
                status.update(label="Process Complete!", state="complete", expanded=False)
                
                st.success("Video Generated Successfully!")
                st.info(f"Execution logs saved to: `{log_file}`")
                
                # Setup download button for logs
                if os.path.exists(log_file):
                    with open(log_file, "rb") as f:
                        st.download_button(
                            label="Download Execution Logs",
                            data=f,
                            file_name=os.path.basename(log_file),
                            mime="text/plain"
                        )
                
                # The result from crew usually is the output of the last task.
                # Our last task returns "Path to the final viral clip file."
                # Let's hope the agent returns the clean path.
                
                # Clean up result string if needed (remove quotes, etc)
                result_str = str(result).strip().strip("'").strip('"')
                
                # Try to parse as JSON array for multiple clips
                video_paths = []
                try:
                    import json
                    parsed = json.loads(result_str)
                    if isinstance(parsed, list):
                        video_paths = [p for p in parsed if os.path.exists(p)]
                except:
                    # Not JSON, try as single path
                    if os.path.exists(result_str):
                        video_paths = [result_str]
                
                # Fallback: scan output folder for recent clips
                if not video_paths:
                    try:
                        list_of_files = os.listdir('output')
                        full_paths = [os.path.join('output', x) for x in list_of_files if x.endswith('.mp4')]
                        if full_paths:
                            # Sort by creation time, newest first
                            full_paths.sort(key=os.path.getctime, reverse=True)
                            # Take clips created in the last 10 minutes
                            import time
                            recent_cutoff = time.time() - 600  # 10 minutes
                            video_paths = [p for p in full_paths if os.path.getctime(p) > recent_cutoff]
                            if video_paths:
                                st.warning(f"Found {len(video_paths)} recent clips in output folder")
                    except Exception as e:
                        st.error(f"Error scanning output folder: {e}")
                
                if video_paths:
                    st.session_state['video_paths'] = video_paths
                else:
                    st.error(f"No video files found. Result was: {result_str[:200]}")
                        
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")

with col2:
    st.subheader("Results")
    if 'video_paths' in st.session_state and st.session_state['video_paths']:
        video_paths = st.session_state['video_paths']
        st.success(f"🎬 Generated {len(video_paths)} viral clip(s)!")
        
        for i, video_path in enumerate(video_paths, 1):
            with st.expander(f"Clip {i}: {os.path.basename(video_path)}", expanded=(i == 1)):
                st.video(video_path)
                
                with open(video_path, "rb") as file:
                    st.download_button(
                        label=f"⬇️ Download Clip {i}",
                        data=file,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4",
                        key=f"download_{i}"
                    )
    elif 'video_path' in st.session_state:
        # Legacy single video support
        video_path = st.session_state['video_path']
        st.video(video_path)
        st.caption(f"Playing: {os.path.basename(video_path)}")
        
        with open(video_path, "rb") as file:
            btn = st.download_button(
                label="Download Video",
                data=file,
                file_name=os.path.basename(video_path),
                mime="video/mp4"
            )
    else:
        st.info("Run the factory to see the results here.")

# Footer
st.markdown("---")
st.markdown("Powered by CrewAI, MoviePy, & Streamlit")

