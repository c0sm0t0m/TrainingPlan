"""
FIT Workout File Generator

Creates FIT workout files with scheduling information that can be uploaded to Garmin Connect.
Uses the Garmin FIT SDK protocol to create binary FIT files.

Based on FIT SDK examples from: external code/fitsdk/FitSDKRelease_21.188.00/
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date, timezone
import struct
import tempfile
from pathlib import Path

try:
    from garmin_fit_sdk import Profile
    FIT_SDK_AVAILABLE = True
except ImportError:
    FIT_SDK_AVAILABLE = False


# FIT Protocol Constants
FIT_EPOCH = datetime(1989, 12, 31, 0, 0, 0, tzinfo=timezone.utc)

# Message Numbers (from Profile)
MESG_NUM_FILE_ID = 0
MESG_NUM_WORKOUT = 26
MESG_NUM_WORKOUT_STEP = 27
MESG_NUM_SCHEDULE = 28

# File Types
FILE_TYPE_WORKOUT = 5

# Sport Types
SPORT_RUNNING = 1
SPORT_CYCLING = 2
SPORT_SWIMMING = 5
SPORT_GENERIC = 0

# Workout Step Duration Types
DURATION_TIME = 0  # Seconds
DURATION_DISTANCE = 1  # Meters
DURATION_HR_LESS_THAN = 2
DURATION_HR_GREATER_THAN = 3
DURATION_OPEN = 28  # Open/lap button press

# Workout Step Target Types
TARGET_SPEED = 0
TARGET_HEART_RATE = 1
TARGET_OPEN = 2  # No target
TARGET_CADENCE = 3
TARGET_POWER = 4

# Workout Step Intensity
INTENSITY_ACTIVE = 0
INTENSITY_REST = 1
INTENSITY_WARMUP = 2
INTENSITY_COOLDOWN = 3


class FITWorkoutEncoder:
    """
    Encodes workout data into FIT file format.
    
    FIT (Flexible and Interoperable Data Transfer) is a binary format used by Garmin devices.
    This encoder creates workout files that can be uploaded to Garmin Connect.
    """
    
    def __init__(self):
        self.data_crc = 0
        self.buffer = bytearray()
        self.data_start_pos = 0
        
    def _calc_crc(self, byte_val: int) -> None:
        """Calculate CRC for FIT file integrity."""
        crc_table = [
            0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
            0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
        ]
        
        # Calculate CRC for lower 4 bits
        tmp = crc_table[self.data_crc & 0xF]
        self.data_crc = (self.data_crc >> 4) & 0x0FFF
        self.data_crc = self.data_crc ^ tmp ^ crc_table[byte_val & 0xF]
        
        # Calculate CRC for upper 4 bits
        tmp = crc_table[self.data_crc & 0xF]
        self.data_crc = (self.data_crc >> 4) & 0x0FFF
        self.data_crc = self.data_crc ^ tmp ^ crc_table[(byte_val >> 4) & 0xF]
    
    def _write_byte(self, value: int) -> None:
        """Write a single byte and update CRC."""
        self.buffer.append(value & 0xFF)
        self._calc_crc(value & 0xFF)
    
    def _write_bytes(self, data: bytes) -> None:
        """Write multiple bytes and update CRC."""
        for byte in data:
            self._write_byte(byte)
    
    def _write_uint8(self, value: int) -> None:
        """Write an 8-bit unsigned integer."""
        self._write_byte(value)
    
    def _write_uint16(self, value: int) -> None:
        """Write a 16-bit unsigned integer (little-endian)."""
        self._write_bytes(struct.pack('<H', value))
    
    def _write_uint32(self, value: int) -> None:
        """Write a 32-bit unsigned integer (little-endian)."""
        self._write_bytes(struct.pack('<I', value))
    
    def _write_string(self, value: str, max_length: int) -> None:
        """Write a fixed-length string field (padded with null bytes)."""
        encoded = value.encode('utf-8')[:max_length]
        self._write_bytes(encoded)
        # Pad with zeros to max_length
        padding = max_length - len(encoded)
        for _ in range(padding):
            self._write_byte(0)
    
    def _datetime_to_fit_timestamp(self, dt: datetime) -> int:
        """Convert datetime to FIT timestamp (seconds since FIT epoch)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = dt - FIT_EPOCH
        return int(delta.total_seconds())
    
    def _write_file_header(self) -> None:
        """Write FIT file header (14 bytes)."""
        header_size = 14
        protocol_version = 0x20  # Protocol version 2.0  
        profile_version = 2113  # Profile version 21.13
        
        # Build header (not part of CRC)
        header = struct.pack('<BBHI4sBB',
            header_size,
            protocol_version,
            profile_version,
            0,  # Placeholder for data size (will update later)
            b'.FIT',
            0,  # CRC for 12-byte header (optional, set to 0)
            0
        )
        
        # Write header without CRC calculation
        self.buffer.extend(header)
        self.data_start_pos = len(self.buffer)
    
    def _write_message_definition(self, local_mesg_num: int, global_mesg_num: int, fields: List[Tuple[int, int, int]]) -> None:
        """
        Write a message definition.
        
        Args:
            local_mesg_num: Local message number (0-15)
            global_mesg_num: Global message number from Profile
            fields: List of (field_num, size, base_type) tuples
        """
        # Definition header: 0x40 | local_mesg_num
        self._write_byte(0x40 | (local_mesg_num & 0x0F))
        
        # Reserved byte
        self._write_byte(0)
        
        # Architecture (0 = little endian)
        self._write_byte(0)
        
        # Global message number
        self._write_uint16(global_mesg_num)
        
        # Number of fields
        self._write_byte(len(fields))
        
        # Field definitions
        for field_num, size, base_type in fields:
            self._write_byte(field_num)
            self._write_byte(size)
            self._write_byte(base_type)
    
    def _write_message_header(self, local_mesg_num: int) -> None:
        """Write message data header."""
        self._write_byte(local_mesg_num & 0x0F)
    
    def _write_file_id_message(self) -> None:
        """Write file_id message (required for all FIT files)."""
        local_mesg_num = 0
        
        # Define file_id message
        # Fields: type(1), manufacturer(2), product(2), serial_number(4), time_created(4)
        fields = [
            (0, 1, 0),   # type: enum (1 byte)
            (1, 2, 132), # manufacturer: uint16 (2 bytes, base type 132)
            (2, 2, 132), # product: uint16 (2 bytes)
            (3, 4, 140), # serial_number: uint32z (4 bytes, base type 140)
            (4, 4, 134), # time_created: uint32 (4 bytes, base type 134)
        ]
        
        self._write_message_definition(local_mesg_num, MESG_NUM_FILE_ID, fields)
        
        # Write file_id data
        self._write_message_header(local_mesg_num)
        self._write_uint8(FILE_TYPE_WORKOUT)  # type = workout
        self._write_uint16(1)  # manufacturer = garmin
        self._write_uint16(0)  # product = 0
        self._write_uint32(0)  # serial_number = 0
        
        # time_created = current time
        timestamp = self._datetime_to_fit_timestamp(datetime.now(timezone.utc))
        self._write_uint32(timestamp)
    
    def _write_workout_message(self, workout_name: str, sport: int, num_steps: int) -> None:
        """Write workout message."""
        local_mesg_num = 1  # Use different local message number
        
        # Define workout message
        # Fields: sport(1), wkt_name(16 bytes string), num_valid_steps(2)
        fields = [
            (4, 1, 0),    # sport: enum (1 byte)
            (8, 16, 7),   # wkt_name: string (16 bytes, base type 7)
            (6, 2, 132),  # num_valid_steps: uint16 (2 bytes)
        ]
        
        self._write_message_definition(local_mesg_num, MESG_NUM_WORKOUT, fields)
        
        # Write workout data
        self._write_message_header(local_mesg_num)
        self._write_uint8(sport)
        self._write_string(workout_name, 16)
        self._write_uint16(num_steps)
    
    def _write_workout_step_message(self, step_index: int, step_name: str, 
                                    duration_type: int, duration_value: int,
                                    target_type: int, target_value: int,
                                    intensity: int) -> None:
        """Write workout_step message."""
        local_mesg_num = 2  # Use different local message number
        
        # Define workout_step message
        # Fields: message_index(2), wkt_step_name(16), duration_type(1), duration_value(4),
        #         target_type(1), target_value(4), intensity(1)
        fields = [
            (254, 2, 132),  # message_index: uint16
            (0, 16, 7),     # wkt_step_name: string
            (1, 1, 0),      # duration_type: enum  
            (2, 4, 134),    # duration_value: uint32
            (3, 1, 0),      # target_type: enum
            (4, 4, 134),    # target_value: uint32
            (6, 1, 0),      # intensity: enum
        ]
        
        self._write_message_definition(local_mesg_num, MESG_NUM_WORKOUT_STEP, fields)
        
        # Write workout_step data
        self._write_message_header(local_mesg_num)
        self._write_uint16(step_index)
        self._write_string(step_name, 16)
        self._write_uint8(duration_type)
        self._write_uint32(duration_value)
        self._write_uint8(target_type)
        self._write_uint32(target_value)
        self._write_uint8(intensity)
    
    def _write_schedule_message(self, workout_time: datetime) -> None:
        """Write schedule message to schedule workout to a specific date."""
        local_mesg_num = 3  # Use different local message number
        
        # Define schedule message
        # Fields: time_created(4), scheduled_time(4), type(1)
        fields = [
            (5, 4, 134),  # time_created: uint32
            (6, 4, 134),  # scheduled_time: uint32  
            (0, 1, 0),    # type: enum (0=workout)
        ]
        
        self._write_message_definition(local_mesg_num, MESG_NUM_SCHEDULE, fields)
        
        # Write schedule data
        self._write_message_header(local_mesg_num)
        
        current_time = self._datetime_to_fit_timestamp(datetime.now(timezone.utc))
        scheduled_time = self._datetime_to_fit_timestamp(workout_time)
        
        self._write_uint32(current_time)  # time_created
        self._write_uint32(scheduled_time)  # scheduled_time
        self._write_uint8(0)  # type = workout
    
    def _finalize_file(self) -> None:
        """Finalize FIT file by updating header and adding CRC."""
        # Calculate data size
        data_size = len(self.buffer) - self.data_start_pos
        
        # Update data size in header (at offset 4)
        struct.pack_into('<I', self.buffer, 4, data_size)
        
        # Append final CRC (2 bytes, little endian)
        crc_bytes = struct.pack('<H', self.data_crc)
        self.buffer.extend(crc_bytes)
    
    def create_workout_file(
        self,
        workout_name: str,
        sport_type: str = 'running',
        duration_seconds: Optional[int] = None,
        distance_meters: Optional[int] = None,
        scheduled_date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a FIT workout file.
        
        Args:
            workout_name: Name of the workout
            sport_type: Type of sport (running, cycling, swimming, etc.)
            duration_seconds: Duration in seconds
            distance_meters: Distance in meters
            scheduled_date: Optional date to schedule (YYYY-MM-DD)
            output_path: Optional path to save file, otherwise uses temp file
            
        Returns:
            Path to the created FIT file
        """
        self.buffer = bytearray()
        self.data_crc = 0
        
        # Map sport type to FIT sport constant
        sport_map = {
            'running': SPORT_RUNNING,
            'cycling': SPORT_CYCLING,
            'swimming': SPORT_SWIMMING,
            'generic': SPORT_GENERIC,
        }
        sport = sport_map.get(sport_type.lower(), SPORT_GENERIC)
        
        # Write file header
        self._write_file_header()
        
        # Write file_id message
        self._write_file_id_message()
        
        # Create workout steps
        steps = []
        if duration_seconds:
            steps.append({
                'name': 'Main',
                'duration_type': DURATION_TIME,
                'duration_value': duration_seconds * 1000,  # Convert to milliseconds
                'target_type': TARGET_OPEN,
                'target_value': 0,
                'intensity': INTENSITY_ACTIVE,
            })
        elif distance_meters:
            steps.append({
                'name': 'Main',
                'duration_type': DURATION_DISTANCE,
                'duration_value': distance_meters * 100,  # Convert to centimeters
                'target_type': TARGET_OPEN,
                'target_value': 0,
                'intensity': INTENSITY_ACTIVE,
            })
        else:
            # Open workout (until lap button press)
            steps.append({
                'name': 'Main',
                'duration_type': DURATION_OPEN,
                'duration_value': 0,
                'target_type': TARGET_OPEN,
                'target_value': 0,
                'intensity': INTENSITY_ACTIVE,
            })
        
        # Write workout message
        self._write_workout_message(workout_name, sport, len(steps))
        
        # Write workout step messages
        for idx, step in enumerate(steps):
            self._write_workout_step_message(
                step_index=idx,
                step_name=step['name'],
                duration_type=step['duration_type'],
                duration_value=step['duration_value'],
                target_type=step['target_type'],
                target_value=step['target_value'],
                intensity=step['intensity']
            )
        
        # Write schedule message if date provided
        if scheduled_date:
            try:
                # Parse date and set to start of day
                scheduled_dt = datetime.strptime(scheduled_date, '%Y-%m-%d')
                scheduled_dt = scheduled_dt.replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
                self._write_schedule_message(scheduled_dt)
            except ValueError:
                print(f"Warning: Invalid scheduled_date format: {scheduled_date}")
        
        # Finalize file
        self._finalize_file()
        
        # Write to file
        if output_path is None:
            # Create temp file
            fd, output_path = tempfile.mkstemp(suffix='.fit', prefix='workout_')
            import os
            os.close(fd)
        
        with open(output_path, 'wb') as f:
            f.write(self.buffer)
        
        return output_path


def create_fit_workout_file(
    workout_data: Dict,
    scheduled_date: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Create a FIT workout file with scheduling information.
    
    Args:
        workout_data: Dictionary with workout fields
        scheduled_date: Optional date to schedule workout (YYYY-MM-DD)
        output_path: Optional path to save the FIT file
        
    Returns:
        Path to the created FIT file
    """
    if not FIT_SDK_AVAILABLE:
        raise ImportError("garmin-fit-sdk is required")
    
    encoder = FITWorkoutEncoder()
    return encoder.create_workout_file(
        workout_name=workout_data.get('title', 'Workout'),
        sport_type=workout_data.get('sport_type', 'running'),
        duration_seconds=int(workout_data.get('duration_minutes', 0) * 60) if workout_data.get('duration_minutes') else None,
        distance_meters=int(workout_data.get('distance_km', 0) * 1000) if workout_data.get('distance_km') else None,
        scheduled_date=scheduled_date,
        output_path=output_path
    )


def upload_fit_workout_file(api, fit_file_path: str) -> str:
    """
    Upload a FIT workout file to Garmin Connect.
    
    Args:
        api: Garmin API instance
        fit_file_path: Path to the FIT workout file
        
    Returns:
        Workout ID from Garmin
    """
    response = api.upload_activity(fit_file_path)
    
    if isinstance(response, dict):
        return str(response.get('workoutId', response.get('id', 'unknown')))
    
    return str(response)
