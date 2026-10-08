import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Hazard, Project, HazardSeverity } from '../../types/index.ts';
import {
  MapPin,
  Layers,
  Filter,
  Eye,
  AlertTriangle,
  FolderGit2,
  Maximize2,
  Compass
} from 'lucide-react';

interface GisMapModuleProps {
  hazards: Hazard[];
  projects: Project[];
  onSelectHazard: (hazard: Hazard) => void;
  onSelectProject: (project: Project) => void;
  initialCenter?: [number, number];
}

export const GisMapModule: React.FC<GisMapModuleProps> = ({
  hazards,
  projects,
  onSelectHazard,
  onSelectProject,
  initialCenter
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerGroupRef = useRef<L.LayerGroup | null>(null);

  const [showHazards, setShowHazards] = useState(true);
  const [showProjects, setShowProjects] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [selectedState, setSelectedState] = useState<string>('ALL');

  const states = Array.from(new Set([...hazards.map(h => h.state), ...projects.map(p => p.state)])).sort();

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const centerPos: [number, number] = initialCenter || [6.5438, 5.8987]; // Edo State center
      const map = L.map(mapContainerRef.current, {
        center: centerPos,
        zoom: initialCenter ? 12 : 9,
        minZoom: 6,
        maxZoom: 18
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | Edo State Ecological Fund Agency (EDEFA)'
      }).addTo(map);

      const markersGroup = L.layerGroup().addTo(map);
      markersLayerGroupRef.current = markersGroup;
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Center if initialCenter changes
  useEffect(() => {
    if (mapInstanceRef.current && initialCenter) {
      mapInstanceRef.current.setView(initialCenter, 13);
    }
  }, [initialCenter]);

  // Update Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersGroup = markersLayerGroupRef.current;
    if (!map || !markersGroup) return;

    markersGroup.clearLayers();

    // 1. Hazards Markers
    if (showHazards) {
      hazards.forEach(hazard => {
        if (!hazard.latitude || !hazard.longitude) return;
        if (filterSeverity !== 'ALL' && hazard.severity !== filterSeverity) return;
        if (selectedState !== 'ALL' && hazard.state !== selectedState) return;

        let color = '#10b981'; // LOW = green
        if (hazard.severity === 'CRITICAL') color = '#e11d48'; // Red
        else if (hazard.severity === 'HIGH') color = '#ea580c'; // Orange
        else if (hazard.severity === 'MEDIUM') color = '#d97706'; // Amber

        const marker = L.circleMarker([hazard.latitude, hazard.longitude], {
          radius: hazard.severity === 'CRITICAL' ? 10 : 8,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.85
        });

        const popupContent = `
          <div style="font-family: sans-serif; font-size: 12px; min-width: 200px; padding: 4px;">
            <div style="font-size: 10px; font-weight: bold; color: ${color}; text-transform: uppercase;">
              ${hazard.severity} HAZARD • ${hazard.status}
            </div>
            <div style="font-size: 13px; font-weight: bold; color: #0f172a; margin-top: 2px;">
              ${hazard.title}
            </div>
            <div style="font-size: 11px; color: #475569; margin-top: 4px;">
              <strong>${hazard.community}</strong>, ${hazard.lga}, ${hazard.state} State
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
              Category: ${hazard.category}
            </div>
            <div style="font-size: 10px; font-family: monospace; color: #94a3b8; margin-top: 4px;">
              GPS: ${hazard.latitude.toFixed(5)}, ${hazard.longitude.toFixed(5)}
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);
        marker.on('click', () => {
          // Can emit select
        });
        marker.addTo(markersGroup);
      });
    }

    // 2. Project Markers
    if (showProjects) {
      projects.forEach(project => {
        if (!project.latitude || !project.longitude) return;
        if (selectedState !== 'ALL' && project.state !== selectedState) return;

        const marker = L.circleMarker([project.latitude, project.longitude], {
          radius: 9,
          fillColor: '#047857', // Emerald
          color: '#f59e0b', // Amber border
          weight: 2.5,
          opacity: 1,
          fillOpacity: 0.9
        });

        const popupContent = `
          <div style="font-family: sans-serif; font-size: 12px; min-width: 220px; padding: 4px;">
            <div style="font-size: 10px; font-weight: bold; color: #047857; text-transform: uppercase;">
              PROJECT • ${project.status} (${project.actual_percentage}%)
            </div>
            <div style="font-size: 13px; font-weight: bold; color: #0f172a; margin-top: 2px;">
              ${project.title}
            </div>
            <div style="font-size: 11px; color: #475569; margin-top: 4px;">
              <strong>${project.community}</strong>, ${project.lga}, ${project.state} State
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
              Contractor: <strong>${project.contractor}</strong>
            </div>
            <div style="font-size: 11px; color: #047857; font-weight: bold; margin-top: 4px;">
              Contract: ₦${(project.contract_amount_ngn / 1e6).toFixed(1)} Million
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);
        marker.addTo(markersGroup);
      });
    }
  }, [hazards, projects, showHazards, showProjects, filterSeverity, selectedState]);

  return (
    <div id="gis-map-module" className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-bold text-slate-900">Edo State GIS & Spatial Intelligence Map</h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              Interactive Geoportal
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Module 11: Georeferenced coordinates of Edo State registered ecological hazards, project sites, and active civil interventions.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-600 border border-white shadow-xs"></span>
            <span className="text-slate-700 font-medium">Critical</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-orange-500 border border-white shadow-xs"></span>
            <span className="text-slate-700 font-medium">High</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-amber-500 border border-white shadow-xs"></span>
            <span className="text-slate-700 font-medium">Medium</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-700 border-2 border-amber-400 shadow-xs"></span>
            <span className="text-slate-700 font-medium">Active Project</span>
          </div>
        </div>
      </div>

      {/* Map Controls Toolbar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          {/* Layer toggles */}
          <label className="inline-flex items-center space-x-1.5 cursor-pointer font-semibold text-slate-800">
            <input
              type="checkbox"
              checked={showHazards}
              onChange={e => setShowHazards(e.target.checked)}
              className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
            />
            <span>Hazard Points ({hazards.length})</span>
          </label>

          <label className="inline-flex items-center space-x-1.5 cursor-pointer font-semibold text-slate-800">
            <input
              type="checkbox"
              checked={showProjects}
              onChange={e => setShowProjects(e.target.checked)}
              className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
            />
            <span>Projects ({projects.length})</span>
          </label>

          <div className="h-4 w-px bg-slate-300 mx-1"></div>

          {/* Severity filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-500">Severity:</span>
            <select
              value={filterSeverity}
              onChange={e => setFilterSeverity(e.target.value)}
              className="py-1 px-2 rounded-md border border-slate-300 bg-slate-50 text-xs"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">CRITICAL only</option>
              <option value="HIGH">HIGH only</option>
              <option value="MEDIUM">MEDIUM only</option>
              <option value="LOW">LOW only</option>
            </select>
          </div>

          {/* State filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-500">State:</span>
            <select
              value={selectedState}
              onChange={e => setSelectedState(e.target.value)}
              className="py-1 px-2 rounded-md border border-slate-300 bg-slate-50 text-xs"
            >
              <option value="ALL">All States ({states.length})</option>
              {states.map(st => (
                <option key={st} value={st}>{st}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => {
            if (mapInstanceRef.current) {
              mapInstanceRef.current.setView([6.5438, 5.8987], 9);
            }
          }}
          className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 font-semibold cursor-pointer"
        >
          Reset Edo State View
        </button>
      </div>

      {/* Map Element */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div
          ref={mapContainerRef}
          id="gis-leaflet-canvas"
          className="w-full h-[600px] z-10"
        ></div>
      </div>
    </div>
  );
};
