#!/usr/bin/env python3
"""
Crash Monitor Tool - Quick Crash Detection and Analysis

Starts the spaceship app with detailed timing and crash detection.
Monitors process lifecycle, captures crash info, and provides timing data.
"""

import subprocess
import time
import sys
import os
from datetime import datetime
import threading
import requests
import psutil


class AppCrashMonitor:
    def __init__(self):
        self.start_time = None
        self.process = None
        self.crash_detected = False
        self.mcp_responsive = False
        self.crash_time = None
        self.last_check_time = None
        
    def monitor_mcp_health(self):
        """Monitor MCP server health in background"""
        while self.process and self.process.poll() is None:
            try:
                response = requests.get('http://localhost:8765/health', timeout=2)
                if response.status_code == 200:
                    if not self.mcp_responsive:
                        elapsed = time.time() - self.start_time
                        print(f"✅ MCP server responsive after {elapsed:.2f}s")
                        self.mcp_responsive = True
                else:
                    print(f"⚠️ MCP server returned {response.status_code}")
            except Exception:
                # MCP not ready yet or crashed
                pass
                
            time.sleep(1)
            
    def run_crash_test(self):
        """Run app with crash monitoring"""
        print("🔍 CRASH MONITOR STARTING")
        print("=" * 50)
        
        # Start the application
        self.start_time = time.time()
        start_dt = datetime.now()
        
        print(f"⏱️ Start Time: {start_dt.strftime('%H:%M:%S.%f')[:-3]}")
        print("🚀 Launching spaceship application...")
        
        # Use venv python path
        python_path = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe"
        
        try:
            self.process = subprocess.Popen(
                [python_path, "spaceship.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            print(f"📊 Process ID: {self.process.pid}")
            
            # Start MCP monitoring thread
            mcp_thread = threading.Thread(target=self.monitor_mcp_health, daemon=True)
            mcp_thread.start()
            
            # Monitor process with detailed timing
            check_interval = 0.5  # Check every 500ms
            next_milestone = 5    # Next milestone to report
            
            while True:
                # Check if process is still running
                return_code = self.process.poll()
                current_time = time.time()
                elapsed = current_time - self.start_time
                
                # Report milestones
                if elapsed >= next_milestone:
                    print(f"⏱️ Running for {elapsed:.1f}s - Process healthy")
                    next_milestone += 5
                
                if return_code is not None:
                    # Process has terminated
                    self.crash_time = elapsed
                    crash_dt = datetime.now()
                    
                    print("\n" + "=" * 50)
                    print("💥 APPLICATION TERMINATED!")
                    print(f"⏱️ Crash Time: {crash_dt.strftime('%H:%M:%S.%f')[:-3]}")
                    print(f"⏱️ Runtime: {elapsed:.2f} seconds")
                    print(f"📊 Exit Code: {return_code}")
                    print(f"🔌 MCP was responsive: {self.mcp_responsive}")
                    
                    # Get final output
                    try:
                        stdout, stderr = self.process.communicate(timeout=2)
                        if stdout:
                            print("\n📋 STDOUT (last 1000 chars):")
                            print("-" * 30)
                            print(stdout[-1000:])
                        if stderr:
                            print("\n❌ STDERR:")
                            print("-" * 30)
                            print(stderr[-1000:])
                    except subprocess.TimeoutExpired:
                        print("⚠️ Could not retrieve final output (timeout)")
                    
                    break
                    
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            if self.process:
                self.process.terminate()
                
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
            
        finally:
            # Cleanup
            if self.process and self.process.poll() is None:
                print("🧹 Terminating process...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("🔨 Force killing process...")
                    self.process.kill()
                    
    def quick_crash_test(self, iterations=3):
        """Run multiple quick crash tests to identify patterns"""
        print("🔄 RUNNING MULTIPLE CRASH TESTS")
        print("=" * 50)
        
        crash_times = []
        
        for i in range(iterations):
            print(f"\n🧪 Test {i+1}/{iterations}")
            print("-" * 30)
            
            self.run_crash_test()
            
            if self.crash_time:
                crash_times.append(self.crash_time)
                print(f"💥 Test {i+1} crashed after {self.crash_time:.2f}s")
            else:
                print(f"✅ Test {i+1} completed successfully")
                
            # Reset for next test
            self.start_time = None
            self.process = None
            self.crash_detected = False
            self.mcp_responsive = False
            self.crash_time = None
            
            # Wait between tests
            if i < iterations - 1:
                print("⏳ Waiting 3 seconds before next test...")
                time.sleep(3)
                
        # Analysis
        print("\n" + "=" * 50)
        print("📊 CRASH ANALYSIS")
        print("=" * 50)
        
        if crash_times:
            avg_crash_time = sum(crash_times) / len(crash_times)
            min_crash_time = min(crash_times)
            max_crash_time = max(crash_times)
            
            print(f"💥 Crashes detected: {len(crash_times)}/{iterations}")
            print(f"⏱️ Average crash time: {avg_crash_time:.2f}s")
            print(f"⏱️ Fastest crash: {min_crash_time:.2f}s")
            print(f"⏱️ Slowest crash: {max_crash_time:.2f}s")
            
            if max_crash_time - min_crash_time < 2:
                print("🎯 CONSISTENT crash timing suggests specific trigger!")
            else:
                print("⚠️ Variable crash timing suggests resource/timing issue")
                
        else:
            print("✅ No crashes detected in any test!")


def main():
    """Main crash monitoring function"""
    monitor = AppCrashMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Run quick multiple tests
        iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        monitor.quick_crash_test(iterations)
    else:
        # Run single detailed test
        monitor.run_crash_test()


if __name__ == "__main__":
    main()