#!/usr/bin/env python3
"""
Virtual Microphone Audio Delay Tool
Creates a virtual microphone with delayed audio for recording software like Camtasia
"""

import pyaudio
import numpy as np
from collections import deque
import argparse
import sys
import threading
import time
from typing import Optional
import signal
import atexit


def _get_device_name(device_index: Optional[int], direction: str = "input") -> str:
    """Return human-readable device name for a given index.

    If ``device_index`` is ``None``, attempts to resolve the default device
    name for the given ``direction`` ("input" or "output"). Falls back to
    "Default" if not available. If the index is invalid, returns a safe
    placeholder containing the index.

    Args:
        device_index: PyAudio device index or None for default.
        direction: "input" or "output" to resolve default device when needed.

    Returns:
        The device name string.
    """
    p = pyaudio.PyAudio()
    try:
        if device_index is None:
            try:
                info = (
                    p.get_default_input_device_info()
                    if direction == "input"
                    else p.get_default_output_device_info()
                )
                return info.get("name", "Default")
            except Exception:
                return "Default"
        # Specific index provided
        try:
            info = p.get_device_info_by_index(device_index)
            return info.get("name", f"Device {device_index}")
        except Exception:
            return f"Device {device_index}"
    finally:
        p.terminate()


def _get_default_device_index(direction: str = "input") -> Optional[int]:
    """Return the default device index for the given direction if available.

    Args:
        direction: "input" or "output".

    Returns:
        The device index or None if not available.
    """
    p = pyaudio.PyAudio()
    try:
        try:
            info = (
                p.get_default_input_device_info()
                if direction == "input"
                else p.get_default_output_device_info()
            )
            return int(info.get("index")) if "index" in info else None
        except Exception:
            return None
    finally:
        p.terminate()

class VirtualMicrophone:
    """Virtual microphone with proper cleanup and thread management"""
    
    def __init__(self, delay_ms=200, sample_rate=44100, chunk_size=1024,
                 input_device=None, output_device=None):
        self.delay_ms = delay_ms
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.input_device = input_device
        self.output_device = output_device
        
        # Threading control
        self._stop_event = threading.Event()
        self._audio_thread = None
        
        # Audio components
        self._pa = None
        self._input_stream = None
        self._output_stream = None
        
        # Calculate buffer size needed for delay
        delay_samples = int(delay_ms * sample_rate / 1000)
        self._delay_buffer = deque([0.0] * delay_samples, maxlen=delay_samples)
    
    def _process_audio(self):
        """Process audio in separate thread with proper cleanup"""
        try:
            self._pa = pyaudio.PyAudio()
            
            # Input stream (physical microphone)
            self._input_stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.input_device
            )
            
            # Output stream (virtual audio device)
            self._output_stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                output_device_index=self.output_device
            )
            
            print("🎤 Virtual microphone active - audio processing started")
            
            while not self._stop_event.is_set():
                try:
                    # Read from physical microphone with timeout
                    input_data = self._input_stream.read(
                        self.chunk_size, 
                        exception_on_overflow=False
                    )
                    
                    if self._stop_event.is_set():
                        break
                        
                    input_audio = np.frombuffer(input_data, dtype=np.float32)
                    
                    # Process through delay buffer
                    output_audio = np.zeros_like(input_audio)
                    for i, sample in enumerate(input_audio):
                        self._delay_buffer.append(sample)
                        output_audio[i] = self._delay_buffer[0]
                    
                    # Write to virtual audio device
                    if not self._stop_event.is_set():
                        self._output_stream.write(output_audio.tobytes())
                        
                except Exception as e:
                    if not self._stop_event.is_set():
                        print(f"❌ Audio processing error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Failed to initialize audio streams: {e}")
        finally:
            self._cleanup_streams()
    
    def _cleanup_streams(self):
        """Safely cleanup audio streams and PyAudio instance"""
        try:
            if self._input_stream:
                try:
                    self._input_stream.stop_stream()
                    self._input_stream.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                self._input_stream = None
                
            if self._output_stream:
                try:
                    self._output_stream.stop_stream()
                    self._output_stream.close()
                except Exception:
                    pass  # Ignore errors during cleanup
                self._output_stream = None
                
            if self._pa:
                try:
                    self._pa.terminate()
                except Exception:
                    pass  # Ignore errors during cleanup
                self._pa = None
                
        except Exception:
            pass  # Ignore any cleanup errors
    
    def start(self):
        """Start the virtual microphone"""
        if self._audio_thread and self._audio_thread.is_alive():
            return False
            
        self._stop_event.clear()
        self._audio_thread = threading.Thread(
            target=self._process_audio,
            name="AudioProcessor",
            daemon=False  # Don't use daemon threads
        )
        self._audio_thread.start()
        return True
    
    def stop(self):
        """Stop the virtual microphone cleanly"""
        if self._audio_thread and self._audio_thread.is_alive():
            self._stop_event.set()
            self._audio_thread.join(timeout=2.0)  # Wait max 2 seconds
            if self._audio_thread.is_alive():
                print("⚠️ Audio thread did not stop cleanly")
        
        self._cleanup_streams()
    
    def is_running(self):
        """Check if the virtual microphone is running"""
        return self._audio_thread and self._audio_thread.is_alive() and not self._stop_event.is_set()

