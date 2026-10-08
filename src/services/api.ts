import {
  User,
  Hazard,
  Project,
  Site,
  SiteVisit,
  Evidence,
  Intervention,
  ActionItem,
  AuditLog,
  NotificationItem,
  ReferenceData,
  DashboardStats,
  ComprehensiveReportData,
  Contractor
} from '../types/index.ts';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorBody = await response.json();
        if (errorBody.error) errorMessage = errorBody.error;
      } catch (e) {
        // ignore json parse error
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error: any) {
    console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, error);
    throw error;
  }
}

export interface AuthResponse {
  success: boolean;
  user: User;
  roles: any[];
  tier: string;
  readonly: boolean;
}

export interface LoginGroupMember {
  username: string;
  role: string;
  name: string;
  role_title: string;
  department: string;
}

export interface LoginGroup {
  tier: string;
  label: string;
  members: LoginGroupMember[];
}

export interface CmsBranding {
  app_name: string;
  app_tagline: string;
  agency_name: string;
  footer_text: string;
  primary_color: string;
  logo_url: string;
}

export interface CmsUser {
  id: string;
  name: string;
  username: string;
  email: string;
  role: string;
  role_title?: string;
  department?: string;
  phone?: string;
  active: boolean;
  quick_access?: boolean;
  created_at?: string;
  last_login?: string;
}

export interface CmsBackup {
  filename: string;
  created_at: string;
  size: number;
}

