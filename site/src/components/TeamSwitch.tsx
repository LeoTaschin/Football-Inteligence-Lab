import type { TeamData } from "../types/data";
import styles from "./TeamSwitch.module.css";

interface TeamSwitchProps {
  teams: TeamData[];
  current: number;
  onChange: (index: number) => void;
  label: string;
}

/** One team at a time: the pills that switch between the two teams of the match. */
export function TeamSwitch({ teams, current, onChange, label }: TeamSwitchProps) {
  return (
    <div className={styles.switch} role="group" aria-label={label}>
      {teams.map((t, i) => (
        <button key={t.teamId} type="button" className={`pill ${styles.pill}`} aria-pressed={i === current} onClick={() => onChange(i)}>
          <span className={styles.dot} style={{ background: t.colors.fill, borderColor: t.colors.line }} />
          {t.displayName}
        </button>
      ))}
    </div>
  );
}