def find_virtual_devices():
    """Find virtual audio devices like VB-Cable"""
    p = pyaudio.PyAudio()
    virtual_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info['name'].lower()
        
        # Look for common virtual audio device names
        virtual_keywords = ['cable', 'virtual', 'vb-audio', 'blackhole', 'loopback']
        if any(keyword in name for keyword in virtual_keywords):
            virtual_devices.append((i, info['name'], info))
    
    p.terminate()
    return virtual_devices

def list_audio_devices():
    """List all audio devices with virtual device highlighting"""
    p = pyaudio.PyAudio()
    
    print("📋 Available audio devices:")
    print("=" * 60)
    
    virtual_devices = []
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info['name']
        inputs = info['maxInputChannels']
        outputs = info['maxOutputChannels']
        
        # Check if it's likely a virtual device
        name_lower = name.lower()
        virtual_keywords = ['cable', 'virtual', 'vb-audio', 'blackhole', 'loopback']
        is_virtual = any(keyword in name_lower for keyword in virtual_keywords)
        
        if is_virtual:
            virtual_devices.append(i)
            print(f"🔊 {i:2d}: {name} (IN:{inputs}, OUT:{outputs}) [VIRTUAL]")
        else:
            print(f"   {i:2d}: {name} (IN:{inputs}, OUT:{outputs})")
    
    print("=" * 60)
    if virtual_devices:
        print(f"✅ Found virtual devices: {virtual_devices}")
        print("💡 Use these device IDs for --output-device")
    else:
        print("⚠️  No virtual audio devices detected")
        print("💡 Install VB-Cable (Windows) or BlackHole (Mac) to create virtual microphones")
    
    p.terminate()

def main():
    parser = argparse.ArgumentParser(description='Virtual microphone with audio delay')
    parser.add_argument('-d', '--delay', type=int, default=200,
                       help='Delay in milliseconds (default: 200ms)')
    parser.add_argument('-r', '--rate', type=int, default=44100,
                       help='Sample rate in Hz (default: 44100)')
    parser.add_argument('-b', '--buffer', type=int, default=1024,
                       help='Buffer size (default: 1024)')
    parser.add_argument('-i', '--input-device', type=int,
                       help='Input device ID (physical microphone)')
    parser.add_argument('-o', '--output-device', type=int,
                       help='Output device ID (virtual audio device)')
    parser.add_argument('--list-devices', action='store_true',
                       help='List available audio devices and exit')
    parser.add_argument('--auto-detect', action='store_true',
                       help='Auto-detect virtual audio devices')
    
    args = parser.parse_args()
    
    if args.list_devices:
        list_audio_devices()
        return
    
    if args.delay < 0:
        print("❌ Delay must be positive")
        sys.exit(1)
    
    # Auto-detect virtual devices if requested
    if args.auto_detect:
        virtual_devices = find_virtual_devices()
        if virtual_devices:
            print("🔍 Auto-detected virtual audio devices:")
            for device_id, name, info in virtual_devices:
                if info['maxOutputChannels'] > 0:
                    print(f"   Device {device_id}: {name}")
                    if args.output_device is None:
                        args.output_device = device_id
                        print(f"   → Using '{name}' as output (ID: {device_id})")
                        break
        
        if args.output_device is None:
            print("❌ No suitable virtual audio device found")
            print("💡 Install VB-Cable or similar virtual audio software")
            sys.exit(1)
    
    # Validate device selection
    if args.output_device is None:
        print("❌ No output device specified")
        print("💡 Use --list-devices to see available devices")
        print("💡 Use --auto-detect to find virtual devices automatically")
        print("💡 Or specify --output-device <ID>")
        sys.exit(1)
    
    print(f"🎤 Setting up virtual microphone")
    input_name = _get_device_name(args.input_device, direction="input")
    output_name = _get_device_name(args.output_device, direction="output")
    input_id = (
        args.input_device
        if args.input_device is not None
        else _get_default_device_index("input")
    )
    output_id = args.output_device
    input_id_label = str(input_id) if input_id is not None else "Default"
    output_id_label = str(output_id) if output_id is not None else "Default"
    print(f"   Input device: {input_name} (ID: {input_id_label})")
    print(f"   Output device: {output_name} (ID: {output_id_label})")
    print(f"   Delay: {args.delay}ms")
    print(f"   Sample rate: {args.rate}Hz")
    print(f"   Buffer size: {args.buffer}")
    print()
    print("🔧 This creates a virtual microphone that Camtasia can select")
    print("📹 In Camtasia, select the virtual audio device as your microphone")
    print("🎯 The delayed audio will be available for recording")
    print("Press Ctrl+C to stop")
    print()
    
    # Create and configure virtual microphone
    virtual_mic = VirtualMicrophone(
        delay_ms=args.delay,
        sample_rate=args.rate,
        chunk_size=args.buffer,
        input_device=args.input_device,
        output_device=args.output_device
    )
    
    # Set up signal handlers for clean shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Stopping virtual microphone...")
        virtual_mic.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Register cleanup function
    atexit.register(virtual_mic.stop)
    
    try:
        # Start the virtual microphone
        if not virtual_mic.start():
            print("❌ Failed to start virtual microphone")
            sys.exit(1)
        
        # Keep main thread alive while virtual microphone is running
        while virtual_mic.is_running():
            time.sleep(0.1)
            
        print("✅ Virtual microphone stopped")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping virtual microphone...")
        virtual_mic.stop()
        print("✅ Virtual microphone stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        virtual_mic.stop()
        print("✅ Virtual microphone stopped")
        sys.exit(1)

if __name__ == "__main__":
    main()
