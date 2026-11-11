import React from "react";
import { Box, Button, Container, Divider, Link, Paper, Stack, Typography } from "@mui/material";
import documentTabs from "../data/documentTabs.json";

const capabilities = [
  ["01 / EVENTS", "Event information", "Submit and view event information, player names, and the details your community uses to follow its tournaments."],
  ["02 / RESULTS", "Archetypes and tournament results", "Keep archetypes and tournament results available alongside community event information."],
  ["03 / REPORTS", "Reports and related settings", "Submit and view reports, with related settings supported for the server’s community setup."],
  ["04 / COMMUNITY", "Configured roles, store, and hub profiles", "The bot can manage configured Discord roles. Store and hub profiles and settings are supported."]
];

const audience = [
  ["01", "Game stores", " supporting their community with store profiles and settings."],
  ["02", "Event organizers", " submitting event information, results, and reports."],
  ["03", "Hubs", " managing supported hub profiles and settings."],
  ["04", "Players", " viewing shared names, archetypes, event information, and results."]
];

const eyebrowSx = { color: "primary.main", fontSize: ".73rem", fontWeight: 800, letterSpacing: ".13em", textTransform: "uppercase" };
const sectionTitleSx = { fontSize: { xs: "2rem", md: "2.8rem" }, lineHeight: 1.08, maxWidth: 620 };
const mail = "mailto:metagametrackerbot@gmail.com";

function Brand() {
  return (
    <Link href="/" underline="none" color="inherit" aria-label="Metagame Tracker Bot home" sx={{ display: "inline-flex", alignItems: "center", gap: 1.4, fontWeight: 800, fontSize: ".95rem", letterSpacing: "-.035em" }}>
      <Box aria-hidden="true" sx={{ width: 36, height: 36, display: "grid", placeItems: "center", bgcolor: "primary.main", color: "#f3f0e7", borderRadius: "11px 11px 11px 3px", fontFamily: '"Manrope", sans-serif', fontWeight: 800, fontSize: 20 }}>M</Box>
      Metagame Tracker Bot
    </Link>
  );
}

