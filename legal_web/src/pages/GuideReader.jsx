import React, { useMemo, useState } from "react";
import {
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  InputAdornment,
  Link,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  TextField,
  Typography
} from "@mui/material";
import tabs from "../data/documentTabs.json";

function GuideSidebar({ tab, onSelect }) {
  const [query, setQuery] = useState("");
  const filteredTabs = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return normalized ? tabs.filter((item) => item.title.toLocaleLowerCase().includes(normalized)) : tabs;
  }, [query]);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Box sx={{ px: 2.25, pt: 2.5, pb: 1.7 }}>
        <Typography sx={{ color: "primary.main", fontSize: ".68rem", fontWeight: 800, letterSpacing: ".14em", textTransform: "uppercase" }}>
          Field guide
        </Typography>
        <Typography component="h2" sx={{ mt: 0.65, fontSize: "1.2rem", fontWeight: 800, letterSpacing: "-.035em" }}>
          Contents
        </Typography>
        <TextField
          fullWidth
          size="small"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Find a section"
          inputProps={{ "aria-label": "Filter guide sections" }}
          sx={{
            mt: 1.8,
            "& .MuiOutlinedInput-root": { bgcolor: "background.paper", borderRadius: 2, fontSize: ".82rem" }
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Typography aria-hidden="true" sx={{ fontSize: ".95rem", color: "text.secondary" }}>⌕</Typography>
              </InputAdornment>
            )
          }}
        />
      </Box>
      <Box component="nav" aria-label="Guide table of contents" sx={{ flex: 1, overflowY: "auto", pb: 2 }}>
        {filteredTabs.length ? (
          <List disablePadding>
            {filteredTabs.map((item) => {
              const index = tabs.findIndex((entry) => entry.tabId === item.tabId);
              const selected = item.slug === tab.slug;
              return (
                <ListItemButton
                  key={item.tabId}
                  component="a"
                  href={`/guide/${item.slug}`}
                  selected={selected}
                  aria-current={selected ? "page" : undefined}
                  onClick={onSelect}
                  sx={{
                    px: 2,
                    py: 1.05,
                    borderLeft: "3px solid",
                    borderColor: selected ? "primary.main" : "transparent",
                    alignItems: "flex-start",
                    "&.Mui-selected": { bgcolor: "rgba(49,91,72,.09)" },
                    "&.Mui-selected:hover": { bgcolor: "rgba(49,91,72,.13)" },
                    "&:hover": { bgcolor: "rgba(49,91,72,.055)" }
                  }}
                >
                  <Typography aria-hidden="true" sx={{ minWidth: 34, pt: 0.15, color: selected ? "primary.main" : "text.secondary", fontFamily: "monospace", fontSize: ".7rem", fontWeight: 700 }}>
                    {String(index + 1).padStart(2, "0")}
                  </Typography>
                  <ListItemText
                    primary={item.title}
                    primaryTypographyProps={{ fontSize: ".84rem", lineHeight: 1.4, fontWeight: selected ? 750 : 550, color: selected ? "primary.dark" : "text.primary" }}
                  />
                </ListItemButton>
              );
            })}
          </List>
        ) : (
          <Box role="status" sx={{ px: 2.5, py: 3 }}>
            <Typography variant="body2" color="text.secondary">No sections match “{query}”.</Typography>
            <Button size="small" onClick={() => setQuery("")} sx={{ mt: 1, px: 0 }}>Clear search</Button>
          </Box>
        )}
      </Box>
      <Divider />
      <Box sx={{ px: 2.25, py: 1.8 }}>
        <Typography variant="caption" color="text.secondary">{tabs.length} sections · Metagame Tracker Bot SOP</Typography>
      </Box>
    </Box>
  );
}

