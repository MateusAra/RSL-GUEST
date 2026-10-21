import type { PrismaFlow } from "../../../types";

const W = 760;
const BOX_W = 330;
const STAGES = ["Identificação", "Triagem", "Elegibilidade", "Inclusão"];

function Box({ x, y, h, lines, strong }: { x: number; y: number; h: number; lines: string[]; strong?: boolean }) {
  return (
    <g>
      <rect x={x} y={y} width={BOX_W} height={h} rx={6} fill={strong ? "#e8f1fd" : "#fff"} stroke="#2c3e50" />
      {lines.map((line, index) => (
        <text key={index} x={x + 10} y={y + 20 + index * 16} fontSize={12} fontWeight={index === 0 ? 600 : 400}>{line}</text>
      ))}
    </g>
  );
}

/** PRISMA 2020 flow diagram computed by the system. */
export default function PrismaFlowDiagram({ flow }: { flow: PrismaFlow }) {
  const left = 120;
  const right = left + BOX_W + 40;
  const sources = flow.per_source.map((item) => `${item.source}: ${item.count}`);
  const criteria = flow.excluded_by_criteria.slice(0, 4).map((item) => `${item.criteria}: ${item.count}`);
  const idH = 34 + sources.length * 16;
  const exH = 52 + criteria.length * 16;
  const rows = [12, 12 + Math.max(idH, 50) + 40, 0, 0];
  rows[2] = rows[1] + Math.max(50, exH) + 40;
  rows[3] = rows[2] + 90;
  const height = rows[3] + 70;

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${height}`} role="img" aria-label="Fluxograma PRISMA 2020">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#2c3e50" /></marker>
      </defs>
      {STAGES.map((stage, index) => (
        <g key={stage}>
          <rect x={4} y={rows[index]} width={100} height={50} rx={6} fill="#2c3e50" />
          <text x={54} y={rows[index] + 30} textAnchor="middle" fontSize={12} fill="#fff">{stage}</text>
        </g>
      ))}
      <Box x={left} y={rows[0]} h={Math.max(idH, 50)} lines={[`Registros identificados (n = ${flow.identified})`, ...sources]} />
      <Box x={right} y={rows[0]} h={50} lines={[`Duplicados removidos (n = ${flow.duplicates_removed})`]} />
      <Box x={left} y={rows[1]} h={50} lines={[`Registros triados (n = ${flow.screened})`]} />
      <Box x={right} y={rows[1]} h={Math.max(50, exH)}
        lines={[`Excluídos na seleção (n = ${flow.excluded_screening})`, ...criteria, `Aguardando classificação (n = ${flow.awaiting_screening})`]} />
      <Box x={left} y={rows[2]} h={50} lines={[`Avaliados na qualidade (n = ${flow.assessed_quality})`]} />
      <Box x={right} y={rows[2]} h={50} lines={[`Excluídos pela nota de corte (n = ${flow.excluded_quality})`]} />
      <Box x={left} y={rows[3]} h={50} strong lines={[`Estudos incluídos (n = ${flow.included})`]} />
      {[0, 1, 2].map((index) => (
        <g key={index}>
          <line x1={left + BOX_W / 2} y1={rows[index] + (index === 0 ? Math.max(idH, 50) : 50)} x2={left + BOX_W / 2} y2={rows[index + 1]}
            stroke="#2c3e50" markerEnd="url(#arrow)" />
          <line x1={left + BOX_W} y1={rows[index] + 25} x2={right} y2={rows[index] + 25} stroke="#2c3e50" markerEnd="url(#arrow)" />
        </g>
      ))}
      <text x={right} y={height - 10} fontSize={11} fill={flow.consistent ? "#198754" : "#dc3545"}>
        {flow.consistent ? "As contagens fecham." : "Atenção: as contagens não fecham."}
      </text>
    </svg>
  );
}
