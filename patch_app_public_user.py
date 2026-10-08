import pathlib

p = pathlib.Path("src/App.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- 1. handleLogin: redirect PUBLIC_USER to /public/report ---
old_hl = """  const handleLogin = async (u: any) => {
    setCurrentUser(u);
    setCurrentRole(u.role as UserRole);
    setAuthenticated(true);
    setLoading(true);
    // Reset any public route when logging in
    if (window.location.pathname.startsWith('/public/')) {
      window.history.pushState({}, '', '/');
      setPublicRoute('/');
    }
    await loadData();
  };"""

new_hl = """  const handleLogin = async (u: any) => {
    setCurrentUser(u);
    setCurrentRole(u.role as UserRole);
    setAuthenticated(true);

    // PUBLIC_USER → send straight to the public report page
    if (u.role === 'PUBLIC_USER') {
      window.history.pushState({}, '', '/public/report');
      setPublicRoute('/public/report');
      setLoading(false);
      return;
    }

    setLoading(true);
    // Reset any public route when logging in
    if (window.location.pathname.startsWith('/public/')) {
      window.history.pushState({}, '', '/');
      setPublicRoute('/');
    }
    await loadData();
  };

  const handlePublicSignOut = async () => {
    try { await api.logout(); } catch {}
    setAuthenticated(false);
    setCurrentUser(null);
    setCurrentRole('SUPER_ADMIN');
    window.history.pushState({}, '', '/');
    setPublicRoute('/');
  };"""

if old_hl in src:
    src = src.replace(old_hl, new_hl)
    changes.append("handleLogin: PUBLIC_USER redirect + handlePublicSignOut added")
elif "handlePublicSignOut" in src:
    changes.append("handleLogin already patched")
else:
    changes.append("handleLogin pattern NOT FOUND — manual edit needed")

# --- 2. PublicReportPage render — pass currentUser/onSignOut ---
old_rp = """  if (publicRoute.startsWith('/public/report')) {
    return (
      <PublicReportPage
        onBack={() => {
          window.history.pushState({}, '', '/');
          setPublicRoute('/');
        }}
      />
    );
  }"""

new_rp = """  if (publicRoute.startsWith('/public/report')) {
    return (
      <PublicReportPage
        currentUser={currentUser}
        onSignOut={handlePublicSignOut}
        onBack={() => {
          window.history.pushState({}, '', '/');
          setPublicRoute('/');
        }}
      />
    );
  }"""

if old_rp in src:
    src = src.replace(old_rp, new_rp)
    changes.append("PublicReportPage: banner props wired")
elif "currentUser={currentUser}" in src and "<PublicReportPage" in src:
    changes.append("PublicReportPage already wired")
else:
    changes.append("PublicReportPage block NOT FOUND")

# --- 3. PublicTrackPage render — pass currentUser/onSignOut ---
old_tp = """    return (
      <PublicTrackPage
        initialCode={code}
        onBack={() => {
          window.history.pushState({}, '', '/');
          setPublicRoute('/');
        }}
      />
    );"""

new_tp = """    return (
      <PublicTrackPage
        initialCode={code}
        currentUser={currentUser}
        onSignOut={handlePublicSignOut}
        onBack={() => {
          window.history.pushState({}, '', '/');
          setPublicRoute('/');
        }}
      />
    );"""

if old_tp in src:
    src = src.replace(old_tp, new_tp)
    changes.append("PublicTrackPage: banner props wired")
elif "initialCode={code}" in src and "currentUser={currentUser}" in src:
    changes.append("PublicTrackPage already wired")
else:
    changes.append("PublicTrackPage block NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# syntax check
import ast
try:
    # TSX won't parse as Python, so skip — just confirm write succeeded
    print("\nWrote src/App.tsx — let Vite/TSX compile check it.")
except Exception as e:
    print("Write failed:", e)