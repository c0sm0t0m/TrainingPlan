"""
Workout XML Import Utilities
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


def parse_workout_xml(xml_string: str) -> Dict:
    """
    Parse workout XML and extract structured data.
    
    Args:
        xml_string: XML workout definition
        
    Returns:
        Dictionary with workout data compatible with our model
    """
    try:
        root = ET.fromstring(xml_string.strip())
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {str(e)}")
    
    # Extract metadata - try different case variations
    author = root.find('author') if root.find('author') is not None else root.find('Author')
    name = root.find('name') if root.find('name') is not None else root.find('Name')
    sport_type_elem = (root.find('sportType') if root.find('sportType') is not None 
                      else root.find('SportType') if root.find('SportType') is not None 
                      else root.find('sport_type'))
    workout_elem = root.find('workout') if root.find('workout') is not None else root.find('Workout')
    
    if name is None or sport_type_elem is None or workout_elem is None:
        # Provide helpful debug info
        found_tags = [child.tag for child in root]
        raise ValueError(
            f"Missing required fields. Root tag: '{root.tag}', "
            f"Found children: {found_tags}. "
            f"Required: 'name', 'sportType', 'workout'"
        )
    
    # Convert sport type
    sport_type_map = {
        'run': 'running',
        'running': 'running',
        'bike': 'cycling',
        'cycling': 'cycling',
        'cycle': 'cycling',
        'swim': 'swimming',
        'swimming': 'swimming',
    }
    sport_type_raw = sport_type_elem.text.lower() if sport_type_elem.text else 'running'
    sport_type = sport_type_map.get(sport_type_raw, 'other')
    
    # Parse workout structure
    segments = []
    total_duration_seconds = 0
    has_intervals = False
    
    def get_attr(element, *names):
        """Get attribute value, trying multiple case variations."""
        for name in names:
            # Try exact case
            if element.get(name):
                return element.get(name)
            # Try lowercase
            if element.get(name.lower()):
                return element.get(name.lower())
            # Try uppercase
            if element.get(name.upper()):
                return element.get(name.upper())
            # Try title case
            if element.get(name.title()):
                return element.get(name.title())
        return None
    
    for child in workout_elem:
        if child.tag == 'Warmup':
            duration = int(get_attr(child, 'Duration', 'duration') or 0)
            pace = get_attr(child, 'Pace', 'pace') or ''
            total_duration_seconds += duration
            segments.append(f"Warmup {duration//60}min @ {pace}")
            
        elif child.tag == 'Cooldown':
            duration = int(get_attr(child, 'Duration', 'duration') or 0)
            pace = get_attr(child, 'Pace', 'pace') or ''
            total_duration_seconds += duration
            segments.append(f"Cooldown {duration//60}min @ {pace}")
            
        elif child.tag == 'Repeat':
            has_intervals = True
            count = int(get_attr(child, 'Reps', 'reps', 'count') or 1)
            repeat_segments = []
            repeat_duration = 0
            
            for repeat_child in child:
                if repeat_child.tag == 'Interval':
                    duration = int(get_attr(repeat_child, 'Duration', 'duration') or 0)
                    pace = get_attr(repeat_child, 'Pace', 'pace') or ''
                    distance = get_attr(repeat_child, 'Distance', 'distance') or ''
                    repeat_duration += duration
                    if distance:
                        repeat_segments.append(f"{distance} @ {pace}")
                    else:
                        repeat_segments.append(f"{duration}s @ {pace}")
                        
                elif repeat_child.tag == 'Rest':
                    duration = int(get_attr(repeat_child, 'Duration', 'duration') or 0)
                    pace = get_attr(repeat_child, 'Pace', 'pace') or ''
                    repeat_duration += duration
                    repeat_segments.append(f"{duration}s rest @ {pace}")
            
            total_duration_seconds += count * repeat_duration
            segments.append(f"{count}×({', '.join(repeat_segments)})")
            
        elif child.tag == 'Interval':
            has_intervals = True
            duration = int(get_attr(child, 'Duration', 'duration') or 0)
            pace = get_attr(child, 'Pace', 'pace') or ''
            distance = get_attr(child, 'Distance', 'distance') or ''
            total_duration_seconds += duration
            if distance:
                segments.append(f"Interval {distance} @ {pace}")
            else:
                segments.append(f"Interval {duration}s @ {pace}")
    
    # Determine workout type
    workout_type = 'interval' if has_intervals else 'easy'
    
    # Calculate duration in minutes
    duration_minutes = (total_duration_seconds + 30) // 60  # Round to nearest minute
    
    # Build description
    description_parts = []
    if author and author.text:
        description_parts.append(f"Created by: {author.text}")
    description_parts.append("\n".join(segments))
    description = "\n\n".join(description_parts)
    
    return {
        'title': name.text,
        'sport_type': sport_type,
        'workout_type': workout_type,
        'description': description,
        'duration_minutes': duration_minutes,
        'intensity_zone': 'zone4' if has_intervals else 'zone2',  # Default zones
    }


def validate_workout_data(data: Dict) -> bool:
    """Validate parsed workout data."""
    required_fields = ['title', 'sport_type', 'workout_type']
    return all(field in data and data[field] for field in required_fields)
