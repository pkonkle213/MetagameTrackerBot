import React from "react";
import { Box, Link, Paper, Stack, Typography } from "@mui/material";

const email = "mailto:metagametrackerbot@gmail.com";

function LegalHeader() {
  return (
    <Box component="header" sx={{ py: 2, px: .5 }}>
      <Link href="/" color="primary.main" sx={{ fontWeight: 750, fontSize: ".98rem" }}>MetaGameTracker Bot</Link>
    </Box>
  );
}

function LegalFooter({ type }) {
  return (
    <Box component="footer" sx={{ color: "text.secondary", pb: 3 }}>
      <Stack component="nav" aria-label="Legal pages" direction="row" spacing={{ xs: 2, sm: 3 }} flexWrap="wrap">
        <Link href="/privacy" color="inherit">Privacy Policy</Link>
        <Link href="/terms" color="inherit">Terms of Service</Link>
        <Link href={email} color="inherit">{type === "privacy" ? "Privacy and legal contact" : "Legal contact"}</Link>
      </Stack>
    </Box>
  );
}

function PrivacyContent() {
  return (
    <>
      <Typography component="h1" variant="h1" sx={{ fontSize: { xs: "2.25rem", sm: "2.8rem" }, mt: 3 }}>Privacy Policy</Typography>
      <Typography className="updated" color="text.secondary" sx={{ fontSize: ".95rem", mb: 3 }}>Effective date: October 25, 2026</Typography>
      <Typography paragraph>This policy explains how Phillip Konkle (“the operator,” “we,” or “us”) handles information when you use MetaGameTracker Bot (“the Bot”) in Discord servers. The operator is based in Ohio, United States.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>1. Information the Bot handles</Typography>
      <Box component="ul" sx={listSx}>
        <li><strong>Discord and command information:</strong> Discord user, server, category, and channel IDs; command names and timestamps; and whether the user had certain Bot roles when a command was used. Discord may also provide usernames or display names needed to operate a command.</li>
        <li><strong>Game and event information:</strong> player names, archetypes, event dates and names, tournament results, pairings, standings, and information submitted through Bot commands and forms.</li>
        <li><strong>Store and hub information:</strong> server names and IDs, owner names and Discord IDs, store addresses, profile settings, and role assignments.</li>
        <li><strong>Integration credentials and links:</strong> Melee.gg client credentials that a store operator chooses to provide, tournament identifiers, and Moxfield decklist links submitted to the Bot. Melee.gg credentials are used to request tournament data for the store.</li>
        <li><strong>Files and submission data:</strong> CSV, text, and Melee tournament data may be processed through Replit Object Storage as part of a submission. Temporary processing files may be removed after processing; the resulting event records may remain in the database.</li>
      </Box>
      <Typography component="h2" variant="h2" sx={h2Sx}>2. How information is used</Typography>
      <Typography paragraph>Information is used to provide Bot features, accept and organize game-event submissions, generate reports, manage store and hub settings and roles, connect to Melee.gg or Moxfield when requested, maintain command and error logs, protect the service, and respond to support or deletion requests.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>3. Service providers and sharing</Typography>
      <Box component="ul" sx={listSx}>
        <li><strong>Discord:</strong> provides the platform through which the Bot receives interactions and sends replies.</li>
        <li><strong>Replit:</strong> hosts the Bot and provides Object Storage used for some file-processing workflows.</li>
        <li><strong>Replit PostgreSQL:</strong> the Bot stores operational data in a PostgreSQL database hosted by Replit.</li>
        <li><strong>Melee.gg and Moxfield:</strong> the Bot may contact these services when a user requests tournament-data or decklist processing. Those services handle information under their own terms and privacy practices.</li>
      </Box>
      <Typography paragraph>We do not sell personal information. Information may be visible to people in a Discord server when a command posts a response there. The Bot operator can access stored data for administration and can use the restricted database-download command to export it.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>4. Retention</Typography>
      <Typography paragraph>The operator’s current retention practice is to keep database records indefinitely. You may request deletion by emailing <Link href={email}>metagametrackerbot@gmail.com</Link> and including the Discord ID associated with the records. The operator will review the request and may need additional information to identify the records. Some information may remain in backups or in Discord or third-party systems that the operator does not control.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>5. Security</Typography>
      <Typography paragraph>The Bot uses access controls and hosting/database services to operate, and its PostgreSQL database is hosted by Replit. No internet service or storage method can be guaranteed completely secure. Do not submit passwords or credentials that you are not authorized to share.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>6. Your choices and requests</Typography>
      <Typography paragraph>You can stop using the Bot or ask the server administrator to remove it from a server. For access, correction, or deletion requests concerning information held by the operator, contact <Link href={email}>metagametrackerbot@gmail.com</Link> and include your Discord ID with deletion requests. Rights available to you depend on applicable law.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>7. Children</Typography>
      <Typography paragraph>You must meet Discord’s minimum age requirements and any higher minimum age that applies where you live. The Bot is not intended for use by anyone who is not legally permitted to use Discord.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>8. Changes and contact</Typography>
      <Typography paragraph>This policy may be updated as the Bot or its data practices change. The effective date above will be revised when an update is made. Questions about this policy can be sent to <Link href={email}>metagametrackerbot@gmail.com</Link>.</Typography>
      <Typography><strong>Operator:</strong> Phillip Konkle, Ohio, United States.</Typography>
    </>
  );
}

