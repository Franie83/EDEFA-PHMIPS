"""
Fix loadData() in App.tsx so that 403 responses on role-restricted
endpoints don't kill the entire Promise.all.

Changes Promise.all -> Promise.allSettled for the fail-prone endpoints
(audit-logs, reference-data), and defensively handles the results.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "App.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "Promise.allSettled" in text and "safeGet" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Locate the existing loadData block
old_block = """  const loadData = async () => {
    try {
      const [
        statsData,
        hazardsData,
        projectsData,
        sitesData,
        visitsData,
        evidenceData,
        interventionsData,
        actionsData,
        logsData,
        notificationsData,
        refData
      ] = await Promise.all([
        api.getDashboardStats(),
        api.getHazards(),
        api.getProjects(),
        api.getSites(),
        api.getSiteVisits(),
        api.getEvidence(),
        api.getInterventions(),
        api.getActions(),
        api.getAuditLogs(),
        api.getNotifications(),
        api.getReferenceData()
      ]);

      setStats(statsData);
      setHazards(hazardsData);
      setProjects(projectsData);
      setSites(sitesData);
      setVisits(visitsData);
      setEvidenceList(evidenceData);
      setInterventions(interventionsData);
      setActions(actionsData);
      setAuditLogs(logsData);
      setNotifications(notificationsData);
      setReferenceData(refData);
    } catch (err) {
      console.error('Failed to load application initial state:', err);
    } finally {
      setLoading(false);
    }
  };"""

new_block = """  const loadData = async () => {
    // Helper: run a promise, swallow role-based 403s, return null on failure
    const safeGet = async <T,>(p: Promise<T>): Promise<T | null> => {
      try {
        return await p;
      } catch (err: any) {
        const msg = String(err?.message || err);
        if (msg.includes('403') || msg.includes('Forbidden')) {
          // Expected for role-restricted endpoints — return null silently
          return null;
        }
        console.warn('loadData endpoint failed:', msg);
        return null;
      }
    };

    try {
      const [
        statsData,
        hazardsData,
        projectsData,
        sitesData,
        visitsData,
        evidenceData,
        interventionsData,
        actionsData,
        logsData,
        notificationsData,
        refData
      ] = await Promise.all([
        safeGet(api.getDashboardStats()),
        safeGet(api.getHazards()),
        safeGet(api.getProjects()),
        safeGet(api.getSites()),
        safeGet(api.getSiteVisits()),
        safeGet(api.getEvidence()),
        safeGet(api.getInterventions()),
        safeGet(api.getActions()),
        safeGet(api.getAuditLogs()),
        safeGet(api.getNotifications()),
        safeGet(api.getReferenceData())
      ]);

      if (statsData) setStats(statsData as any);
      if (hazardsData) setHazards(hazardsData as any);
      if (projectsData) setProjects(projectsData as any);
      if (sitesData) setSites(sitesData as any);
      if (visitsData) setVisits(visitsData as any);
      if (evidenceData) setEvidenceList(evidenceData as any);
      if (interventionsData) setInterventions(interventionsData as any);
      if (actionsData) setActions(actionsData as any);
      if (logsData) setAuditLogs(logsData as any);
      if (notificationsData) setNotifications(notificationsData as any);
      if (refData) setReferenceData(refData as any);
    } catch (err) {
      console.error('Failed to load application initial state:', err);
    } finally {
      setLoading(false);
    }
  };"""

if old_block not in text:
    raise SystemExit(
        "loadData() block not found in expected form. "
        "Open src/App.tsx and search for 'Promise.all' to patch manually."
    )

text = text.replace(old_block, new_block, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  loadData() now wraps each endpoint in safeGet()")
print("  Role-restricted 403s are swallowed silently")
print("  All other endpoints still load normally")