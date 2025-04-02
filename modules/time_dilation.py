import numpy as np
import random
import time
from typing import Dict, List, Any
from scipy.signal import butter, filtfilt
from functools import lru_cache

class TimeDilationSystem:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._initialize_state()
        self._setup_frequency_tables()
        
    def _initialize_state(self):
        """Initialize system state with optimized defaults."""
        self.cognitive_state = {
            'current_level': 1,
            'mastery_percentage': 0,
            'next_milestone': 'Flow State Level 1',
            'total_training_time': 0,
            'sessions_completed': 0,
            'achievements': set(),
            'highest_flow_depth': 0,
            'best_time_dilation': 1.0
        }
        self.cache = {}
        
    def _setup_frequency_tables(self):
        """Pre-compute frequency tables for faster pattern generation."""
        self.frequency_tables = {
            'Standard': {
                'theta': (4.0, 8.0),
                'alpha': (8.0, 12.0),
                'beta': (12.0, 30.0)
            },
            'Speed Focus': {
                'alpha': (10.0, 12.0),
                'beta': (18.0, 22.0),
                'gamma': (32.0, 38.0)
            },
            'Deep Flow': {
                'theta': (5.5, 6.5),
                'alpha': (9.5, 10.5),
                'beta': (14.0, 16.0)
            },
            'Time Compression': {
                'alpha': (10.5, 11.5),
                'beta': (17.0, 19.0),
                'gamma': (28.0, 32.0)
            }
        }

    @lru_cache(maxsize=32)
    def _generate_base_frequencies(self, mode: str) -> Dict[str, float]:
        """Generate optimized base frequencies for each mode with caching."""
        if mode not in self.frequency_tables:
            mode = 'Standard'
            
        frequencies = {}
        for wave_type, (min_freq, max_freq) in self.frequency_tables[mode].items():
            frequencies[wave_type] = np.random.uniform(min_freq, max_freq)
        return frequencies

    @lru_cache(maxsize=128)
    def generate_neural_pattern(self, mode: str = "Standard", pattern_seed: int = None) -> Dict[str, Any]:
        """Generate optimized neural frequency pattern with caching."""
        if pattern_seed is not None:
            np.random.seed(pattern_seed)
            
        base_frequencies = self._generate_base_frequencies(mode)
        pattern = {
            "frequencies": base_frequencies,
            "modulation": self._generate_modulation_pattern(mode),
            "phase_shifts": self._generate_phase_shifts(len(base_frequencies)),
            "timestamp": time.time()
        }
        
        return pattern

    def _generate_modulation_pattern(self, mode: str) -> Dict[str, float]:
        """Generate optimized modulation patterns for different modes."""
        if mode == "Speed Focus":
            return {"amplitude": 0.2, "frequency": 0.5}
        elif mode == "Deep Flow":
            return {"amplitude": 0.15, "frequency": 0.3}
        elif mode == "Time Compression":
            return {"amplitude": 0.25, "frequency": 0.4}
        else:
            return {"amplitude": 0.1, "frequency": 0.2}

    def _generate_phase_shifts(self, num_frequencies: int) -> List[float]:
        """Generate optimized phase shifts."""
        return [i * np.pi / num_frequencies for i in range(num_frequencies)]

    def apply_neural_pattern(self, pattern: Dict[str, Any]) -> np.ndarray:
        """Generate optimized binaural beats with parallel processing for large arrays."""
        duration = 60  # 1 minute
        sample_rate = 44100
        chunk_size = sample_rate * 10  # Process in 10-second chunks
        
        # Pre-allocate the full array
        total_samples = int(sample_rate * duration)
        audio_data = np.zeros(total_samples)
        
        # Generate base carrier wave
        carrier_freq = 200  # Hz
        t = np.linspace(0, duration, total_samples)
        carrier = np.sin(2 * np.pi * carrier_freq * t)
        
        # Process each frequency component
        for wave_type, freq in pattern["frequencies"].items():
            # Apply modulation
            mod_amp = pattern["modulation"]["amplitude"]
            mod_freq = pattern["modulation"]["frequency"]
            
            # Process in chunks for better memory usage
            for i in range(0, total_samples, chunk_size):
                end_idx = min(i + chunk_size, total_samples)
                chunk_t = t[i:end_idx]
                
                # Generate modulated wave for this chunk
                modulator = np.sin(2 * np.pi * freq * chunk_t + 
                                 mod_amp * np.sin(2 * np.pi * mod_freq * chunk_t))
                
                # Add to main audio data
                audio_data[i:end_idx] += 0.2 * carrier[i:end_idx] * modulator
        
        # Apply smoothing filter
        b, a = butter(4, 0.1)
        audio_data = filtfilt(b, a, audio_data)
        
        # Normalize
        audio_data = audio_data / np.max(np.abs(audio_data))
        return audio_data

    def get_progress_report(self) -> Dict[str, Any]:
        return self.cognitive_state

    def train_time_perception(self, mode="Standard", duration=300):
        """
        Generate a time perception training session.
        
        Args:
            mode (str): Training mode - "Standard", "Speed Focus", "Deep Flow", or "Time Compression"
            duration (int): Session duration in seconds
            
        Returns:
            dict: Training session configuration
        """
        # Configure session based on mode
        if mode == "Speed Focus":
            frequencies = {
                "alpha": 12.0,  # Higher alpha for increased alertness (12 Hz)
                "beta": 20.0,   # Strong beta for quick thinking (20 Hz)
                "gamma": 35.0   # Light gamma for rapid processing (35 Hz)
            }
            exercise_prompt = """🚀 Speed Focus Training
            
            Focus on quick, precise responses while maintaining clarity.
            1. Keep your breathing steady but energized
            2. Let thoughts flow rapidly but stay sharp
            3. Type with precision and speed
            4. Notice how time seems to slow while your mind speeds up"""
            
        elif mode == "Deep Flow":
            frequencies = {
                "theta": 6.0,   # Strong theta for deep flow state (6 Hz)
                "alpha": 10.0,  # Moderate alpha for awareness (10 Hz)
                "beta": 15.0    # Light beta for engagement (15 Hz)
            }
            exercise_prompt = """🌊 Deep Flow Training
            
            Enter a profound state of flow and temporal expansion.
            1. Let your breath become slow and deep
            2. Allow thoughts to arise naturally
            3. Feel the rhythm of the patterns
            4. Experience time expanding around you"""
            
        elif mode == "Time Compression":
            frequencies = {
                "alpha": 11.0,  # Balanced alpha (11 Hz)
                "beta": 18.0,   # Enhanced beta (18 Hz)
                "gamma": 30.0   # Moderate gamma (30 Hz)
            }
            exercise_prompt = """⌛ Time Compression Training
            
            Experience advanced time dilation effects.
            1. Synchronize your breath with the patterns
            2. Feel each moment expand and contract
            3. Notice the spaces between thoughts
            4. Let time become fluid and malleable"""
            
        else:  # Standard mode
            frequencies = {
                "theta": 5.0,   # Light theta for relaxation (5 Hz)
                "alpha": 10.0,  # Moderate alpha for balance (10 Hz)
                "beta": 15.0    # Moderate beta for focus (15 Hz)
            }
            exercise_prompt = """🎯 Standard Training
            
            Build your foundational time dilation skills.
            1. Find a comfortable, relaxed position
            2. Breathe naturally with the patterns
            3. Let your mind synchronize gradually
            4. Notice how time feels different"""

        # Generate visual patterns based on mode
        visual_patterns = []
        base_intensity = 0.7  # Slightly reduced base intensity
        
        for wave_type, freq in frequencies.items():
            # Adjust intensity based on wave type and mode
            if mode == "Speed Focus" and wave_type in ["beta", "gamma"]:
                intensity = base_intensity + 0.1
            elif mode == "Deep Flow" and wave_type in ["theta", "alpha"]:
                intensity = base_intensity + 0.1
            elif mode == "Time Compression" and wave_type == "gamma":
                intensity = base_intensity + 0.1
            else:
                intensity = base_intensity
            
            visual_patterns.append({
                "frequency": freq,
                "intensity": intensity,
                "type": wave_type
            })

        return {
            "mode": mode,
            "expected_duration": duration,
            "frequencies": frequencies,
            "exercise": {
                "prompt": exercise_prompt,
                "visual_patterns": visual_patterns
            }
        }

    def analyze_performance(self, elapsed_time: float, expected_duration: float) -> Dict[str, float]:
        """Analyze training session performance."""
        # Calculate time perception accuracy
        time_accuracy = min(1.0, elapsed_time / expected_duration)
        
        # Calculate flow state depth based on timing accuracy
        flow_depth = 1.0 - abs(1.0 - time_accuracy)
        
        # Update cognitive state
        self.cognitive_state['sessions_completed'] += 1
        self.cognitive_state['total_training_time'] += elapsed_time
        
        if flow_depth > self.cognitive_state['highest_flow_depth']:
            self.cognitive_state['highest_flow_depth'] = flow_depth
            self.cognitive_state['achievements'].add('New Flow State Record!')
        
        # Calculate mastery percentage
        sessions_for_mastery = 10
        self.cognitive_state['mastery_percentage'] = min(100, 
            (self.cognitive_state['sessions_completed'] / sessions_for_mastery) * 100)
        
        # Update level based on mastery
        new_level = 1 + int(self.cognitive_state['mastery_percentage'] / 20)
        if new_level > self.cognitive_state['current_level']:
            self.cognitive_state['current_level'] = new_level
            self.cognitive_state['achievements'].add(f'Reached Level {new_level}!')
            
        # Update next milestone
        if self.cognitive_state['mastery_percentage'] < 100:
            next_level = self.cognitive_state['current_level'] + 1
            self.cognitive_state['next_milestone'] = f'Flow State Level {next_level}'
        else:
            self.cognitive_state['next_milestone'] = 'Mastery Achieved'
        
        return {
            'time_accuracy': time_accuracy,
            'flow_depth': flow_depth,
            'mastery': self.cognitive_state['mastery_percentage']
        }

    def analyze_flow_state(self, typing_patterns, response_times):
        """Analyze flow state based on typing patterns and response times."""
        if not typing_patterns or not response_times:
            return {
                'flow_depth': 0,
                'coherence': 0,
                'rhythm': 0
            }
        
        # Calculate typing rhythm consistency
        typing_speeds = np.array(typing_patterns)
        rhythm_consistency = 1.0 - np.std(typing_speeds) / (np.mean(typing_speeds) + 1e-6)
        
        # Calculate response coherence
        response_times = np.array(response_times)
        coherence = 1.0 - np.std(response_times) / (np.mean(response_times) + 1e-6)
        
        # Calculate overall flow depth
        avg_speed = np.mean(typing_speeds)
        ideal_speed = 5.0  # words per second
        speed_factor = np.exp(-0.5 * ((avg_speed - ideal_speed) / 3.0) ** 2)
        
        flow_depth = 0.4 * rhythm_consistency + 0.3 * coherence + 0.3 * speed_factor
        
        return {
            'flow_depth': min(1.0, max(0.0, flow_depth)),
            'coherence': min(1.0, max(0.0, coherence)),
            'rhythm': min(1.0, max(0.0, rhythm_consistency))
        }

    def generate_flow_state_feedback(self, metrics: Dict[str, float]) -> str:
        """Generate feedback based on flow state metrics."""
        flow_depth = metrics.get('flow_depth', 0)
        
        if flow_depth >= 80:
            return """🌟 Exceptional Flow State Achieved!
Your mind has reached an extraordinary level of focus and time dilation."""
        elif flow_depth >= 60:
            return """✨ Strong Flow State Detected
You're experiencing significant time dilation and enhanced mental clarity."""
        elif flow_depth >= 40:
            return """🌊 Moderate Flow State
You're beginning to enter a flow state. Keep focusing on the patterns."""
        else:
            return """🌱 Flow State Building
Focus on your breathing and the visual patterns to deepen your flow state."""

    def update_cognitive_state(self, performance: Dict[str, float]) -> None:
        """Update cognitive state based on performance."""
        # Update basic stats
        self.cognitive_state['sessions_completed'] += 1
        self.cognitive_state['total_training_time'] += performance.get('session_duration', 0)
        
        # Update flow metrics
        flow_depth = performance.get('flow_depth', 0)
        time_dilation = performance.get('time_dilation_factor', 1.0)
        
        if flow_depth > self.cognitive_state['highest_flow_depth']:
            self.cognitive_state['highest_flow_depth'] = flow_depth
        
        if time_dilation > self.cognitive_state['best_time_dilation']:
            self.cognitive_state['best_time_dilation'] = time_dilation
        
        # Update level and mastery
        base_mastery = self.cognitive_state['mastery_percentage']
        mastery_gain = min(5.0, flow_depth / 10)  # Max 5% per session
        new_mastery = min(100, base_mastery + mastery_gain)
        
        self.cognitive_state['mastery_percentage'] = new_mastery
        
        # Update level based on mastery
        current_level = self.cognitive_state['current_level']
        if new_mastery >= current_level * 20:  # Each level requires 20% mastery
            self.cognitive_state['current_level'] += 1
            self.cognitive_state['next_milestone'] = f'Flow State Level {current_level + 1}'
            
        # Update achievements
        achievements = self.cognitive_state['achievements']
        if flow_depth >= 80:
            achievements.add('Flow Master')
        if time_dilation >= 2:
            achievements.add('Time Bender')
        if self.cognitive_state['sessions_completed'] >= 5:
            achievements.add('Consistent')
        if self.cognitive_state['sessions_completed'] >= 1:
            achievements.add('First Session')

    def generate_time_crystal(self) -> Dict[str, Any]:
        """Generate time crystal pattern with meaningful phase names that reflect temporal perception states."""
        phases = [
            'Temporal Awareness',    # Initial phase of time perception
            'Conscious Expansion',   # Expanding awareness of time
            'Flow Synchronization', # Stabilizing in the flow state
            'Time Mastery'          # Final integration of time perception
        ]
        crystal_data = []
        
        for phase in phases:
            t = np.linspace(0, 10, 1000)
            if phase == 'Temporal Awareness':
                values = np.sin(t) * np.exp(-t/5)  # Initial awakening pattern
            elif phase == 'Conscious Expansion':
                values = np.sin(2*t) * (1 - np.exp(-t/3))  # Expanding consciousness
            elif phase == 'Flow Synchronization':
                values = np.sin(3*t) * np.tanh(t/2)  # Stabilizing flow state
            else:  # Time Mastery
                values = np.sin(4*t) * np.cos(t/2)  # Integration pattern
            
            crystal_data.append({
                'phase': phase,
                'time': t.tolist(),
                'values': values.tolist()
            })
        
        return {'crystal_data': crystal_data}

    def visualize_time_crystal(self, crystal_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare time crystal data for visualization."""
        return crystal_structure
