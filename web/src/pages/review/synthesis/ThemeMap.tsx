import type { ThemeRow } from "../../../types";

type Node = { key: string; label: string; level: number; x: number; y: number; kind: "higher" | "theme" | "code" };

const WIDTH = 860;
const BOX_W = 150;
const BOX_H = 34;
const ROW_GAP = 90;
const COLORS = { higher: "#2c3e50", theme: "#2f80ed", code: "#6c757d" };

function truncate(text: string, size = 22) {
  return text.length > size ? `${text.slice(0, size - 1)}…` : text;
}

/** Layered thematic map: higher-order themes → themes → codes, with connecting lines. */
export default function ThemeMap({ themes }: { themes: ThemeRow[] }) {
  const parents = new Set(themes.map((theme) => theme.parent_id).filter((id): id is number => id !== null));
  const higher = themes.filter((theme) => parents.has(theme.id) && theme.parent_id === null);
  const base = themes.filter((theme) => !parents.has(theme.id));
  const codeIds = new Map<number, string>();
  base.forEach((theme) => theme.codes.forEach((code) => codeIds.set(code.id, code.name)));

  const rows: Node[][] = [
    higher.map((theme) => ({ key: `t${theme.id}`, label: theme.name, level: 0, x: 0, y: 0, kind: "higher" as const })),
    base.map((theme) => ({ key: `t${theme.id}`, label: theme.name, level: 1, x: 0, y: 0, kind: "theme" as const })),
    [...codeIds].map(([id, name]) => ({ key: `c${id}`, label: name, level: 2, x: 0, y: 0, kind: "code" as const })),
  ].filter((row) => row.length > 0);
  if (rows.length === 0) return null;

  const width = Math.max(WIDTH, ...rows.map((row) => row.length * (BOX_W + 16) + 16));
  const nodes = new Map<string, Node>();
  rows.forEach((row, rowIndex) => {
    const gap = width / row.length;
    row.forEach((node, index) => {
      node.x = gap * index + gap / 2;
      node.y = 24 + rowIndex * ROW_GAP;
      nodes.set(node.key, node);
    });
  });

  const edges: [Node, Node][] = [];
  for (const theme of themes) {
    const node = nodes.get(`t${theme.id}`);
    if (!node) continue;
    if (theme.parent_id !== null && nodes.get(`t${theme.parent_id}`)) edges.push([nodes.get(`t${theme.parent_id}`)!, node]);
    if (!parents.has(theme.id)) theme.codes.forEach((code) => { const target = nodes.get(`c${code.id}`); if (target) edges.push([node, target]); });
  }
  const height = 24 + rows.length * ROW_GAP;

  return (
    <div className="overflow-auto">
      <svg width={width} height={height} role="img" aria-label="Mapa temático">
        {edges.map(([from, to]) => (
          <line key={`${from.key}-${to.key}`} x1={from.x} y1={from.y + BOX_H} x2={to.x} y2={to.y} stroke="#adb5bd" />
        ))}
        {[...nodes.values()].map((node) => (
          <g key={node.key}>
            <rect x={node.x - BOX_W / 2} y={node.y} width={BOX_W} height={BOX_H} rx={6}
              fill={node.kind === "code" ? "#fff" : COLORS[node.kind]} stroke={COLORS[node.kind]} />
            <text x={node.x} y={node.y + BOX_H / 2 + 4} textAnchor="middle" fontSize={12}
              fill={node.kind === "code" ? "#212529" : "#fff"}>
              <title>{node.label}</title>
              {truncate(node.label)}
            </text>
          </g>
        ))}
      </svg>
      <div className="small text-muted mt-1">
        <span className="badge" style={{ background: COLORS.higher }}>tema de ordem superior</span>{" "}
        <span className="badge" style={{ background: COLORS.theme }}>tema</span>{" "}
        <span className="badge border text-dark">código</span>
      </div>
    </div>
  );
}
