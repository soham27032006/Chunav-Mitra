import { Header } from "./Header";
import { Footer } from "./Footer";
import { Petals } from "./Petals";
import { CursorGlow } from "./CursorGlow";

export function Layout({
  children,
  hideFooter = false,
}: {
  children: React.ReactNode;
  hideFooter?: boolean;
}) {
  return (
    <div className="relative min-h-screen rangoli-bg">
      <Petals count={14} />
      <CursorGlow />
      <Header />
      <main className="relative z-10">{children}</main>
      {!hideFooter && <Footer />}
    </div>
  );
}
