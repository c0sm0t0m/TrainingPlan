/**
 * ActivityMap Component
 * 
 * Displays GPS track on a Leaflet map with:
 * - Dark/light mode tile layers
 * - Start/end markers
 * - Fullscreen toggle
 * - Auto-fit bounds
 */
import React, { useEffect, useRef, useState } from 'react';
import { Box, IconButton, useTheme, Paper, Typography } from '@mui/material';
import { Fullscreen as FullscreenIcon, FullscreenExit as FullscreenExitIcon } from '@mui/icons-material';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L, { LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon issue in React
// Use CDN icons instead of bundled ones to avoid TypeScript errors
const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const iconRetinaUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface TrackPoint {
  lat: number;
  lng: number;
  ele?: number;
  timestamp?: string;
}

interface ActivityMapProps {
  trackPoints: TrackPoint[];
  activityName: string;
  showElevation?: boolean;
}

// Component to handle map bounds
const MapBoundsHandler: React.FC<{ trackPoints: TrackPoint[] }> = ({ trackPoints }) => {
  const map = useMap();

  useEffect(() => {
    if (trackPoints.length > 0) {
      const bounds = new LatLngBounds(trackPoints.map(p => [p.lat, p.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [trackPoints, map]);

  return null;
};

const ActivityMap: React.FC<ActivityMapProps> = ({ trackPoints, activityName, showElevation = false }) => {
  const theme = useTheme();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const isDarkMode = theme.palette.mode === 'dark';

  // Theme-aware tile selection
  // Dark mode: CartoDB Dark (dark_all) - Dark map with street labels
  // Light mode: CartoDB Positron (light_all) - Light map with subtle styling
  const tileUrl = isDarkMode
    ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';

  const tileAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!containerRef.current) return;

    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  if (trackPoints.length === 0) {
    return (
      <Paper
        sx={{
          height: 400,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.default',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          No GPS data available
        </Typography>
      </Paper>
    );
  }

  // Start and end points
  const startPoint = trackPoints[0];
  const endPoint = trackPoints[trackPoints.length - 1];

  // Create custom start/end markers
  const startIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });

  const endIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
  });

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        height: isFullscreen ? '100vh' : 400,
        minHeight: isFullscreen ? '100vh' : 400,
        width: '100%',
        borderRadius: isFullscreen ? 0 : 1,
        overflow: 'hidden',
        '& .leaflet-container': {
          height: '100%',
          width: '100%',
          minHeight: isFullscreen ? '100vh' : 400,
          borderRadius: isFullscreen ? 0 : 1,
          zIndex: 0,
        },
      }}
    >
      <MapContainer
        center={[startPoint.lat, startPoint.lng]}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer 
          attribution={tileAttribution} 
          url={tileUrl} 
        />

        {/* GPS Track - Outline layer for contrast */}
        <Polyline
          positions={trackPoints.map(p => [p.lat, p.lng])}
          pathOptions={{
            color: isDarkMode ? '#ffffff' : '#000000',
            weight: 5,
            opacity: 0.3,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />

        {/* GPS Track - Main polyline */}
        <Polyline
          positions={trackPoints.map(p => [p.lat, p.lng])}
          pathOptions={{
            color: theme.palette.primary.main,
            weight: 3,
            opacity: 0.9,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        />

        {/* Start Marker */}
        <Marker position={[startPoint.lat, startPoint.lng]} icon={startIcon}>
          <Popup>
            <strong>Start</strong>
            <br />
            {activityName}
            {startPoint.ele && (
              <>
                <br />
                Elevation: {Math.round(startPoint.ele)}m
              </>
            )}
          </Popup>
        </Marker>

        {/* End Marker */}
        <Marker position={[endPoint.lat, endPoint.lng]} icon={endIcon}>
          <Popup>
            <strong>Finish</strong>
            {endPoint.ele && (
              <>
                <br />
                Elevation: {Math.round(endPoint.ele)}m
              </>
            )}
          </Popup>
        </Marker>

        {/* Auto-fit bounds */}
        <MapBoundsHandler trackPoints={trackPoints} />
      </MapContainer>

      {/* Fullscreen Toggle Button */}
      <IconButton
        onClick={toggleFullscreen}
        aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
        sx={{
          position: 'absolute',
          top: 10,
          right: 10,
          zIndex: 1000,
          minWidth: 44,
          minHeight: 44,
          bgcolor: isDarkMode 
            ? 'rgba(30, 30, 30, 0.85)' 
            : 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(10px)',
          boxShadow: isDarkMode
            ? '0 4px 12px rgba(0, 0, 0, 0.4)'
            : '0 4px 12px rgba(0, 0, 0, 0.15)',
          border: isDarkMode 
            ? '1px solid rgba(255, 255, 255, 0.1)'
            : '1px solid rgba(0, 0, 0, 0.1)',
          '&:hover': { 
            bgcolor: isDarkMode
              ? 'rgba(40, 40, 40, 0.95)'
              : 'rgba(255, 255, 255, 0.95)',
            transform: 'scale(1.05)',
          },
          transition: 'all 0.2s ease-in-out',
        }}
      >
        {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
      </IconButton>

      {/* Map Info Overlay */}
      <Paper
        elevation={0}
        sx={{
          position: 'absolute',
          bottom: 10,
          left: 10,
          zIndex: 1000,
          px: 2,
          py: 1,
          bgcolor: isDarkMode 
            ? 'rgba(30, 30, 30, 0.85)' 
            : 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(10px)',
          boxShadow: isDarkMode
            ? '0 4px 12px rgba(0, 0, 0, 0.4)'
            : '0 4px 12px rgba(0, 0, 0, 0.15)',
          border: isDarkMode 
            ? '1px solid rgba(255, 255, 255, 0.1)'
            : '1px solid rgba(0, 0, 0, 0.1)',
          borderRadius: 2,
        }}
      >
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
          {trackPoints.length} GPS points
          {showElevation && trackPoints[0]?.ele && ' • Elevation data available'}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ActivityMap;
