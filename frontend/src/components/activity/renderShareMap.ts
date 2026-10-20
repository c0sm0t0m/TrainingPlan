/**
 * Rasterize Esri basemap tiles + GPS track into a canvas for IG share cards.
 * Output is a data URL so html-to-image export has no cross-origin tile issues.
 */
export interface MapPoint {
  lat: number;
  lng: number;
}

const TILE_SIZE = 256;
const TILE_URL =
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}';

function latLngToWorld(lat: number, lng: number, zoom: number): { x: number; y: number } {
  const scale = TILE_SIZE * 2 ** zoom;
  const x = ((lng + 180) / 360) * scale;
  const sin = Math.sin((lat * Math.PI) / 180);
  const y =
    (0.5 - Math.log((1 + sin) / (1 - sin)) / (4 * Math.PI)) * scale;
  return { x, y };
}

function chooseZoom(
  points: MapPoint[],
  width: number,
  height: number,
  paddingPx: number
): number {
  let minLat = points[0].lat;
  let maxLat = points[0].lat;
  let minLng = points[0].lng;
  let maxLng = points[0].lng;
  for (const p of points) {
    minLat = Math.min(minLat, p.lat);
    maxLat = Math.max(maxLat, p.lat);
    minLng = Math.min(minLng, p.lng);
    maxLng = Math.max(maxLng, p.lng);
  }

  // Prefer a zoom that fits the track with padding
  for (let z = 16; z >= 10; z--) {
    const nw = latLngToWorld(maxLat, minLng, z);
    const se = latLngToWorld(minLat, maxLng, z);
    const spanX = Math.abs(se.x - nw.x);
    const spanY = Math.abs(se.y - nw.y);
    const availW = width - paddingPx * 2;
    const availH = height - paddingPx * 2;
    if (spanX <= availW && spanY <= availH) {
      return z;
    }
  }
  return 10;
}

function loadTile(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`tile failed: ${url}`));
    img.src = url;
  });
}

export async function renderShareMapDataUrl(
  points: MapPoint[],
  width: number,
  height: number
): Promise<string | null> {
  if (!points.length || typeof document === 'undefined') return null;

  const padding = Math.round(Math.min(width, height) * 0.08);
  const zoom = chooseZoom(points, width, height, padding);

  let minLat = points[0].lat;
  let maxLat = points[0].lat;
  let minLng = points[0].lng;
  let maxLng = points[0].lng;
  for (const p of points) {
    minLat = Math.min(minLat, p.lat);
    maxLat = Math.max(maxLat, p.lat);
    minLng = Math.min(minLng, p.lng);
    maxLng = Math.max(maxLng, p.lng);
  }

  const nw = latLngToWorld(maxLat, minLng, zoom);
  const se = latLngToWorld(minLat, maxLng, zoom);
  const trackW = Math.max(se.x - nw.x, 1);
  const trackH = Math.max(se.y - nw.y, 1);
  const scale = Math.min((width - padding * 2) / trackW, (height - padding * 2) / trackH);
  const offsetX = (width - trackW * scale) / 2 - nw.x * scale;
  const offsetY = (height - trackH * scale) / 2 - nw.y * scale;

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;

  // Soft base fill while tiles load gaps
  ctx.fillStyle = '#e8eef3';
  ctx.fillRect(0, 0, width, height);

  const worldLeft = -offsetX / scale;
  const worldTop = -offsetY / scale;
  const worldRight = (width - offsetX) / scale;
  const worldBottom = (height - offsetY) / scale;

  const tileMinX = Math.floor(worldLeft / TILE_SIZE);
  const tileMaxX = Math.floor(worldRight / TILE_SIZE);
  const tileMinY = Math.floor(worldTop / TILE_SIZE);
  const tileMaxY = Math.floor(worldBottom / TILE_SIZE);
  const maxTile = 2 ** zoom;

  const tasks: Promise<void>[] = [];
  for (let ty = tileMinY; ty <= tileMaxY; ty++) {
    for (let tx = tileMinX; tx <= tileMaxX; tx++) {
      if (tx < 0 || ty < 0 || tx >= maxTile || ty >= maxTile) continue;
      const url = TILE_URL.replace('{z}', String(zoom))
        .replace('{y}', String(ty))
        .replace('{x}', String(tx));
      const dx = tx * TILE_SIZE * scale + offsetX;
      const dy = ty * TILE_SIZE * scale + offsetY;
      const dw = TILE_SIZE * scale;
      const dh = TILE_SIZE * scale;
      tasks.push(
        loadTile(url)
          .then((img) => {
            ctx.drawImage(img, dx, dy, dw, dh);
          })
          .catch(() => {
            /* leave base fill for failed tiles */
          })
      );
    }
  }
  await Promise.all(tasks);

  // Subtle darken so track pops
  ctx.fillStyle = 'rgba(15, 23, 42, 0.12)';
  ctx.fillRect(0, 0, width, height);

  // Track outline + stroke
  const step = Math.max(1, Math.floor(points.length / 800));
  const drawTrack = (color: string, lineWidth: number) => {
    ctx.beginPath();
    let started = false;
    for (let i = 0; i < points.length; i += step) {
      const p = points[i];
      const w = latLngToWorld(p.lat, p.lng, zoom);
      const x = w.x * scale + offsetX;
      const y = w.y * scale + offsetY;
      if (!started) {
        ctx.moveTo(x, y);
        started = true;
      } else {
        ctx.lineTo(x, y);
      }
    }
    const last = points[points.length - 1];
    const lw = latLngToWorld(last.lat, last.lng, zoom);
    ctx.lineTo(lw.x * scale + offsetX, lw.y * scale + offsetY);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
  };
  drawTrack('rgba(255,255,255,0.85)', Math.max(6, width * 0.01));
  drawTrack('#0284c7', Math.max(3, width * 0.0055));

  // Start / end dots
  const start = latLngToWorld(points[0].lat, points[0].lng, zoom);
  const end = latLngToWorld(points[points.length - 1].lat, points[points.length - 1].lng, zoom);
  const r = Math.max(5, width * 0.008);
  ctx.fillStyle = '#22c55e';
  ctx.beginPath();
  ctx.arc(start.x * scale + offsetX, start.y * scale + offsetY, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#ef4444';
  ctx.beginPath();
  ctx.arc(end.x * scale + offsetX, end.y * scale + offsetY, r, 0, Math.PI * 2);
  ctx.fill();

  return canvas.toDataURL('image/jpeg', 0.92);
}
