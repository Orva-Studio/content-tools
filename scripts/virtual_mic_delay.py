#!/usr/bin/env python3
"""
Cuca: Virtual Microphone Audio Delay Tool
Creates a virtual microphone with delayed audio for recording software like your recording software
"""

import pyaudio
import numpy as np
from collections import deque
import sys
import threading
import time
from typing import Optional, List 
import signal
import atexit


def _get_device_name(device_index: Optional[int], direction: str = "input") -> str:
    """Return human-readable device name for a given index."""
    p = pyaudio.PyAudio()
    try:
        if device_index is None:
            try:
                info = (
                    p.get_default_input_device_info()
                    if direction == "input"
                    else p.get_default_output_device_info()
                )
                name = info.get("name", "Default")
                return str(name) if name is not None else "Default"
            except Exception:
                return "Default"
        try:
            info = p.get_device_info_by_index(device_index)
            name = info.get("name", f"Device {device_index}")
            return str(name) if name is not None else f"Device {device_index}"
        except Exception:
            return f"Device {device_index}"
    finally:
        p.terminate()


def _get_default_device_index(direction: str = "input") -> Optional[int]:
    """Return the default device index for the given direction if available."""
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
        delay_samples = max(1, int(delay_ms * sample_rate / 1000))
        buffer_list = [0.0] * delay_samples
        self._delay_buffer = deque(buffer_list, maxlen=int(delay_samples))
    
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
                    pass
                self._input_stream = None
                
            if self._output_stream:
                try:
                    self._output_stream.stop_stream()
                    self._output_stream.close()
                except Exception:
                    pass
                self._output_stream = None
                
            if self._pa:
                try:
                    self._pa.terminate()
                except Exception:
                    pass
                self._pa = None
                
        except Exception:
            pass
    
    def start(self):
        """Start the virtual microphone"""
        if self._audio_thread and self._audio_thread.is_alive():
            return False
            
        self._stop_event.clear()
        self._audio_thread = threading.Thread(
            target=self._process_audio,
            name="AudioProcessor",
            daemon=False
        )
        self._audio_thread.start()
        return True
    
    def stop(self):
        """Stop the virtual microphone cleanly"""
        if self._audio_thread and self._audio_thread.is_alive():
            self._stop_event.set()
            self._audio_thread.join(timeout=2.0)
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
        name = str(info.get('name', '')).lower()
        
        # Look for common virtual audio device names
        virtual_keywords = ['cable', 'virtual', 'vb-audio', 'blackhole', 'loopback']
        if any(keyword in name for keyword in virtual_keywords):
            virtual_devices.append((i, str(info.get('name', '')), info))
    
    p.terminate()
    return virtual_devices


def get_device_list_with_info():
    """Get list of all audio devices with detailed information"""
    p = pyaudio.PyAudio()
    
    devices = []
    virtual_devices = []
    
    # Get host API info to identify virtual/software devices
    host_apis = {}
    for i in range(p.get_host_api_count()):
        api_info = p.get_host_api_info_by_index(i)
        host_apis[i] = api_info
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = str(info.get('name', ''))
        inputs = int(info.get('maxInputChannels', 0))
        outputs = int(info.get('maxOutputChannels', 0))
        host_api_index = int(info.get('hostApi', 0))
        
        # Check if it's a communications device (common for conferencing tools)
        name_lower = name.lower()
        is_communications_device = any(keyword in name_lower for keyword in [
            'communications', 'meeting', 'conference', 'zoom', 'teams', 'skype',
            'webex', 'google meet', 'discord', 'slack'
        ])
        
        # Skip communications devices completely - don't add to devices list at all
        if is_communications_device:
            continue
        
        # Check if it's likely a virtual device using multiple criteria
        virtual_keywords = ['cable', 'virtual', 'vb-audio', 'blackhole', 'loopback']
        is_virtual_by_name = any(keyword in name_lower for keyword in virtual_keywords)
        
        # Check host API - virtual devices often use specific APIs
        host_api_info = host_apis.get(host_api_index, {})
        host_api_name = str(host_api_info.get('name', '')).lower()
        
        # Common virtual device indicators (excluding communications)
        is_virtual_by_api = any(keyword in host_api_name for keyword in [
            'windows audio session', 'wasapi', 'core audio', 'windows multimedia'
        ])
        
        # Additional heuristics for virtual devices (excluding communications)
        is_suspicious_device = (
            # Devices with very specific names that suggest virtual
            any(keyword in name_lower for keyword in [
                'audio device', 'stereo mix', 'what you hear', 'wave out'
            ]) or
            # Devices that are both input and output (often virtual)
            (inputs > 0 and outputs > 0 and not is_virtual_by_name) or
            # Devices with generic names that are likely virtual
            any(keyword in name_lower for keyword in [
                'default', 'primary'
            ])
        )
        
        # Final determination: only mark as virtual if it's a legitimate virtual device
        is_virtual = is_virtual_by_name or (
            is_suspicious_device and is_virtual_by_api
        )
        
        device_info = {
            'id': i,
            'name': name,
            'inputs': inputs,
            'outputs': outputs,
            'is_virtual': is_virtual,
            'is_communications': False,  # We've already filtered these out
            'host_api': host_api_name,
            'host_api_index': host_api_index
        }
        devices.append(device_info)
        
        if is_virtual:
            virtual_devices.append(device_info)
    
    p.terminate()
    return devices, virtual_devices


