export type UserRole =
  | 'SUPER_ADMIN'
  | 'EXECUTIVE'
  | 'COORDINATOR'
  | 'INSPECTOR'
  | 'TECHNICAL_OFFICER'
  | 'PLANNING_OFFICER'
  | 'AUDITOR';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  role_title: string;
  department: string;
  phone: string;
  active: boolean;
  created_at: string;
}

export type HazardSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type HazardUrgency = 'IMMEDIATE' | 'HIGH' | 'NORMAL' | 'ROUTINE';

export type HazardStatus =
  | 'Draft'
  | 'Submitted'
  | 'Under Review'
  | 'Verified'
  | 'Rejected/Invalid'
  | 'Assessment Required'
  | 'Assessed'
  | 'Intervention Recommended'
  | 'Prioritised'
  | 'Intervention Planned'
  | 'Intervention Approved'
  | 'Intervention Assigned'
  | 'Intervention Ongoing'
  | 'Intervention Completed'
  | 'Follow-up Verification'
  | 'Resolved'
  | 'Closed';

export interface HazardAssessment {
  severity_score: number;
  urgency_score: number;
  exposure_score: number;
  impact_score: number;
  escalation_risk_score: number;
  calculated_priority_score: number;
  recommended_priority: HazardSeverity;
  environmental_impact: string;
  economic_impact: string;
  social_impact: string;
  technical_findings: string;
  recommended_intervention_type: string;
  assessed_by: string;
  assessed_at: string;
}

export interface RecommendedIntervention {
  intervention_id?: string;
  title: string;
  scope_description: string;
  estimated_cost_ngn: number;
  proposed_funding: string;
  responsible_department: string;
  responsible_officer: string;
  proposed_start_date: string;
  proposed_completion_date: string;
  expected_outcome: string;
}

export interface Hazard {
  id: string;
  title: string;
  category: string;
  hazard_type: string;
  description: string;
  date_observed: string;
  date_reported: string;
  reporter_name: string;
  reporter_type: 'PUBLIC' | 'FIELD_OFFICER' | 'COMMUNITY_LEADER' | 'LGA_OFFICIAL';
  reporter_contact: string;
  state: string;
  lga: string;
  ward: string;
  community: string;
  address_description: string;
  latitude: number;
  longitude: number;
  estimated_affected_area_sqm: number;
  estimated_affected_population: number;
  estimated_affected_assets: string;
  potential_impact: string;
  severity: HazardSeverity;
  urgency: HazardUrgency;
  status: HazardStatus;
  linked_project_id?: string;
  verification_notes?: string;
  verified_by?: string;
  verified_at?: string;
  assessment?: HazardAssessment;
  recommended_intervention?: RecommendedIntervention;
  is_recurring?: boolean;
  recurring_count?: number;
  tracking_code?: string;
  evidence_files?: Evidence[];
  actions?: ActionItem[];
  intervention?: Intervention;
}

export type ProjectStatus = 'Proposed' | 'Approved' | 'Procurement' | 'Active' | 'Suspended' | 'Delayed' | 'Completed' | 'Cancelled';

export interface Milestone {
  id: string;
  title: string;
  due_date: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Delayed';
  progress_percentage: number;
}

export interface Project {
  id: string;
  title: string;
  category: string;
  description: string;
  state: string;
  lga: string;
  ward: string;
  community: string;
  site_name: string;
  latitude: number;
  longitude: number;
  funding_source: string;
  approved_amount_ngn: number;
  contract_amount_ngn: number;
  contractor: string;
  implementing_agency: string;
  project_officer: string;
  start_date: string;
  expected_completion_date: string;
  actual_completion_date?: string;
  planned_percentage: number;
  actual_percentage: number;
  status: ProjectStatus;
  milestones: Milestone[];
  remarks: string;
  created_at: string;
  sites?: Site[];
  site_visits?: SiteVisit[];
  linked_hazards?: Hazard[];
  evidence_files?: Evidence[];
}

export interface Site {
  id: string;
  project_id: string;
  name: string;
  state: string;
  lga: string;
  community: string;
  latitude: number;
  longitude: number;
  terrain_type: string;
  ecological_zone: string;
  baseline_condition: string;
  assigned_inspector: string;
  created_at: string;
}

export interface SiteVisit {
  id: string;
  site_id: string;
  project_id: string;
  officer_name: string;
  visit_date: string;
  gps_latitude: number;
  gps_longitude: number;
  purpose: string;
  weather_conditions: string;
  activities_observed: string;
  progress_percentage: number;
  work_completed: string;
  work_outstanding: string;
  materials_equipment: string;
  quality_observations: string;
  safety_observations: string;
  problems_challenges: string;
  recommendations: string;
  officer_comments: string;
  stage: 'Initial' | 'Visit 1' | 'Visit 2' | 'Visit 3' | 'Current' | 'Follow-up';
  created_at: string;
}

export interface Evidence {
  id: string;
  hazard_id?: string;
  project_id?: string;
  site_id?: string;
  visit_id?: string;
  file_name: string;
  file_type: string;
  file_size: number;
  media_type: 'photo' | 'video' | 'document';
  file_url: string;
  uploader_name: string;
  uploader_id: string;
  upload_date: string;
  description: string;
  gps_latitude?: number;
  gps_longitude?: number;
  stage_tag?: 'before' | 'during' | 'after' | 'evidence';
}

