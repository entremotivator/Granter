import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    requirements = [
        "streamlit",
        "pandas", 
        "plotly",
        "requests",
        "numpy"
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def run_streamlit():
    """Run the Streamlit dashboard"""
    try:
        # Install requirements first
        print("Installing required packages...")
        install_requirements()
        
        # Run Streamlit app
        print("\n🚀 Starting Streamlit dashboard...")
        print("Dashboard will open at: http://localhost:8501")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "scripts/streamlit_grants_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

if __name__ == "__main__":
    run_streamlit()
