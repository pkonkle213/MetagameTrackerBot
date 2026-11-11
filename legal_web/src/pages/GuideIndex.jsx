import React from "react";
import { Box, Container, Link, List, ListItem, ListItemText, Typography } from "@mui/material";
import tabs from "../data/documentTabs.json";

export default function GuideIndex() {
  return (
    <Container maxWidth="md" sx={{ py: { xs: 4, sm: 7 } }}>
      <Box component="header" sx={{ mb: 4 }}>
        <Link href="/" underline="none" color="primary.main" sx={{ fontWeight: 800 }}>
          Metagame Tracker Bot
        </Link>
        <Typography component="h1" sx={{ mt: 3, fontSize: { xs: "2.2rem", sm: "3rem" }, fontWeight: 800, letterSpacing: "-.05em" }}>
          Standard operating procedures
        </Typography>
        <Typography sx={{ mt: 1.5, color: "text.secondary", lineHeight: 1.7 }}>
          Each section opens as its own page with the original instructions and screenshots.
        </Typography>
      </Box>
      <List disablePadding aria-label="SOP sections">
        {tabs.map((tab, index) => (
          <ListItem
            key={tab.slug}
            component="a"
            href={`/guide/${tab.slug}`}
            sx={{
              px: { xs: 1.5, sm: 2 },
              py: 1.25,
              mb: 1,
              border: "1px solid",
              borderColor: "divider",
              borderRadius: 2,
              color: "text.primary",
              textDecoration: "none",
              bgcolor: "background.paper",
              "&:hover": { borderColor: "primary.main", bgcolor: "rgba(49,91,72,.04)" }
            }}
          >
            <Typography aria-hidden="true" sx={{ minWidth: 44, color: "primary.main", fontFamily: "monospace", fontWeight: 800 }}>
              {String(index + 1).padStart(2, "0")}
            </Typography>
            <ListItemText primary={tab.title} primaryTypographyProps={{ fontWeight: 700, lineHeight: 1.45 }} />
          </ListItem>
        ))}
      </List>
    </Container>
  );
}
