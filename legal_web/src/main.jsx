import React from "react";
import { createRoot } from "react-dom/client";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import App from "./App.jsx";
import "./index.css";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#315b48", dark: "#234536", contrastText: "#f8f6ee" },
    secondary: { main: "#c35d39" },
    background: { default: "#f3f0e7", paper: "#faf9f4" },
    text: { primary: "#202925", secondary: "#65706a" },
    divider: "#d4d0c3",
    warning: { main: "#b97922", light: "#fff3d5" }
  },
  typography: {
    fontFamily: '"DM Sans", sans-serif',
    h1: { fontFamily: '"Manrope", sans-serif', fontWeight: 800, letterSpacing: "-.055em" },
    h2: { fontFamily: '"Manrope", sans-serif', fontWeight: 750, letterSpacing: "-.045em" },
    h3: { fontFamily: '"Manrope", sans-serif', fontWeight: 700, letterSpacing: "-.035em" },
    button: { fontWeight: 700, textTransform: "none" }
  },
  shape: { borderRadius: 14 },
  components: {
    MuiButton: { styleOverrides: { root: { borderRadius: 999, padding: "11px 20px" } } },
    MuiLink: { styleOverrides: { root: { textUnderlineOffset: "3px" } } }
  }
});

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
