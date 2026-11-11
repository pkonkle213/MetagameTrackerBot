import React, { useEffect } from "react";
import { Box, Container } from "@mui/material";
import Home from "./pages/Home.jsx";
import LegalPage from "./pages/LegalPage.jsx";
import GuideReader from "./pages/GuideReader.jsx";
import documentTabs from "./data/documentTabs.json";

const metadata = {
  "/": {
    title: "Metagame Tracker Bot — Game community information, in Discord",
    description: "Metagame Tracker Bot helps game stores, event organizers, hubs, and players manage community event information in Discord."
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
  const guideMatch = path.match(/^\/guide\/([^/]+)$/);
  const guide = guideMatch ? documentTabs.find((tab) => tab.slug === guideMatch[1]) : null;
  const pageMeta = guide
    ? {
        title: `${guide.title} — Metagame Tracker Bot Guide`,
        description: `Section ${documentTabs.indexOf(guide) + 1} of the Metagame Tracker Bot standard operating procedure: ${guide.title}.`
      }
    : metadata[path] || metadata["/"];
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
      ) : guide ? (
        <GuideReader key={guide.slug} tab={guide} />
      ) : path.startsWith("/guide/") ? (
        <Container maxWidth="md" sx={{ py: 10 }}>
          <Box component="main" sx={{ textAlign: "center" }}>
            <Box sx={{ color: "secondary.main", fontFamily: "monospace", fontWeight: 800, letterSpacing: ".12em" }}>GUIDE SECTION NOT FOUND</Box>
            <Box component="h1" sx={{ mt: 1, fontSize: { xs: "2rem", sm: "3rem" }, letterSpacing: "-.05em" }}>That page isn’t in the guide.</Box>
            <Box component="p" sx={{ color: "text.secondary" }}>Choose a section from the full index to continue.</Box>
            <a href={`/guide/${documentTabs[0].slug}`}>Open the guide</a>
          </Box>
        </Container>
      ) : <Home />}
    </Box>
  );
}
