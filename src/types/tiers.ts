// Tier definitions for the 4-tier permission model.
// Maps the 7 underlying roles to 4 tiers.

export type Tier = 'TIER_1_ADMIN' | 'TIER_2_EXEC' | 'TIER_3_DIRECTOR' | 'TIER_4_STAFF';

export type Role =
  | 'SUPER_ADMIN'
  | 'EXECUTIVE'
  | 'AUDITOR'
  | 'COORDINATOR'
  | 'INSPECTOR'
  | 'TECHNICAL_OFFICER'
  | 'PLANNING_OFFICER';

export const ROLE_TO_TIER: Record<Role, Tier> = {
  SUPER_ADMIN: 'TIER_1_ADMIN',
  EXECUTIVE: 'TIER_2_EXEC',
  AUDITOR: 'TIER_2_EXEC',
  COORDINATOR: 'TIER_3_DIRECTOR',
  INSPECTOR: 'TIER_3_DIRECTOR',
  TECHNICAL_OFFICER: 'TIER_4_STAFF',
  PLANNING_OFFICER: 'TIER_4_STAFF',
};

export const TIER_LABELS: Record<Tier, string> = {
  TIER_1_ADMIN: 'Super Admin',
  TIER_2_EXEC: 'Executive (Admin)',
  TIER_3_DIRECTOR: 'Director',
  TIER_4_STAFF: 'Staff',
};

// Read-only roles — full read access, no writes
export const READONLY_ROLES: Role[] = ['AUDITOR'];

// Module IDs from the sidebar
export type ModuleId =
  | 'dashboard' | 'map'
  | 'hazards' | 'sites' | 'visits' | 'monitoring' | 'evidence'
  | 'projects' | 'verification' | 'interventions' | 'actions'
  | 'reports' | 'analytics'
  | 'audit';

// Which tiers can see each module in the sidebar.
// This mirrors the backend permission matrix.
const MODULE_TIERS: Record<ModuleId, Tier[]> = {
  dashboard:    ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  map:          ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  hazards:      ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  sites:        ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  visits:       ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  monitoring:   ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  evidence:     ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  projects:     ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  verification: ['TIER_1_ADMIN', 'TIER_4_STAFF'],
  interventions:['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  actions:      ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  reports:      ['TIER_1_ADMIN', 'TIER_2_EXEC'],
  analytics:    ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
  audit:        ['TIER_1_ADMIN', 'TIER_2_EXEC'],
};

export function tierOf(role: string | undefined | null): Tier | '' {
  if (!role) return '';
  return ROLE_TO_TIER[role as Role] || '';
}

export function isReadonly(role: string | undefined | null): boolean {
  if (!role) return false;
  return READONLY_ROLES.includes(role as Role);
}

export function canAccess(moduleId: string, role: string | undefined | null): boolean {
  const tier = tierOf(role);
  if (!tier) return false;
  const allowed = MODULE_TIERS[moduleId as ModuleId];
  if (!allowed) return true; // unknown modules default to visible
  return allowed.includes(tier);
}

// Convenience: does this role have the given capability?
export function can(role: string | undefined | null, capability:
  | 'create_hazard' | 'verify_hazard' | 'assess_hazard' | 'recommend_intervention'
  | 'create_project' | 'create_site' | 'log_visit' | 'upload_evidence'
  | 'assign_action' | 'complete_action' | 'generate_report'
  | 'manage_settings' | 'manage_db' | 'view_audit'
): boolean {
  const tier = tierOf(role);
  if (!tier) return false;
  const ro = isReadonly(role);
  const table: Record<string, Tier[]> = {
    create_hazard:        ['TIER_1_ADMIN', 'TIER_3_DIRECTOR'],
    verify_hazard:        ['TIER_1_ADMIN', 'TIER_4_STAFF'],
    assess_hazard:        ['TIER_1_ADMIN', 'TIER_4_STAFF'],
    recommend_intervention:['TIER_1_ADMIN', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
    create_project:       ['TIER_1_ADMIN', 'TIER_3_DIRECTOR'],
    create_site:          ['TIER_1_ADMIN', 'TIER_3_DIRECTOR'],
    log_visit:            ['TIER_1_ADMIN', 'TIER_3_DIRECTOR'],
    upload_evidence:      ['TIER_1_ADMIN', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
    assign_action:        ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_3_DIRECTOR'],
    complete_action:      ['TIER_1_ADMIN', 'TIER_3_DIRECTOR', 'TIER_4_STAFF'],
    generate_report:      ['TIER_1_ADMIN', 'TIER_2_EXEC', 'TIER_4_STAFF'],
    manage_settings:      ['TIER_1_ADMIN'],
    manage_db:            ['TIER_1_ADMIN'],
    view_audit:           ['TIER_1_ADMIN', 'TIER_2_EXEC'],
  };
  if (ro) return false; // read-only roles can never do write actions
  return (table[capability] || []).includes(tier);
}


// T1 + T2 can edit and delete — Auditor is read-only so it's excluded
export function canEdit(role: string | undefined | null): boolean {
  const tier = tierOf(role);
  if (!tier) return false;
  if (isReadonly(role)) return false;
  return tier === 'TIER_1_ADMIN' || tier === 'TIER_2_EXEC';
}

export function canDelete(role: string | undefined | null): boolean {
  return canEdit(role);
}
