import React from 'react';
import { Navigation } from 'lucide-react';

interface DirectionsLinkProps {
  lat: number | null | undefined;
  lng: number | null | undefined;
  label?: string;
  className?: string;
  /** If provided, appended to the label after a " — " separator */
  destination?: string;
}

/**
 * Renders a link that opens Google Maps turn-by-turn directions
 * to the given coordinates. Works on desktop (browser) and on mobile
 * (opens the Google Maps app or offers the choice of maps apps).
 * Returns null when coordinates are missing or invalid.
 */
export const DirectionsLink: React.FC<DirectionsLinkProps> = ({
  lat,
  lng,
  label = 'Directions',
  className = 'text-blue-700 hover:text-blue-950 font-semibold inline-flex items-center text-xs',
  destination,
}) => {
  const latN = Number(lat);
  const lngN = Number(lng);
  if (!isFinite(latN) || !isFinite(lngN)) return null;
  if (latN < -90 || latN > 90) return null;
  if (lngN < -180 || lngN > 180) return null;

  const url = `https://www.google.com/maps/dir/?api=1&destination=${latN},${lngN}`;
  const text = destination ? `${label} — ${destination}` : label;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
      title="Open turn-by-turn directions in your maps app"
    >
      <Navigation className="w-3.5 h-3.5 mr-1" />
      {text}
    </a>
  );
};
