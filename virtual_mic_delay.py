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

def virtual_microphone_delay(delay_ms=200, sample_rate=44100, chunk_size=1024, 
                           input_device=None, output_device=None):
    """
    Create virtual microphone with delayed audio
    
    Args:
        delay_ms: Delay in milliseconds
        sample_rate: Audio sample rate (Hz)
        chunk_size: Audio buffer size
        input_device: Physical microphone device index
        output_device: Virtual audio device index (like VB-Cable)
    """
    # Calculate buffer size needed for delay
    delay_samples = int(delay_ms * sample_rate / 1000)
    
    # Circular buffer for delay
    delay_buffer = deque([0.0] * delay_samples, maxlen=delay_samples)
    
    p = pyaudio.PyAudio()
    
    def process_audio():
        """Process audio in separate thread"""
        try:
            # Input stream (physical microphone)
            input_stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size,
                input_device_index=input_device
            )
            
            # Output stream (virtual audio device)
            output_stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                output=True,
                frames_per_buffer=chunk_size,
                output_device_index=output_device
            )
            
            print("🎤 Virtual microphone active - audio processing started")
            
            while True:
                # Read from physical microphone
                input_data = input_stream.read(chunk_size, exception_on_overflow=False)
                input_audio = np.frombuffer(input_data, dtype=np.float32)
                
                # Process through delay buffer
                output_audio = np.zeros_like(input_audio)
                for i, sample in enumerate(input_audio):
                    delay_buffer.append(sample)
                    output_audio[i] = delay_buffer[0]
                
                # Write to virtual audio device
                output_stream.write(output_audio.tobytes())
                
        except Exception as e:
            print(f"❌ Audio processing error: {e}")
        finally:
            if 'input_stream' in locals():
                input_stream.stop_stream()
                input_stream.close()
            if 'output_stream' in locals():
                output_stream.stop_stream()
                output_stream.close()
    
    return process_audio, p

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
                        print(f"   → Using device {device_id} as output")
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
    print(f"   Input device: {args.input_device or 'Default'}")
    print(f"   Output device: {args.output_device}")
    print(f"   Delay: {args.delay}ms")
    print(f"   Sample rate: {args.rate}Hz")
    print(f"   Buffer size: {args.buffer}")
    print()
    print("🔧 This creates a virtual microphone that Camtasia can select")
    print("📹 In Camtasia, select the virtual audio device as your microphone")
    print("🎯 The delayed audio will be available for recording")
    print("Press Ctrl+C to stop")
    print()
    
    # Create virtual microphone
    process_func, pa = virtual_microphone_delay(
        delay_ms=args.delay,
        sample_rate=args.rate,
        chunk_size=args.buffer,
        input_device=args.input_device,
        output_device=args.output_device
    )
    
    # Start processing in background thread
    audio_thread = threading.Thread(target=process_func, daemon=True)
    audio_thread.start()
    
    try:
        # Keep main thread alive
        while audio_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping virtual microphone...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        pa.terminate()
        print("✅ Virtual microphone stopped")

if __name__ == "__main__":
    main()
