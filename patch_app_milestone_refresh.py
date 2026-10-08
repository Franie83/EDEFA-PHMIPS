import pathlib

p = pathlib.Path("src/App.tsx")
src = p.read_text(encoding="utf-8")

old = """      <ProjectDetailModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
        onLogVisitClick={p => {
          setVisitDefaultProject(p);
          setIsVisitModalOpen(true);
        }}
        onNavigateToMap={navigateToMapCoordinate}"""

new = """      <ProjectDetailModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
        onLogVisitClick={p => {
          setVisitDefaultProject(p);
          setIsVisitModalOpen(true);
        }}
        onNavigateToMap={navigateToMapCoordinate}
        onRefresh={loadData}"""

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Added onRefresh to ProjectDetailModal in App.tsx")
else:
    print("Pattern not found — paste the current ProjectDetailModal block from App.tsx")