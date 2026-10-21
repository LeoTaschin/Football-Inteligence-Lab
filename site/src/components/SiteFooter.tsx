import { site } from "../content/pt";
import styles from "./SiteFooter.module.css";

export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        <span>{site.footerLeft}</span>
        <span>{site.footerRight}</span>
      </div>
    </footer>
  );
}
