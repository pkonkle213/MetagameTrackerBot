import React, { useEffect, useState } from "react";
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme
} from "@mui/material";
import tabs from "../data/documentTabs.json";

const drawerWidth = 320;

function getInitialTab() {
  const requestedSlug = new URLSearchParams(window.location.search).get("section");
  return tabs.find((tab) => tab.slug === requestedSlug) || tabs[0];
}

export default function GuideIndex() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up("md"));
  const [selectedTab, setSelectedTab] = useState(getInitialTab);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    const syncSelectedTab = () => {
      const requestedSlug = new URLSearchParams(window.location.search).get("section");
      setSelectedTab(tabs.find((tab) => tab.slug === requestedSlug) || tabs[0]);
    };
    window.addEventListener("popstate", syncSelectedTab);
    return () => window.removeEventListener("popstate", syncSelectedTab);
  }, []);

  const selectTab = (tab) => {
    setSelectedTab(tab);
    setMobileNavOpen(false);
    const url = new URL(window.location.href);
    url.searchParams.set("section", tab.slug);
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  const guideList = (
    <Box component="nav" aria-label="Guide pages" sx={{ height: "100%", overflowY: "auto", py: 1.5 }}>
      <List disablePadding>
        {tabs.map((tab) => (
          <ListItemButton
            key={tab.slug}
            selected={selectedTab.slug === tab.slug}
            onClick={() => selectTab(tab)}
            aria-current={selectedTab.slug === tab.slug ? "page" : undefined}
            sx={{
              mx: 1.25,
              my: 0.35,
              px: 1.75,
              py: 1.15,
              borderRadius: 1.5,
              alignItems: "flex-start",
              "&.Mui-selected": {
                bgcolor: "rgba(49,91,72,.11)",
                color: "primary.dark",
                "&:hover": { bgcolor: "rgba(49,91,72,.16)" }
              }
            }}
          >
            <ListItemText
              primary={tab.title}
              primaryTypographyProps={{ fontSize: "0.91rem", fontWeight: selectedTab.slug === tab.slug ? 700 : 500, lineHeight: 1.45 }}
            />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ height: "100dvh", display: "flex", flexDirection: "column", bgcolor: "background.default", overflow: "hidden" }}>
      <AppBar position="static" elevation={0} sx={{ bgcolor: "primary.dark", color: "primary.contrastText" }}>
        <Toolbar sx={{ minHeight: { xs: 64, sm: 72 }, gap: 1.5, px: { xs: 1.5, sm: 3 } }}>
          {!isDesktop && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Open guide pages"
              sx={{ flexShrink: 0, width: 42, height: 42 }}
            >
              <Box component="span" aria-hidden="true" sx={{ fontSize: 25, lineHeight: 1 }}>☰</Box>
            </IconButton>
          )}
          <Typography component="h1" variant="h6" sx={{ fontWeight: 800, letterSpacing: "-.025em", lineHeight: 1.2, fontSize: { xs: "1rem", sm: "1.25rem" } }}>
            Metagame Tracker - Tracking your meta so you don't have to
          </Typography>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: "flex", flex: 1, minHeight: 0 }}>
        {isDesktop ? (
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              "& .MuiDrawer-paper": {
                position: "relative",
                width: drawerWidth,
                boxSizing: "border-box",
                borderRight: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper"
              }
            }}
          >
            {guideList}
          </Drawer>
        ) : (
          <Drawer
            variant="temporary"
            open={mobileNavOpen}
            onClose={() => setMobileNavOpen(false)}
            ModalProps={{ keepMounted: true }}
            sx={{
              "& .MuiDrawer-paper": {
                width: Math.min(drawerWidth, "86vw"),
                boxSizing: "border-box",
                bgcolor: "background.paper"
              }
            }}
          >
            {guideList}
          </Drawer>
        )}

        <Box component="main" sx={{ flex: 1, minWidth: 0, minHeight: 0, display: "flex", flexDirection: "column", p: { xs: 1.5, sm: 2.5, md: 3 } }}>
          <Typography component="h2" variant="h5" sx={{ mb: 2, fontWeight: 750, letterSpacing: "-.035em", lineHeight: 1.3 }}>
            {selectedTab.title}
          </Typography>
          <Box
            sx={{
              flex: 1,
              minHeight: 0,
              overflow: "hidden",
              border: "1px solid",
              borderColor: "divider",
              borderRadius: 2,
              bgcolor: "#fff",
              boxShadow: "0 8px 28px rgba(30, 40, 34, .06)"
            }}
          >
            <Box
              key={selectedTab.slug}
              component="iframe"
              title={`Guide page: ${selectedTab.title}`}
              src={`/guides/${selectedTab.slug}.html`}
              loading="eager"
              sx={{ display: "block", width: "100%", height: "100%", border: 0, bgcolor: "#fff" }}
            />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