def list_audio_devices():
    """List only physical microphone devices, excluding communications devices"""
    devices, virtual_devices = get_device_list_with_info()
    
    # Filter to show only physical microphones (exclude communications devices)
    physical_mics = []
    for device in devices:
        # Must have input channels
        if device.get('inputs', 0) <= 0:
            continue
        
        # Exclude communications devices (Zoom, Teams, etc.)
        if device.get('is_communications', False):
            continue
        
        # Exclude virtual devices that aren't intended for output
        if device.get('is_virtual', False) and device.get('outputs', 0) == 0:
            continue
        
        physical_mics.append(device)
    
    # Get virtual devices that can be used as output
    output_virtual_devices = []
    for device in virtual_devices:
        if device.get('outputs', 0) > 0:
            output_virtual_devices.append(device)
    
    print("📋 Available microphone devices:")
    print("=" * 60)
    
    if not physical_mics:
        print("⚠️  No physical microphone devices found!")
        print("💡 Make sure your microphone is connected and not being used by another application")
        print("=" * 60)
        return
    
    # Display with ordered numbers (1, 2, 3, ...) instead of device IDs
    # Bold every even line (2nd, 4th, 6th, etc.)
    for i, device in enumerate(physical_mics, 1):
        device_line = ""
        if device.get('is_virtual', False) and device.get('outputs', 0) > 0:
            device_line = f"🔊 {i}: {device['name']} (IN:{device['inputs']}, OUT:{device['outputs']}) [VIRTUAL]"
        else:
            device_line = f"   {i}: {device['name']} (IN:{device['inputs']}, OUT:{device['outputs']})"
        
        # Apply bold to even lines
        if i % 2 == 0:
            print(f"\033[1m{device_line}\033[0m")  # Bold
        else:
            print(device_line)
    
    print("=" * 60)
    if output_virtual_devices:
        virtual_ids = [d['id'] for d in output_virtual_devices]
        print(f"✅ Found virtual output devices: {virtual_ids}")
        print("💡 These will be used as output devices")
    else:
        print("⚠️  No virtual output devices detected")
        print("💡 Install VB-Cable (Windows) or BlackHole (Mac) to create virtual microphones")
    
    # Return the filtered physical microphones for use in selection
    return physical_mics


def get_device_selection(prompt: str, devices: List[dict], filter_func=None, use_ordered_numbers=False) -> Optional[int]:
    """Interactive device selection with validation"""
    import sys
    import termios
    import tty
    
    while True:
        try:
            if use_ordered_numbers:
                # Get single character input without requiring Enter
                print(prompt, end='', flush=True)
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    user_input = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                print()  # New line after input
                
                # Allow user to quit
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("👋 Exiting...")
                    return None
                
                if not user_input or not user_input.isdigit():
                    print("❌ Please enter a device number (1-{}) or 'q' to quit".format(len(devices)))
                    continue
                
                device_index = int(user_input) - 1  # Convert to 0-based index
                
                # Validate device index
                if device_index < 0 or device_index >= len(devices):
                    print(f"❌ Invalid device number. Please enter a number between 1 and {len(devices)}")
                    continue
                
                # Get the actual device ID from the ordered list
                device_id = devices[device_index]['id']
                
                # Apply filter function if provided
                if filter_func:
                    device = devices[device_index]
                    if not filter_func(device):
                        print("❌ This device doesn't meet the requirements for this selection")
                        continue
                
                return device_id
            else:
                # Original behavior for device ID input
                user_input = input(prompt).strip()
                
                # Allow user to quit
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print("👋 Exiting...")
                    return None
                
                if not user_input:
                    print("❌ Please enter a device number or 'q' to quit")
                    continue
                
                device_id = int(user_input)
                
                # Validate device ID exists
                device_exists = any(d['id'] == device_id for d in devices)
                if not device_exists:
                    valid_ids = [d['id'] for d in devices]
                    print(f"❌ Invalid device ID. Valid IDs are: {valid_ids}")
                    continue
                
                # Apply filter function if provided
                if filter_func:
                    device = next((d for d in devices if d['id'] == device_id), None)
                    if not filter_func(device):
                        print("❌ This device doesn't meet the requirements for this selection")
                        continue
                
                return device_id
            
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return None


