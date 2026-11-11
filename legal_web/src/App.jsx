import React, { useEffect } from "react";
import { Box, Container } from "@mui/material";
import Home from "./pages/Home.jsx";
import LegalPage from "./pages/LegalPage.jsx";
import GuideIndex from "./pages/GuideIndex.jsx";

const metadata = {
  "/": {
    title: "Metagame Tracker Bot — Game community information, in Discord",
    description: "Metagame Tracker Bot helps game stores, event organizers, hubs, and players manage community event information in Discord."
  },
  "/guide": {
    title: "Metagame Tracker — Guide",
    description: "Browse the Metagame Tracker guide pages."
  },
  "/privacy": {
    title: "Privacy Policy — MetaGameTracker Bot",
    description: "Privacy Policy for MetaGameTracker Bot."
  },
  "/terms": {
    title: "Terms of Service — MetaGameTracker Bot",
    description: "Terms of Service for MetaGameTracker Bot."
  }
};

export default function App() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  const pageMeta = metadata[path] || metadata["/"];
  useEffect(() => {
    document.title = pageMeta.title;
    let description = document.querySelector('meta[name="description"]');
    if (!description) {
      description = document.createElement("meta");
      description.name = "description";
      document.head.appendChild(description);
    }
    description.content = pageMeta.description;
  }, [pageMeta]);

  return (
    <Box className={path === "/" ? "home-grain" : ""} sx={{ minHeight: "100dvh" }}>
      {path === "/privacy" || path === "/terms" ? (
        <Container maxWidth="md" disableGutters sx={{ px: { xs: 2.5, sm: 3 }, py: { xs: 2.5, sm: 4 } }}>
          <LegalPage type={path.slice(1)} />
        </Container>
      ) : path === "/guide" ? <GuideIndex /> : <Home />}
    </Box>
  );
}
