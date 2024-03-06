import React from "react";
import { AppBar, Toolbar, Typography, Box } from "@mui/material";
import logo from "../assets/BubbleMachine_Transparent.png"; // Adjust the path if necessary

const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Box sx={{ display: "flex", alignItems: "center", flexGrow: 1 }}>
          <img src={logo} alt="Logo" style={{ marginRight: 10, height: 50 }} />
          <Typography variant="h3" align="center" style={{ flexGrow: 1 }}>
            BubbleMachine Header Test
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