def interactive_main():
    """Interactive CLI main function"""
    print("🎤 Virtual Microphone Audio Delay Tool")
    print("=" * 50)
    
    # Get device list
    devices, virtual_devices = get_device_list_with_info()
    
    # Show device list and get filtered input devices
    input_devices = list_audio_devices()
    print()
    
    # Check for virtual devices
    if not virtual_devices:
        print("❌ No virtual audio devices found!")
        print("💡 Please install a virtual audio device:")
        print("   • macOS: brew install blackhole-2ch")
        print("   • Windows: Install VB-Cable from vb-audio.com")
        print()
        return
    
    # Get input device (physical microphone) with ordered numbering
    if not input_devices:
        print("❌ No input devices (microphones) found!")
        return
    
    input_device_id = get_device_selection(
        "Select INPUT device (physical microphone): ",
        input_devices,
        lambda d: d['inputs'] > 0,
        use_ordered_numbers=True
    )
    
    if input_device_id is None:
        return
    
    # Get output device (virtual audio device)
    if len(virtual_devices) == 1:
        # Auto-select the only virtual device
        output_device_id = virtual_devices[0]['id']
        output_device_name = virtual_devices[0]['name']
        print(f"✅ Auto-selected virtual device: \"{output_device_name}\" (ID: {output_device_id})")
    else:
        # Multiple virtual devices, let user choose
        output_device_id = get_device_selection(
            "Select OUTPUT device (virtual audio device): ",
            virtual_devices,
            lambda d: d['outputs'] > 0
        )
        
    if output_device_id is None:
            return
    
    # Get delay value from user with default of 140
    while True:
        try:
            delay_input = input("Enter delay in milliseconds (default: 140): ").strip()
            if not delay_input:
                delay_ms = 140
                break
            delay_ms = int(delay_input)
            if delay_ms < 0:
                print("❌ Delay must be positive")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number or press Enter for default")
    
    print()
    print("📋 Configuration Summary:")
    print("=" * 30)
    
    input_device = next(d for d in devices if d['id'] == input_device_id)
    output_device = next(d for d in devices if d['id'] == output_device_id)
    
    # Configuration lines with bold on even lines (2nd, 4th, 6th)
    config_lines = [
        f"Input device:  {input_device['name']} (ID: {input_device_id})",
        f"Output device: {output_device['name']} (ID: {output_device_id})",
        f"Delay:         {delay_ms}ms",
        f"Sample rate:   44100 Hz",
        f"Buffer size:   1024"
    ]
    
    for i, line in enumerate(config_lines, 1):
        if i % 2 == 0:
            print(f"\033[1m{line}\033[0m")  # Bold for even lines
        else:
            print(line)
    print()
    
    # Confirm before starting
    confirm = input("Start virtual microphone with these settings? (Y/n): ").strip().lower()
    if confirm in ['', 'y', 'yes']:
        pass  # Continue with default Y
    else:
        print("👋 Cancelled")
        return
    
    print()
    print("🔧 Starting virtual microphone...")
    print("📹 In your recording software, select the virtual audio device as your microphone")
    print("🎯 The delayed audio will be available for recording")
    print("Press Ctrl+C to stop")
    print()
    
    # Create and configure virtual microphone
    virtual_mic = VirtualMicrophone(
        delay_ms=delay_ms,
        sample_rate=44100,
        chunk_size=1024,
        input_device=input_device_id,
        output_device=output_device_id
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


def main():
    """Main function with backward compatibility for command-line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Virtual microphone with audio delay')
    parser.add_argument('-d', '--delay', type=int, default=140,
                       help='Delay in milliseconds (default: 140ms)')
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
    
    # If no arguments provided, run interactive mode
    if len(sys.argv) == 1:
        interactive_main()
        return
    
    # Original command-line argument handling
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
    print("🔧 This creates a virtual microphone that your recording software can select")
    print("📹 In your recording software, select the virtual audio device as your microphone")
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
