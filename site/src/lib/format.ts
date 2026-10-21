// pt-BR display formatting. Only formatting: no football rules are computed here.

const integer = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });

/** 2490 -> "2.490" */
export function formatInt(n: number): string {
  return integer.format(n);
}

/** 14.75 -> "14,75" (always `digits` decimals) */
export function formatDecimal(n: number, digits = 2): string {
  return new Intl.NumberFormat("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(n);
}

/** part / whole as a rounded percentage: (400, 471) -> "85%" */
export function formatPercent(part: number, whole: number): string {
  return whole ? `${Math.round((100 * part) / whole)}%` : "–";
}

const MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

/** "1970-06-21" -> "21 jun 1970" (no Date object: avoids timezone shifts) */
export function formatDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

/** 74 -> "74′" */
export function formatMinute(minute: number): string {
  return `${minute}′`;
}

/** 7.4 -> "0:07" */
export function formatClock(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
