import * as React from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";
import { Petals } from "./Petals";
import { CursorGlow } from "./CursorGlow";

export function Layout({
  children,
  hideFooter = false,
  disableAmbientEffects = false,
}: {
  children: React.ReactNode;
  hideFooter?: boolean;
  disableAmbientEffects?: boolean;
}) {
  return (
    <div className="relative min-h-screen rangoli-bg">
      {!disableAmbientEffects && <Petals count={14} />}
      {!disableAmbientEffects && <CursorGlow />}
      <Header />
      <main id="main-content" role="main" tabIndex={-1} className="relative z-10">
        {children}
      </main>
      {!hideFooter && <Footer />}
    </div>
  );
}
