#!/usr/bin/env python3
"""
System runner for Pakistani Legal Assistant RAG system
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
import threading

class SystemRunner:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def run_command_async(self, command, cwd=None, name="Process"):
        """Run a command asynchronously"""
        try:
            print(f"🚀 Starting {name}...")
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append((process, name))
            
            # Monitor output in a separate thread
            def monitor_output():
                for line in iter(process.stdout.readline, ''):
                    if line.strip():
                        print(f"[{name}] {line.strip()}")
                process.stdout.close()
            
            thread = threading.Thread(target=monitor_output)
            thread.daemon = True
            thread.start()
            
            return process
            
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
            return None
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down system...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up all processes"""
        for process, name in self.processes:
            if process.poll() is None:
                print(f"🔄 Stopping {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"⚠️ Error stopping {name}: {e}")
    
    def check_env_file(self):
        """Check if .env file exists and has required variables"""
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file not found. Please run setup.py first.")
            return False
        
        required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
        missing_vars = []
        
        with open(env_file, 'r') as f:
            content = f.read()
            for var in required_vars:
                if f"{var}=your_" in content or f"{var}=" not in content:
                    missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Please set the following environment variables in .env:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        
        return True
    
    def check_data_file(self):
        """Check if data file exists"""
        data_file = Path("pdf_data.json")
        if not data_file.exists():
            print("❌ pdf_data.json not found. Please ensure the data file is in the project root.")
            return False
        return True
    
    def run_system(self):
        """Run the complete system"""
        print("🏛️ Pakistani Legal Assistant RAG System")
        print("=" * 50)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check prerequisites
        if not self.check_env_file():
            return False
        
        if not self.check_data_file():
            return False
        
        # Check if backend virtual environment exists
        backend_dir = Path("backend")
        if os.name == 'nt':  # Windows
            python_path = backend_dir / "venv" / "Scripts" / "python"
            if not python_path.exists():
                python_path = "python"
        else:  # Unix/Linux/Mac
            python_path = backend_dir / "venv" / "bin" / "python"
            if not python_path.exists():
                python_path = "python"
        
        # Start backend
        backend_cmd = f"{python_path} -m uvicorn app.main:app --reload --port 8000"
        backend_process = self.run_command_async(
            backend_cmd, 
            cwd=backend_dir, 
            name="Backend API"
        )
        
        if not backend_process:
            return False
        
        # Wait a bit for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # Start frontend
        frontend_dir = Path("frontend")
        frontend_cmd = "npm start"
        frontend_process = self.run_command_async(
            frontend_cmd, 
            cwd=frontend_dir, 
            name="Frontend"
        )
        
        if not frontend_process:
            return False
        
        print("\n✅ System started successfully!")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n💡 Press Ctrl+C to stop the system")
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                for process, name in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️ {name} has stopped unexpectedly")
                        
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """Main function"""
    runner = SystemRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Pakistani Legal Assistant RAG System Runner")
        print("\nUsage:")
        print("  python run_system.py          # Start the complete system")
        print("  python run_system.py --help   # Show this help")
        print("\nPrerequisites:")
        print("  1. Run setup.py first")
        print("  2. Configure .env file")
        print("  3. Set up Supabase database")
        print("  4. Run data ingestion (backend/run_ingest.py)")
        return
    
    try:
        success = runner.run_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()