export const api = {
  // Auth
  getCurrentUser: () => request<{ user: User | null; roles: any[]; authenticated: boolean; tier: string; readonly: boolean }>('/auth/me'),
  login: (username: string, password: string) => request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  quickLogin: (role: string) => request<AuthResponse>('/auth/quick-login', { method: 'POST', body: JSON.stringify({ role }) }),
  logout: () => request<{ success: boolean }>('/auth/logout', { method: 'POST' }),
  switchRole: (role_id: string) => request<AuthResponse>('/auth/switch-role', {
    method: 'POST',
    body: JSON.stringify({ role_id })
  }),
  getLoginGroups: () => request<LoginGroup[]>('/auth/login-groups'),
  getUsers: () => request<User[]>('/users'),
  createUser: (data: Partial<User>) => request<User>('/users', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Dashboard
  getDashboardStats: () => request<DashboardStats>('/dashboard/stats'),

  // Hazards
  getHazards: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<Hazard[]>(`/hazards${query ? `?${query}` : ''}`);
  },
  getHazardById: (id: string) => request<Hazard>(`/hazards/${id}`),
  createHazard: (data: Partial<Hazard> & { evidence?: any[] }) => request<Hazard>('/hazards', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  verifyHazard: (id: string, payload: { is_valid: boolean; verification_notes: string; request_inspection?: boolean }) =>
    request<{ success: boolean; hazard: Hazard }>(`/hazards/${id}/verify`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  assessHazard: (id: string, payload: any) =>
    request<{ success: boolean; hazard: Hazard }>(`/hazards/${id}/assess`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  recommendIntervention: (id: string, payload: any) =>
    request<{ success: boolean; intervention: Intervention; hazard: Hazard }>(`/hazards/${id}/intervention`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  bulkVerifyHazards: (ids: string[], action: 'VERIFY' | 'INVALIDATE', notes?: string) =>
    request<{ success: boolean; updated_count: number }>('/hazards/bulk-verify', {
      method: 'POST',
      body: JSON.stringify({ ids, action, notes })
    }),

  // Projects & Sites
  getProjects: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<Project[]>(`/projects${query ? `?${query}` : ''}`);
  },
  updateHazard: (id: string, data: Partial<Hazard>) => request<Hazard>(`/hazards/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteHazard: (id: string) => request<{ success: boolean; deleted_id: string }>(`/hazards/${id}`, {
    method: 'DELETE'
  }),
  getProjectById: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: Partial<Project>) => request<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getSites: () => request<Site[]>('/sites'),
  createSite: (data: Partial<Site>) => request<Site>('/sites', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  getSiteVisits: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<SiteVisit[]>(`/site-visits${query ? `?${query}` : ''}`);
  },
  updateSite: (id: string, data: Partial<Site>) => request<Site>(`/sites/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteSite: (id: string) => request<{ success: boolean; deleted_id: string }>(`/sites/${id}`, {
    method: 'DELETE'
  }),
  updateProject: (id: string, data: Partial<Project>) => request<Project>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteProject: (id: string) => request<{ success: boolean; deleted_id: string }>(`/projects/${id}`, {
    method: 'DELETE'
  }),
  createSiteVisit: (data: Partial<SiteVisit> & { evidence?: any[]; stage_tag?: string }) =>
    request<SiteVisit>('/site-visits', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  updateSiteVisit: (id: string, data: Partial<SiteVisit>) => request<SiteVisit>(`/site-visits/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteSiteVisit: (id: string) => request<{ success: boolean; deleted_id: string }>(`/site-visits/${id}`, {
    method: 'DELETE'
  }),
  getMonitoringTimeline: (site_id: string) => request<any>(`/monitoring/timeline/${site_id}`),

  // Contractors
  getContractors: () => request<Contractor[]>('/contractors?active=1'),
  getAllContractors: () => request<Contractor[]>('/contractors'),
  updateContractor: (id: string, data: Partial<Contractor>) => request<Contractor>(`/contractors/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteContractor: (id: string) => request<{ success: boolean; deactivated_id: string }>(`/contractors/${id}`, {
    method: 'DELETE'
  }),
  createContractor: (data: Partial<Contractor>) => request<Contractor>('/contractors', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Interventions & Actions
  createIntervention: (hazard_id: string, data: any) =>
    request<{ success: boolean; intervention: Intervention; hazard: Hazard }>(`/hazards/${hazard_id}/intervention`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Approval flow — Stage 1: Intervention approvals
  directorApproveIntervention: (id: string, notes?: string) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/director-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes })
    }),
  executiveApproveIntervention: (id: string, notes?: string, approved_amount_ngn?: number) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/executive-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes, approved_amount_ngn })
    }),
  rejectIntervention: (id: string, rejection_reason: string) =>
    request<{ success: boolean; intervention: Intervention }>(`/interventions/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason })
    }),
  getInterventionsByQueue: (queue: 'director' | 'executive' | 'approved') => {
    const q = new URLSearchParams({ queue }).toString();
    return request<Intervention[]>(`/interventions?${q}`);
  },

  // Approval flow — Stage 2: Project approvals
  rejectProject: (id: string, rejection_reason: string) =>
    request<{ success: boolean; project: Project }>(`/projects/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason })
    }),
  executiveApproveProject: (id: string, notes?: string, approved_amount_ngn?: number) =>
    request<{ success: boolean; project: Project }>(`/projects/${id}/executive-approve`, {
      method: 'POST',
      body: JSON.stringify({ notes, approved_amount_ngn })
    }),
  getProjectsByQueue: (queue: 'approval') => {
    const q = new URLSearchParams({ queue }).toString();
    return request<Project[]>(`/projects?${q}`);
  },

  getInterventions: () => request<Intervention[]>('/interventions'),
  updateIntervention: (id: string, data: Partial<Intervention>) =>
    request<Intervention>(`/interventions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),
  getActions: () => request<ActionItem[]>('/actions'),
  createAction: (data: Partial<ActionItem>) => request<ActionItem>('/actions', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updateAction: (id: string, data: Partial<ActionItem>) =>
    request<ActionItem>(`/actions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),

  // Evidence
  getEvidence: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<Evidence[]>(`/evidence${query ? `?${query}` : ''}`);
  },
  uploadActionEvidence: (id: string, data: any) =>
    request<{ success: boolean; evidence: any; action: ActionItem }>(`/actions/${id}/evidence`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  deleteAction: (id: string) => request<{ success: boolean; deleted_id: string }>(`/actions/${id}`, {
    method: 'DELETE'
  }),
  deleteIntervention: (id: string) => request<{ success: boolean; deleted_id: string }>(`/interventions/${id}`, {
    method: 'DELETE'
  }),
  uploadEvidence: (data: any) => request<Evidence>('/evidence/upload', {
    method: 'POST',
    body: JSON.stringify(data)
  }),

  // Comprehensive Report Engine
  generateComprehensiveReport: (filters: any) =>
    request<ComprehensiveReportData>('/reports/hazard-intervention-planning', {
      method: 'POST',
      body: JSON.stringify(filters)
    }),

  // GIS / Map
  getMapPoints: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<{ hazard_points: any[]; project_points: any[]; total_points: number }>(`/map/points${query ? `?${query}` : ''}`);
  },

  // Analytics & AI Assistant
  getAnalytics: () => request<any>('/analytics'),
  askAiAssistant: (query: string) => request<any>('/ai/query', {
    method: 'POST',
    body: JSON.stringify({ query })
  }),

  // Public Portal (no login required)
  submitPublicReport: (data: any) => request<{ success: boolean; tracking_code: string; hazard_id: string; message: string }>('/public/report', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  trackPublicReport: (code: string) => request<any>(`/public/track/${encodeURIComponent(code)}`),
  publicSignup: (data: { name?: string; username: string; email: string; password: string; phone?: string }) =>
    request<{ success: boolean; user: any; message: string }>('/public/signup', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  // Reference Data & Settings
  getReferenceData: () => request<ReferenceData>('/reference-data'),
  updateReferenceData: (data: Partial<ReferenceData>) => request<ReferenceData>('/reference-data', {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  getAuditLogs: (params: Record<string, string> = {}) => {
    const query = new URLSearchParams(params).toString();
    return request<AuditLog[]>(`/audit-logs${query ? `?${query}` : ''}`);
  },
  getSettings: () => request<any>('/settings'),
  updateSettings: (data: any) => request<any>('/settings', {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  getNotifications: () => request<NotificationItem[]>('/notifications'),
  markNotificationRead: (id: string) => request<{ success: boolean }>(`/notifications/${id}/read`, { method: 'POST' }),

  // Backup & Restore
  createBackup: (label?: string) => request<{ filename: string; timestamp: string; size: number }>('/backup/create', {
    method: 'POST',
    body: JSON.stringify({ label })
  }),
  listBackups: () => request<Array<{ filename: string; created_at: string; size: number }>>('/backup/list'),
  restoreBackup: (filename: string) => request<{ success: boolean }>('/backup/restore', {
    method: 'POST',
    body: JSON.stringify({ filename })
  }),
  resetDatabase: () => request<{ success: boolean; message: string }>('/database/reset', { method: 'POST' }),
  clearDatabase: () => request<{ success: boolean; message: string }>('/database/clear', { method: 'POST' }),

  // ==================== CMS ====================
  cmsBranding: () => request<CmsBranding>('/cms/branding'),
  cmsUpdateBranding: (data: Partial<CmsBranding> & { logo_base64?: string; logo_mime?: string }) =>
    request<CmsBranding>('/cms/branding', { method: 'PUT', body: JSON.stringify(data) }),

  cmsUsers: () => request<CmsUser[]>('/cms/users'),
  cmsCreateUser: (data: { name?: string; username: string; email: string; password: string; role?: string; phone?: string; department?: string }) =>
    request<CmsUser>('/cms/users', { method: 'POST', body: JSON.stringify(data) }),
  cmsUpdateUser: (id: string, data: Partial<CmsUser> & { password?: string }) =>
    request<CmsUser>(`/cms/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  cmsDeleteUser: (id: string) =>
    request<{ success: boolean; deleted_id: string }>(`/cms/users/${id}`, { method: 'DELETE' }),
  cmsSuspendUser: (id: string) =>
    request<{ success: boolean; active: boolean }>(`/cms/users/${id}/suspend`, { method: 'POST' }),
  cmsResetPassword: (id: string, password: string) =>
    request<{ success: boolean }>(`/cms/users/${id}/reset-password`, {
      method: 'POST',
      body: JSON.stringify({ password })
    }),

  cmsDbStats: () => request<Record<string, number>>('/cms/database/stats'),
  cmsDbFlush: () => request<{ success: boolean; snapshot: string; message: string }>('/cms/database/flush', { method: 'POST' }),
  cmsDbReseed: () => request<{ success: boolean; snapshot: string; message: string }>('/cms/database/reseed', { method: 'POST' }),
  cmsDbSnapshot: (label: string) =>
    request<{ success: boolean; filename: string; size: number; created_at: string }>('/cms/database/snapshot', {
      method: 'POST',
      body: JSON.stringify({ label })
    }),
  cmsDbBackups: () => request<CmsBackup[]>('/cms/database/backups'),
  cmsDbRollback: (filename: string) =>
    request<{ success: boolean; restored: string; presnapshot: string }>('/cms/database/rollback', {
      method: 'POST',
      body: JSON.stringify({ filename })
    }),

  // ==================== Reference Data (Dropdowns) ====================
  cmsFullReferenceData: () =>
    request<any>('/reference-data'),

  cmsRefCategories: () =>
    request<string[]>('/reference-data/categories'),

  cmsAddCategory: (name: string) =>
    request<{ success: boolean; hazard_categories: string[] }>(
      '/reference-data/categories',
      { method: 'POST', body: JSON.stringify({ name }) }
    ),

  cmsUpdateCategory: (oldName: string, newName: string) =>
    request<{ success: boolean; hazard_categories: string[] }>(
      `/reference-data/categories/${encodeURIComponent(oldName)}`,
      { method: 'PUT', body: JSON.stringify({ name: newName }) }
    ),

  cmsDeleteCategory: (name: string) =>
    request<{ success: boolean; hazard_categories: string[] }>(
      `/reference-data/categories/${encodeURIComponent(name)}`,
      { method: 'DELETE' }
    ),

  cmsAddState: (name: string) =>
    request<{ success: boolean; states_and_lgas: Record<string, string[]> }>(
      '/reference-data/states',
      { method: 'POST', body: JSON.stringify({ name }) }
    ),

  cmsDeleteState: (name: string) =>
    request<{ success: boolean; states_and_lgas: Record<string, string[]> }>(
      `/reference-data/states/${encodeURIComponent(name)}`,
      { method: 'DELETE' }
    ),

  cmsAddLga: (state: string, name: string) =>
    request<{ success: boolean; states_and_lgas: Record<string, string[]> }>(
      `/reference-data/states/${encodeURIComponent(state)}/lgas`,
      { method: 'POST', body: JSON.stringify({ name }) }
    ),

  cmsDeleteLga: (state: string, name: string) =>
    request<{ success: boolean; states_and_lgas: Record<string, string[]> }>(
      `/reference-data/states/${encodeURIComponent(state)}/lgas/${encodeURIComponent(name)}`,
      { method: 'DELETE' }
    ),

  // ==================== Generic Reference Lists ====================
  cmsRefListKeys: () =>
    request<Record<string, string[]>>('/reference-data/lists'),

  cmsRefListAdd: (key: string, name: string) =>
    request<{ success: boolean; key: string; values: string[] }>(
      `/reference-data/lists/${encodeURIComponent(key)}`,
      { method: 'POST', body: JSON.stringify({ name }) }
    ),

  cmsRefListUpdate: (key: string, oldName: string, newName: string) =>
    request<{ success: boolean; key: string; values: string[] }>(
      `/reference-data/lists/${encodeURIComponent(key)}/${encodeURIComponent(oldName)}`,
      { method: 'PUT', body: JSON.stringify({ name: newName }) }
    ),

  cmsRefListDelete: (key: string, name: string) =>
    request<{ success: boolean; key: string; values: string[] }>(
      `/reference-data/lists/${encodeURIComponent(key)}/${encodeURIComponent(name)}`,
      { method: 'DELETE' }
    )
};

// Local storage offline-draft helper for field inspectors
export const offlineDrafts = {
  saveDraft: (key: string, data: any) => {
    try {
      localStorage.setItem(`ef_draft_${key}`, JSON.stringify({ data, saved_at: new Date().toISOString() }));
    } catch (e) {
      console.warn('LocalStorage draft save error', e);
    }
  },
  getDraft: (key: string) => {
    try {
      const item = localStorage.getItem(`ef_draft_${key}`);
      return item ? JSON.parse(item) : null;
    } catch (e) {
      return null;
    }
  },
  clearDraft: (key: string) => {
    localStorage.removeItem(`ef_draft_${key}`);
  }
};