function resizeGuideFrame(event) {
  const frame = event.currentTarget;
  const document = frame.contentDocument;
  if (!document) return;
  const contentHeight = Math.max(
    document.body?.scrollHeight || 0,
    document.documentElement?.scrollHeight || 0
  );
  if (contentHeight > 0) frame.style.height = `${contentHeight}px`;
}

export default function GuideReader({ tab }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const index = tabs.findIndex((item) => item.slug === tab.slug);
  const previous = tabs[index - 1];
  const next = tabs[index + 1];

  return (
    <Box className="guide-shell" sx={{ minHeight: "100dvh", color: "text.primary" }}>
      <Box component="header" sx={{ position: "sticky", top: 0, zIndex: 5, bgcolor: "background.default", borderBottom: "1px solid", borderColor: "divider" }}>
        <Box sx={{ minHeight: 70, px: { xs: 1.5, sm: 3 }, display: "flex", alignItems: "center", gap: 1.5 }}>
          <IconButton
            aria-label="Open guide contents"
            aria-expanded={mobileOpen}
            aria-controls="guide-mobile-navigation"
            onClick={() => setMobileOpen(true)}
            sx={{ display: { md: "none" }, border: "1px solid", borderColor: "divider", borderRadius: 2, width: 42, height: 42 }}
          >
            <Box aria-hidden="true" sx={{ display: "grid", gap: ".22rem" }}>
              {[0, 1, 2].map((line) => <Box key={line} sx={{ width: 17, height: 2, bgcolor: "text.primary", borderRadius: 2 }} />)}
            </Box>
          </IconButton>
          <Link href="/" underline="none" color="inherit" sx={{ display: "inline-flex", alignItems: "center", gap: 1.1, minWidth: 0 }}>
            <Box aria-hidden="true" sx={{ width: 34, height: 34, flex: "0 0 auto", display: "grid", placeItems: "center", bgcolor: "primary.main", color: "#f3f0e7", borderRadius: "10px 10px 10px 3px", fontFamily: '"Manrope", sans-serif', fontWeight: 800, fontSize: 18 }}>M</Box>
            <Box sx={{ minWidth: 0 }}>
              <Typography sx={{ fontSize: ".86rem", fontWeight: 800, letterSpacing: "-.035em", lineHeight: 1.15 }}>Metagame Tracker Bot</Typography>
              <Typography sx={{ display: { xs: "none", sm: "block" }, mt: 0.3, color: "text.secondary", fontSize: ".69rem", letterSpacing: ".035em" }}>Operations guide</Typography>
            </Box>
          </Link>
          <Box sx={{ flex: 1 }} />
          <Link href="/" underline="hover" color="text.secondary" sx={{ display: { xs: "none", sm: "inline" }, fontSize: ".82rem", fontWeight: 650 }}>Home</Link>
          <Typography aria-hidden="true" sx={{ color: "divider", display: { xs: "none", sm: "block" } }}>/</Typography>
          <Typography noWrap sx={{ maxWidth: { xs: 125, sm: 250, md: 340 }, fontSize: ".82rem", fontWeight: 700 }}>{tab.title}</Typography>
        </Box>
      </Box>

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "278px minmax(0, 1fr)" }, maxWidth: 1600, mx: "auto", minHeight: "calc(100dvh - 70px)" }}>
        <Paper
          component="aside"
          elevation={0}
          square
          sx={{
            display: { xs: "none", md: "block" },
            position: "sticky",
            top: 70,
            height: "calc(100dvh - 70px)",
            bgcolor: "#eeece3",
            borderRight: "1px solid",
            borderColor: "divider"
          }}
        >
          <GuideSidebar tab={tab} />
        </Paper>

        <Box component="main" id="main-content" sx={{ minWidth: 0, px: { xs: 1.5, sm: 3, lg: 5 }, pt: { xs: 3, sm: 4.5 }, pb: 6 }}>
          <Box sx={{ maxWidth: 1040, mx: "auto" }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.1 }}>
              <Typography sx={{ color: "secondary.main", fontFamily: "monospace", fontSize: ".75rem", fontWeight: 800 }}>
                {String(index + 1).padStart(2, "0")} / {String(tabs.length).padStart(2, "0")}
              </Typography>
              <Divider flexItem orientation="vertical" sx={{ mx: 0.3, borderColor: "divider" }} />
              <Typography sx={{ color: "text.secondary", fontSize: ".76rem", fontWeight: 600 }}>Standard operating procedure</Typography>
            </Stack>
            <Typography component="h1" sx={{ maxWidth: 850, fontSize: { xs: "1.85rem", sm: "2.6rem", lg: "3.1rem" }, lineHeight: 1.08, letterSpacing: "-.055em", overflowWrap: "anywhere" }}>
              {tab.title}
            </Typography>
            <Typography sx={{ mt: 1.2, mb: 2.7, color: "text.secondary", fontSize: ".9rem", lineHeight: 1.7 }}>
              Practical instructions for game stores, event organizers, hubs, and players.
            </Typography>

            <Paper elevation={0} className="guide-document-frame" sx={{ overflow: "hidden", border: "1px solid", borderColor: "divider", borderRadius: { xs: 2, sm: 3 }, bgcolor: "background.paper" }}>
              <iframe
                key={tab.tabId}
                title={`${tab.title} — original exported guide`}
                src={tab.htmlPath}
                loading="eager"
                className="guide-original"
                referrerPolicy="same-origin"
                onLoad={resizeGuideFrame}
              />
            </Paper>

            <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1.5} sx={{ mt: 2.5 }}>
              {previous ? (
                <Button component="a" href={`/guide/${previous.slug}`} variant="outlined" color="inherit" sx={{ justifyContent: "flex-start", textAlign: "left", borderColor: "divider", borderRadius: 2, px: 2, py: 1.3, maxWidth: { sm: "48%" } }}>
                  <Box><Typography variant="caption" color="text.secondary">Previous section</Typography><Typography sx={{ fontSize: ".88rem", fontWeight: 700 }}>← {previous.title}</Typography></Box>
                </Button>
              ) : <Box />}
              {next ? (
                <Button component="a" href={`/guide/${next.slug}`} variant="contained" sx={{ justifyContent: "flex-end", textAlign: "right", borderRadius: 2, px: 2, py: 1.3, maxWidth: { sm: "48%" } }}>
                  <Box><Typography variant="caption" sx={{ color: "rgba(248,246,238,.72)" }}>Next section</Typography><Typography sx={{ fontSize: ".88rem", fontWeight: 700 }}>{next.title} →</Typography></Box>
                </Button>
              ) : <Button component="a" href="/" variant="outlined" color="inherit" sx={{ borderColor: "divider", borderRadius: 2 }}>Return home</Button>}
            </Stack>
            <Box component="footer" sx={{ mt: 5, pt: 2, borderTop: "1px solid", borderColor: "divider", display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 1 }}>
              <Typography variant="caption" color="text.secondary">Metagame Tracker Bot · SOP reader</Typography>
              <Stack direction="row" spacing={2}>
                <Link href="/privacy" color="text.secondary" variant="caption">Privacy</Link>
                <Link href="/terms" color="text.secondary" variant="caption">Terms</Link>
              </Stack>
            </Box>
          </Box>
        </Box>
      </Box>

      <Drawer
        id="guide-mobile-navigation"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{ sx: { width: "min(88vw, 360px)", bgcolor: "#eeece3" } }}
      >
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", px: 2.25, py: 1.5, borderBottom: "1px solid", borderColor: "divider" }}>
          <Typography sx={{ fontWeight: 800 }}>Guide contents</Typography>
          <Button onClick={() => setMobileOpen(false)} aria-label="Close guide contents" size="small">Close</Button>
        </Box>
        <GuideSidebar tab={tab} onSelect={() => setMobileOpen(false)} />
      </Drawer>
    </Box>
  );
}