function Footer() {
  return (
    <Box component="footer" sx={{ borderTop: "1px solid", borderColor: "divider", py: 3.5, mt: { xs: 7, md: 10 } }}>
      <Container maxWidth="lg" sx={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
        <Typography variant="body2" color="text.secondary">Metagame Tracker Bot · Game community information for Discord</Typography>
        <Stack component="nav" aria-label="Legal and support" direction="row" spacing={{ xs: 1.8, sm: 3 }} flexWrap="wrap">
          <Link href={`/guide/${documentTabs[0].slug}`} color="text.secondary" variant="body2">SOP Guide</Link>
          <Link href="/privacy" color="text.secondary" variant="body2">Privacy Policy</Link>
          <Link href="/terms" color="text.secondary" variant="body2">Terms of Service</Link>
          <Link href={mail} color="text.secondary" variant="body2">Support</Link>
        </Stack>
      </Container>
    </Box>
  );
}

export default function Home() {
  return (
    <>
      <Box component="header" sx={{ borderBottom: "1px solid", borderColor: "divider" }}>
        <Container maxWidth="lg" sx={{ minHeight: 82, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
          <Brand />
          <Stack component="nav" aria-label="Main navigation" direction="row" spacing={{ xs: 1.5, sm: 3.5 }} alignItems="center">
            <Link href="#features" underline="none" color="text.primary" sx={{ fontSize: ".88rem", fontWeight: 700, display: { xs: "none", sm: "inline" } }}>What it does</Link>
            <Link href={`/guide/${documentTabs[0].slug}`} underline="none" color="text.primary" sx={{ fontSize: ".88rem", fontWeight: 700 }}>Guide</Link>
            <Link href="#plans" underline="none" color="text.primary" sx={{ fontSize: ".88rem", fontWeight: 700 }}>Plans</Link>
            <Link href={mail} underline="none" color="primary.dark" sx={{ fontSize: ".88rem", fontWeight: 700 }}>Contact</Link>
          </Stack>
        </Container>
      </Box>

      <Box component="main">
        <Container maxWidth="lg">
          <Box component="section" aria-labelledby="hero-title" sx={{ py: { xs: 7, md: 11 }, display: "grid", gridTemplateColumns: { xs: "1fr", md: "1.03fr .97fr" }, gap: { xs: 5, md: 8 }, alignItems: "center" }}>
            <Box className="enter">
              <Typography sx={eyebrowSx}>For game communities on Discord</Typography>
              <Typography id="hero-title" component="h1" sx={{ mt: 2, fontSize: { xs: "3.25rem", sm: "4.3rem", md: "5rem" }, lineHeight: .99, maxWidth: 650 }}>
                Keep your local scene <Box component="span" sx={{ color: "primary.main", fontStyle: "italic" }}>in the loop.</Box>
              </Typography>
              <Typography sx={{ mt: 2.5, maxWidth: 580, fontSize: { xs: "1.02rem", md: "1.13rem" }, lineHeight: 1.75, color: "text.secondary" }}>
                Metagame Tracker Bot helps stores, event organizers, hubs, and players submit and view the game-community information they need—right in their Discord server.
              </Typography>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={1.7} alignItems={{ xs: "stretch", sm: "center" }} sx={{ mt: 3.5 }}>
                <Button component="a" href={`${mail}?subject=Metagame%20Tracker%20Bot%20support`} variant="contained" color="primary">Ask a question</Button>
                <Button component="a" href="#features" variant="text" color="inherit" sx={{ justifyContent: { xs: "center", sm: "flex-start" } }}>See what the bot supports</Button>
              </Stack>
            </Box>

            <Paper className="enter enter-delay-1" role="img" aria-label="Illustration of event results organized in a community tournament board" elevation={0} sx={{ p: { xs: 2, sm: 3 }, bgcolor: "#e9e4d7", border: "1px solid #d4d0c3", borderRadius: 4, transform: { md: "rotate(1.1deg)" } }}>
              <Stack direction="row" justifyContent="space-between" sx={{ px: .5, pb: 2 }}>
                <Typography variant="overline" sx={{ fontWeight: 800, letterSpacing: ".1em" }}>Community event</Typography>
                <Typography variant="overline" sx={{ color: "primary.main", fontWeight: 800 }}>Results view</Typography>
              </Stack>
              <Paper elevation={0} sx={{ p: { xs: 2, sm: 3 }, bgcolor: "background.paper", borderRadius: 3, border: "1px solid #d4d0c3" }}>
                <Typography sx={{ ...eyebrowSx, fontSize: ".65rem" }}>Example event data</Typography>
                <Typography component="h2" sx={{ mt: .7, mb: 2.4, fontFamily: '"Manrope", sans-serif', fontSize: { xs: "1.45rem", sm: "1.75rem" }, fontWeight: 800, letterSpacing: "-.045em" }}>Event information, together.</Typography>
                <Box sx={{ display: "grid", gridTemplateColumns: "1.1fr 1.2fr .55fr", gap: 1, borderBottom: "1px solid", borderColor: "divider", pb: 1, color: "text.secondary" }}>
                  {["Player", "Archetype", "Record"].map((item) => <Typography key={item} variant="caption" sx={{ fontWeight: 700 }}>{item}</Typography>)}
                </Box>
                {[["Mira K.", "Control", "4–1"], ["Jon R.", "Midrange", "4–1"], ["Alex T.", "Aggro", "3–2"]].map((row) => (
                  <Box key={row[0]} sx={{ display: "grid", gridTemplateColumns: "1.1fr 1.2fr .55fr", gap: 1, py: 1.35, borderBottom: "1px solid #e9e4d7" }}>
                    <Typography variant="body2" fontWeight={700}>{row[0]}</Typography><Typography variant="body2" color="text.secondary">{row[1]}</Typography><Typography variant="body2" fontWeight={700}>{row[2]}</Typography>
                  </Box>
                ))}
                <Stack direction="row" justifyContent="space-between" sx={{ pt: 2 }}>
                  <Typography variant="caption" fontWeight={700}>Tournament report</Typography><Typography variant="caption" color="text.secondary">Available in server</Typography>
                </Stack>
              </Paper>
              <Typography variant="body2" sx={{ mt: 2, px: .5, color: "text.secondary", lineHeight: 1.65 }}>
                <Box component="strong" sx={{ color: "text.primary" }}>Made for local play.</Box> Submit, view, and keep track of the details your community shares.
              </Typography>
            </Paper>
          </Box>

          <Box component="section" aria-label="Supported community information" sx={{ display: "grid", gridTemplateColumns: { xs: "1fr 1fr", md: "repeat(4, 1fr)" }, borderTop: "1px solid", borderBottom: "1px solid", borderColor: "divider", py: 2.6, gap: { xs: 2, md: 1 } }}>
            {["Events and player names", "Archetypes and results", "Reports and settings", "Store and hub profiles"].map((label, index) => (
              <Stack key={label} direction="row" spacing={1.3} alignItems="center">
                <Typography sx={{ fontFamily: "monospace", color: "secondary.main", fontSize: ".78rem", fontWeight: 700 }}>0{index + 1}</Typography>
                <Typography variant="body2" fontWeight={600}>{label}</Typography>
              </Stack>
            ))}
          </Box>

          <Box component="section" id="features" aria-labelledby="features-title" sx={{ py: { xs: 8, md: 11 }, scrollMarginTop: 28 }}>
            <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr .72fr" }, gap: 3, alignItems: "end", mb: 4.5 }}>
              <Box><Typography sx={eyebrowSx}>A practical toolkit</Typography><Typography id="features-title" component="h2" sx={{ ...sectionTitleSx, mt: 1.3 }}>The details that keep a scene connected.</Typography></Box>
              <Typography color="text.secondary" sx={{ lineHeight: 1.75 }}>Use the bot to submit and view the information around your game events and community. Supported details depend on what your server chooses to configure and share.</Typography>
            </Box>
            <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" }, borderTop: "1px solid", borderLeft: { sm: "1px solid" }, borderColor: "divider" }}>
              {capabilities.map(([index, title, copy]) => (
                <Box component="article" key={index} sx={{ p: { xs: 2.5, sm: 3.5 }, minHeight: 195, borderRight: "1px solid", borderBottom: "1px solid", borderColor: "divider" }}>
                  <Typography sx={{ ...eyebrowSx, color: "secondary.main", fontFamily: "monospace", fontSize: ".7rem" }}>{index}</Typography>
                  <Typography component="h3" sx={{ mt: 1.4, fontSize: "1.28rem", fontWeight: 750 }}>{title}</Typography>
                  <Typography color="text.secondary" sx={{ mt: 1, lineHeight: 1.7 }}>{copy}</Typography>
                </Box>
              ))}
            </Box>
            <Paper component="aside" aria-label="Optional service connections" elevation={0} sx={{ mt: 3, p: { xs: 2.5, sm: 3 }, bgcolor: "#e8eddf", border: "1px solid #cbd5c5", borderRadius: 3, display: { sm: "grid" }, gridTemplateColumns: { sm: ".8fr 1.2fr" }, gap: 2 }}>
              <Typography component="h3" sx={{ fontSize: "1.2rem", fontWeight: 750 }}>Connect the details you already use.</Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.75 }}>When requested, the bot can connect to <Box component="strong" sx={{ color: "text.primary" }}>Melee.gg</Box> for tournament data and <Box component="strong" sx={{ color: "text.primary" }}>Moxfield</Box> for decklist links. These are optional service connections, not a claim that every event or decklist is automatically imported.</Typography>
            </Paper>
          </Box>
        </Container>

        <Box component="section" id="plans" aria-labelledby="plans-title" sx={{ bgcolor: "#e9e4d7", borderTop: "1px solid #d4d0c3", borderBottom: "1px solid #d4d0c3", scrollMarginTop: 28 }}>
          <Container maxWidth="lg" sx={{ py: { xs: 7, md: 9 } }}>
            <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr .72fr" }, gap: 3, alignItems: "end", mb: 4 }}>
              <Box><Typography sx={eyebrowSx}>Monthly plans</Typography><Typography id="plans-title" component="h2" sx={{ ...sectionTitleSx, mt: 1.3 }}>Straightforward pricing for your community.</Typography></Box>
              <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>Three current monthly plans, sized for individual players, stores, and hubs.</Typography>
            </Box>
            <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" }, gap: 1.5 }}>
              {[["Player", "$5", "A monthly plan for players using the bot’s game-community information tools."], ["Store", "$10", "A monthly plan for game stores with supported store profiles and settings."], ["Hub", "$20", "A monthly plan for hubs with supported hub profiles and settings."]].map(([name, price, copy], index) => (
                <Paper key={name} component="article" elevation={0} sx={{ p: { xs: 2.5, sm: 3 }, bgcolor: "background.paper", border: "1px solid", borderColor: "divider", borderRadius: 3, ...(index === 1 ? { borderTop: "4px solid", borderTopColor: "primary.main" } : {}) }}>
                  <Typography sx={eyebrowSx}>{name}</Typography>
                  <Typography sx={{ mt: 1.3, fontFamily: '"Manrope", sans-serif', fontSize: "2.35rem", fontWeight: 800, letterSpacing: "-.06em" }}>{price}<Box component="span" sx={{ ml: 1, color: "text.secondary", fontFamily: '"DM Sans", sans-serif', fontSize: ".9rem", fontWeight: 500, letterSpacing: 0 }}>/ month</Box></Typography>
                  <Typography color="text.secondary" sx={{ mt: 1.2, lineHeight: 1.65 }}>{copy}</Typography>
                </Paper>
              ))}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2.5 }}><Box component="strong" sx={{ color: "text.primary" }}>Plan note:</Box> These are the current monthly plan prices. Contact support with questions about plans or using the bot.</Typography>
          </Container>
        </Box>

        <Container maxWidth="lg">
          <Box component="section" aria-labelledby="community-title" sx={{ py: { xs: 8, md: 11 }, display: "grid", gridTemplateColumns: { xs: "1fr", md: ".9fr 1.1fr" }, gap: { xs: 4, md: 9 }, alignItems: "start" }}>
            <Box>
              <Typography sx={eyebrowSx}>Built around real play</Typography>
              <Typography id="community-title" component="h2" sx={{ ...sectionTitleSx, mt: 1.3 }}>One place for the community’s game information.</Typography>
              <Typography color="text.secondary" sx={{ mt: 2, lineHeight: 1.78 }}>Whether you run events, manage a store or hub, or take part as a player, Metagame Tracker Bot is focused on the information your community submits and views in Discord.</Typography>
            </Box>
            <Box component="ul" sx={{ listStyle: "none", p: 0, m: 0, borderTop: "1px solid", borderColor: "divider" }}>
              {audience.map(([number, title, rest]) => (
                <Box component="li" key={number} sx={{ display: "grid", gridTemplateColumns: "40px 1fr", gap: 1.5, py: 2.1, borderBottom: "1px solid", borderColor: "divider" }}>
                  <Typography sx={{ color: "secondary.main", fontFamily: "monospace", fontWeight: 700, pt: .15 }}>{number}</Typography>
                  <Typography color="text.secondary"><Box component="strong" sx={{ color: "text.primary" }}>{title}</Box>{rest}</Typography>
                </Box>
              ))}
            </Box>
          </Box>

          <Paper component="section" aria-labelledby="contact-title" elevation={0} sx={{ p: { xs: 2.5, md: 4 }, display: "flex", flexDirection: { xs: "column", sm: "row" }, gap: 2, alignItems: { sm: "center" }, justifyContent: "space-between", bgcolor: "primary.main", color: "#f8f6ee", borderRadius: 3 }}>
            <Box><Typography id="contact-title" component="h2" sx={{ fontSize: { xs: "1.5rem", md: "1.8rem" }, fontWeight: 750 }}>Questions about the service?</Typography><Typography sx={{ mt: .8, color: "rgba(248,246,238,.78)" }}>For support or questions about Metagame Tracker Bot, contact the operator by email.</Typography></Box>
            <Link href={mail} sx={{ color: "#f8f6ee", fontWeight: 700, whiteSpace: "nowrap", overflowWrap: "anywhere" }}>metagametrackerbot@gmail.com</Link>
          </Paper>
        </Container>
      </Box>
      <Footer />
    </>
  );
}
