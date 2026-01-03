"""
FIT File Parser - Extract time series data from Garmin FIT files
"""
from typing import Dict, List, Optional
from fitparse import FitFile
import io


def parse_fit_time_series(fit_data: bytes) -> Dict:
    """
    Parse FIT file and extract time series data.
    
    Args:
        fit_data: Raw FIT file bytes
        
    Returns:
        Dictionary containing time series arrays and metadata
    """
    try:
        # Check if data is gzipped (Garmin sometimes returns compressed FIT files)
        if fit_data[:2] == b'\x1f\x8b':  # gzip magic number
            import gzip
            fit_data = gzip.decompress(fit_data)
        
        # Check for ZIP format (sometimes wrapped in ZIP)
        if fit_data[:4] == b'PK\x03\x04':  # ZIP magic number
            import zipfile
            zip_buffer = io.BytesIO(fit_data)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                # Get first file (usually the .fit file)
                fit_data = zip_file.read(zip_file.namelist()[0])
        
        # Parse FIT file directly from bytes
        fit_file = FitFile(fit_data)
        
        # Extract record messages (time series data points)
        records = list(fit_file.get_messages("record"))
        
        if not records:
            return {"error": "No record data found in FIT file"}
        
        # Initialize arrays
        time_series = {
            "timestamps": [],
            "elapsed_time": [],  # seconds since start
            "heart_rate": [],
            "altitude": [],
            "speed": [],  # m/s
            "cadence": [],
            "power": [],
            "latitude": [],
            "longitude": [],
            "temperature": [],
            "distance": [],  # meters
        }
        
        # Track start time
        start_time = None
        
        # Extract data from each record
        for record in records:
            # Get timestamp
            timestamp = None
            for field in record.fields:
                if field.name == "timestamp":
                    timestamp = field.value
                    if start_time is None:
                        start_time = timestamp
                    break
            
            if timestamp is None:
                continue
            
            # Calculate elapsed time
            elapsed = (timestamp - start_time).total_seconds() if start_time else 0
            
            time_series["timestamps"].append(timestamp.isoformat())
            time_series["elapsed_time"].append(int(elapsed))
            
            # Extract all available fields
            field_map = {
                "heart_rate": "heart_rate",
                "altitude": "altitude",
                "enhanced_altitude": "altitude",  # Garmin uses enhanced_altitude
                "speed": "speed",
                "enhanced_speed": "speed",  # Garmin uses enhanced_speed
                "cadence": "cadence",
                "power": "power",
                "position_lat": "latitude",
                "position_long": "longitude",
                "temperature": "temperature",
                "distance": "distance",
            }
            
            field_values = {}
            for field in record.fields:
                if field.name in field_map:
                    target_key = field_map[field.name]
                    # Convert semicircles to degrees for GPS coordinates
                    if field.name in ["position_lat", "position_long"] and field.value is not None:
                        field_values[target_key] = field.value * (180.0 / 2**31)
                    else:
                        field_values[target_key] = field.value
            
            # Append values (None if not present)
            time_series["heart_rate"].append(field_values.get("heart_rate"))
            time_series["altitude"].append(field_values.get("altitude"))
            time_series["speed"].append(field_values.get("speed"))
            time_series["cadence"].append(field_values.get("cadence"))
            time_series["power"].append(field_values.get("power"))
            time_series["latitude"].append(field_values.get("latitude"))
            time_series["longitude"].append(field_values.get("longitude"))
            time_series["temperature"].append(field_values.get("temperature"))
            time_series["distance"].append(field_values.get("distance"))
        
        # Calculate statistics
        def calc_stats(values: List) -> Dict:
            """Calculate min/max/avg for a list of values."""
            valid_values = [v for v in values if v is not None]
            if not valid_values:
                return {"min": None, "max": None, "avg": None, "count": 0}
            return {
                "min": min(valid_values),
                "max": max(valid_values),
                "avg": sum(valid_values) / len(valid_values),
                "count": len(valid_values)
            }
        
        # Add metadata
        metadata = {
            "total_points": len(records),
            "duration_seconds": int(time_series["elapsed_time"][-1]) if time_series["elapsed_time"] else 0,
            "heart_rate_stats": calc_stats(time_series["heart_rate"]),
            "altitude_stats": calc_stats(time_series["altitude"]),
            "speed_stats": calc_stats(time_series["speed"]),
            "cadence_stats": calc_stats(time_series["cadence"]),
            "power_stats": calc_stats(time_series["power"]),
            "has_gps": any(lat is not None for lat in time_series["latitude"]),
            "has_heart_rate": any(hr is not None for hr in time_series["heart_rate"]),
            "has_altitude": any(alt is not None for alt in time_series["altitude"]),
            "has_power": any(p is not None for p in time_series["power"]),
        }
        
        return {
            "time_series": time_series,
            "metadata": metadata
        }
        
    except Exception as e:
        return {"error": f"FIT parsing error: {str(e)}"}


def get_time_series_summary(time_series_data: Dict) -> str:
    """
    Get a human-readable summary of time series data.
    
    Args:
        time_series_data: Parsed time series data from parse_fit_time_series
        
    Returns:
        Summary string
    """
    if "error" in time_series_data:
        return f"Error: {time_series_data['error']}"
    
    metadata = time_series_data.get("metadata", {})
    
    summary_parts = [
        f"📊 {metadata.get('total_points', 0)} data points",
        f"⏱️  {metadata.get('duration_seconds', 0)}s duration"
    ]
    
    if metadata.get("has_heart_rate"):
        hr_stats = metadata.get("heart_rate_stats", {})
        summary_parts.append(f"❤️  HR: {hr_stats.get('avg', 0):.0f} bpm avg")
    
    if metadata.get("has_altitude"):
        summary_parts.append("🏔️  Elevation data")
    
    if metadata.get("has_power"):
        power_stats = metadata.get("power_stats", {})
        summary_parts.append(f"⚡ Power: {power_stats.get('avg', 0):.0f}W avg")
    
    if metadata.get("has_gps"):
        summary_parts.append("📍 GPS track")
    
    return " | ".join(summary_parts)
