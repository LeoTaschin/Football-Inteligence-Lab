import { useRef, type KeyboardEvent } from "react";

import styles from "./Tabs.module.css";

export interface TabItem<K extends string> {
  key: K;
  label: string;
}

interface TabsProps<K extends string> {
  items: TabItem<K>[];
  current: K;
  onChange: (key: K) => void;
  label: string;
  idPrefix: string;
}

/** WAI-ARIA tabs: arrow keys move between tabs, Home/End jump to the ends. */
export function Tabs<K extends string>({ items, current, onChange, label, idPrefix }: TabsProps<K>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);

  const onKey = (index: number) => (event: KeyboardEvent) => {
    const last = items.length - 1;
    const target =
      event.key === "ArrowRight" ? (index === last ? 0 : index + 1)
      : event.key === "ArrowLeft" ? (index === 0 ? last : index - 1)
      : event.key === "Home" ? 0
      : event.key === "End" ? last
      : null;
    if (target === null) return;
    event.preventDefault();
    onChange(items[target].key);
    refs.current[target]?.focus();
  };

  return (
    <div className={styles.tabs} role="tablist" aria-label={label}>
      {items.map((item, i) => {
        const selected = item.key === current;
        return (
          <button
            key={item.key}
            ref={(el) => (refs.current[i] = el)}
            type="button"
            role="tab"
            id={`${idPrefix}-tab-${item.key}`}
            aria-selected={selected}
            aria-controls={`${idPrefix}-panel-${item.key}`}
            tabIndex={selected ? 0 : -1}
            className={styles.tab}
            onClick={() => onChange(item.key)}
            onKeyDown={onKey(i)}
          >
            {item.label}
          </button>
        );
      })}
    </div>
  );
}

export function TabPanel({ idPrefix, tab, children }: { idPrefix: string; tab: string; children: React.ReactNode }) {
  return (
    <div role="tabpanel" id={`${idPrefix}-panel-${tab}`} aria-labelledby={`${idPrefix}-tab-${tab}`} className={styles.panel}>
      {children}
    </div>
  );
}