export interface Intervention {
  id: string;
  hazard_id: string;
  project_id?: string;
  title: string;
  technical_description: string;
  priority: HazardSeverity;
  estimated_scope: string;
  estimated_cost_ngn: number;
  proposed_funding: string;
  responsible_department: string;
  responsible_officer: string;
  proposed_start_date: string;
  proposed_completion_date: string;
  actual_start_date?: string;
  actual_completion_date?: string;
  expected_outcome: string;
  approval_status: 'Proposed' | 'Under Review' | 'Approved' | 'Rejected' | 'Fund Allocated';
  implementation_status: 'Not Started' | 'Procurement' | 'Ongoing' | 'Suspended' | 'Completed' | 'Follow-up Verified';
  progress_percentage: number;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
}

export interface ActionItem {
  id: string;
  hazard_id?: string;
  project_id?: string;
  intervention_id?: string;
  title: string;
  description: string;
  responsible_person: string;
  responsible_organization: string;
  priority: HazardSeverity;
  due_date: string;
  completion_date?: string;
  status: 'Open' | 'Assigned' | 'In Progress' | 'Overdue' | 'Completed' | 'Verified' | 'Closed';
  progress_percentage: number;
  evidence_summary?: string;
  verification_comments?: string;
  verified_by?: string;
  created_at: string;
  is_overdue?: boolean;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user_name: string;
  user_role: string;
  action: string;
  entity_type: 'HAZARD' | 'PROJECT' | 'SITE' | 'VISIT' | 'INTERVENTION' | 'ACTION' | 'EVIDENCE' | 'SETTINGS';
  entity_id: string;
  old_value: any;
  new_value: any;
  ip_address: string;
  device_info: string;
  details: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  category: 'HAZARD' | 'PROJECT' | 'ACTION' | 'INTERVENTION' | 'SYSTEM';
  timestamp: string;
  read: boolean;
  link?: string;
  priority: 'CRITICAL' | 'HIGH' | 'NORMAL';
}

export interface PriorityWeights {
  severity_weight: number;
  urgency_weight: number;
  exposure_weight: number;
  impact_weight: number;
  escalation_weight: number;
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
}


export interface Contractor {
  id: string;
  name: string;
  registration_no?: string;
  category?: string;
  specialties?: string[];
  contact_person?: string;
  phone?: string;
  email?: string;
  address?: string;
  state?: string;
  active?: boolean;
  rating?: number;
  created_at?: string;
}

export interface ReferenceData {
  hazard_categories: string[];
  project_categories: string[];
  states_and_lgas: Record<string, string[]>;
  priority_weights: PriorityWeights;
  intervention_types: string[];
  implementing_agencies: string[];
}

export interface DashboardStats {
  kpis: {
    totalProjects: number;
    activeProjects: number;
    completedProjects: number;
    totalSites: number;
    totalSiteVisits: number;
    totalHazards: number;
    unverifiedHazards: number;
    verifiedHazards: number;
    criticalHazards: number;
    highHazards: number;
    awaitingIntervention: number;
    activeInterventions: number;
    completedInterventions: number;
    outstandingActions: number;
    overdueActions: number;
    totalInterventionCost: number;
    totalApprovedProjectFunding: number;
  };
  charts: {
    hazardsByCategory: Record<string, number>;
    hazardsBySeverity: Record<string, number>;
    hazardsByState: Record<string, number>;
    hazardsByLga: Record<string, number>;
    projectsByStatus: Record<string, number>;
    monthlyReports: Array<{ month: string; reports: number; visits: number }>;
    resolvedVsUnresolved: { resolved: number; unresolved: number };
  };
}

export interface ComprehensiveReportData {
  report_metadata: {
    report_title: string;
    organization: string;
    department: string;
    generated_at: string;
    generated_by: string;
    reporting_scope: {
      state: string;
      lga: string;
      category: string;
      severity: string;
    };
  };
  executive_summary_stats: {
    totalReports: number;
    verifiedReports: number;
    unverifiedReports: number;
    invalidReports: number;
    criticalHazards: number;
    highHazards: number;
    mediumHazards: number;
    lowHazards: number;
    requiringIntervention: number;
    alreadyReceivingIntervention: number;
    resolvedHazards: number;
  };
  geographic_analysis: {
    by_state: Record<string, number>;
    by_lga: Record<string, number>;
    by_ward: Record<string, number>;
  };
  hazard_category_analysis: Record<string, { count: number; percentage: number }>;
  severity_analysis: Record<string, { count: number; percentage: number }>;
  detailed_hazard_register: Array<{
    hazard_id: string;
    title: string;
    category: string;
    description: string;
    state: string;
    lga: string;
    ward: string;
    community: string;
    coordinates: string;
    date_reported: string;
    reporter: string;
    verification_status: string;
    verified_by: string;
    severity: string;
    priority_score: any;
    potential_impact: string;
    recommended_intervention: string;
    estimated_cost_ngn: number;
    responsible_authority: string;
    photographs: Array<{ id: string; file_name: string; url: string; description: string }>;
    video_references: Array<{ evidence_id: string; file_name: string; date_time: string; description: string; secure_link: string }>;
  }>;
  intervention_recommendations: Array<{
    hazard_id: string;
    recommended_intervention: string;
    priority: string;
    estimated_cost_ngn: number;
    responsible_organization: string;
    expected_timeline: string;
  }>;
  planning_analysis: {
    immediate_intervention_requirements: number;
    short_term_requirements: number;
    medium_term_requirements: number;
    long_term_requirements: number;
    total_estimated_pipeline_budget_ngn: number;
    high_risk_zones: Array<{ lga: string; count: number }>;
    recurring_hotspots: Array<{ id: string; community: string; lga: string; recurrence_count: number }>;
  };
  conclusion_text: string;
  sign_off: {
    prepared_by: string;
    reviewed_by: string;
    approved_by: string;
  };
}