function TermsContent() {
  return (
    <>
      <Typography component="h1" variant="h1" sx={{ fontSize: { xs: "2.25rem", sm: "2.8rem" }, mt: 3 }}>Terms of Service</Typography>
      <Typography className="updated" color="text.secondary" sx={{ fontSize: ".95rem", mb: 3 }}>Effective date: October 25, 2026</Typography>
      <Typography paragraph>These Terms of Service (“Terms”) govern your use of MetaGameTracker Bot (“the Bot”), operated by Phillip Konkle in Ohio, United States. By inviting, configuring, or using the Bot, you agree to these Terms. If you do not agree, do not use the Bot or ask a server administrator to remove it.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>1. What the Bot does</Typography>
      <Typography paragraph>The Bot provides tools for game communities, stores, and hubs to submit and view event information, player names, archetypes, tournament results, reports, and related settings. It may assign configured Discord roles, process submitted files, and connect to third-party services such as Melee.gg and Moxfield. Features may change or be unavailable.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>2. Eligibility and server permissions</Typography>
      <Typography paragraph>You must meet Discord’s minimum age requirements and any higher minimum age required where you live. You are responsible for following Discord’s terms and rules. If you invite or configure the Bot for a server, you must have authority to do so and are responsible for the permissions granted to it and for notifying server members about its use.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>3. Your submissions and responsibilities</Typography>
      <Typography paragraph>You are responsible for the information and files you submit. You must have the right and any required permission to provide player, event, store, or tournament information and any credentials you enter. Do not submit passwords or credentials that you are not authorized to share. Submissions must be lawful, accurate to the best of your knowledge, and consistent with the rules of your Discord server.</Typography>
      <Typography paragraph>You retain any rights you already have in your submissions. You give the operator permission to host, process, store, and display them only as needed to operate, maintain, and improve the Bot and its requested features. Bot replies may be visible to other members of the relevant Discord server.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>4. Acceptable use</Typography>
      <Typography paragraph>You may not use the Bot to violate law or third-party rights; submit malicious files or unauthorized credentials; interfere with the Bot, its infrastructure, or another server; attempt to gain unauthorized access to data; or abuse the Bot’s commands, integrations, or database-export features. The database-download command is limited to authorized use by the operator.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>5. Third-party services</Typography>
      <Typography paragraph>The Bot depends on Discord, Replit hosting, Replit Object Storage, a PostgreSQL database hosted by Replit, and (when requested) Melee.gg and Moxfield. Those services are governed by their respective terms and policies. The operator is not responsible for their availability or practices.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>6. Availability and changes</Typography>
      <Typography paragraph>The Bot is provided without an uptime or availability guarantee. The operator may change, suspend, or discontinue any feature, or restrict access when reasonably needed to protect the service, comply with law, or address misuse. The operator may update these Terms by posting a revised version here and changing the effective date. Continued use after an update means you accept the revised Terms to the extent permitted by law.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>7. No professional advice</Typography>
      <Typography paragraph>The Bot provides game-event tracking and information tools. Its reports and outputs are provided for informational purposes and are not legal, financial, medical, or other professional advice. You are responsible for checking that submitted information and generated reports are suitable for your purposes.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>8. Disclaimers and liability</Typography>
      <Typography paragraph>To the maximum extent permitted by law, the Bot is provided “as is” and “as available,” without warranties of any kind. The operator does not warrant that information will be complete, accurate, uninterrupted, or error-free. Nothing in these Terms excludes rights or liability that cannot lawfully be excluded.</Typography>
      <Typography paragraph>To the maximum extent permitted by law, the operator will not be liable for indirect, incidental, special, consequential, exemplary, or punitive losses arising from use of the Bot. The operator’s total liability for claims relating to the Bot will not exceed US$100, except where applicable law does not permit that limitation.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>9. Suspension and termination</Typography>
      <Typography paragraph>You can stop using the Bot at any time. The operator may suspend or terminate access for a violation of these Terms or to protect the Bot or its users. Data handling and deletion requests are described in the <Link href="/privacy">Privacy Policy</Link>.</Typography>
      <Typography component="h2" variant="h2" sx={h2Sx}>10. Governing law and contact</Typography>
      <Typography paragraph>These Terms are governed by the laws of the State of Ohio, United States, without regard to conflict-of-law rules, subject to any mandatory rights that apply where you live. Questions about these Terms may be sent to <Link href={email}>metagametrackerbot@gmail.com</Link>.</Typography>
      <Typography><strong>Operator:</strong> Phillip Konkle, Ohio, United States.</Typography>
    </>
  );
}

const h2Sx = { mt: 4, mb: 1.2, color: "#234536", fontSize: "1.28rem", lineHeight: 1.3 };
const listSx = { pl: 3, "& li": { mb: 1.1, lineHeight: 1.78 }, "& li::marker": { color: "#c35d39" } };

export default function LegalPage({ type }) {
  const isPrivacy = type === "privacy";
  return (
    <>
      <LegalHeader />
      <Paper component="main" elevation={0} className="legal-copy" sx={{ p: { xs: 2.5, sm: 4, md: 6 }, my: 2, bgcolor: "background.paper", border: "1px solid", borderColor: "divider", boxShadow: "0 12px 36px rgba(42,55,43,.06)", borderRadius: 3 }}>
        <Box component="p" sx={{ m: 0, p: 2, color: "#713f00", bgcolor: "#fff3d5", border: "1px solid #ead39a", borderRadius: 1.5, lineHeight: 1.65 }}>
          <strong>Legal notice:</strong> {isPrivacy ? "This document is general information, not legal advice. Have a qualified attorney review it for your circumstances." : "These terms are a general draft, not legal advice. Have a qualified attorney review them before relying on them."}
        </Box>
        {isPrivacy ? <PrivacyContent /> : <TermsContent />}
      </Paper>
      <LegalFooter type={type} />
    </>
  );
}
