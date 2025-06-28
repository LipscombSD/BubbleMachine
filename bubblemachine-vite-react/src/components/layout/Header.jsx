import { useState } from "react";
import {
  AppBar,
  Box,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  Avatar,
} from "@mui/material";
import {
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  AccountCircle as AccountIcon,
  MoreVert as MoreVertIcon,
} from "@mui/icons-material";
import { useTheme } from "../../styles/context/ThemeContext.jsx";
import { headerStyles } from "../../styles/context/LayoutStyles.jsx";
import logo from "../../assets/BubbleMachine_Transparent.png";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";

const MusicNote = ({ delay, position }) => (
  <Box
    sx={{
      ...headerStyles.musicNote,
      animationDelay: `${delay}s`,
      left: `${position.x}%`,
      top: `${position.y}%`,
    }}
  >
    {["♪", "♫", "♩", "♬"][Math.floor(Math.random() * 4)]}
  </Box>
);

const Header = () => {
  const { darkMode, setDarkMode } = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const [moreAnchorEl, setMoreAnchorEl] = useState(null);
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuthStore();
  const [musicNotes] = useState(() =>
    Array.from({ length: 8 }, (_, i) => ({
      id: i,
      delay: Math.random() * 8,
      position: {
        x: Math.random() * 100,
        y: Math.random() * 100,
      },
    }))
  );

  const handleLogout = () => {
    logout();
    navigate("/");
    setAnchorEl(null);
  };

  return (
    <AppBar sx={headerStyles.appBar(darkMode)}>
      <Toolbar sx={headerStyles.toolbar}>
        {musicNotes.map((note) => (
          <MusicNote
            key={note.id}
            delay={note.delay}
            position={note.position}
          />
        ))}
        <Box sx={headerStyles.logoContainer}>
          <img src={logo} alt="Logo" style={headerStyles.logo} />
          <Box component="span" sx={headerStyles.brandText(darkMode)}>
            BubbleMachine
          </Box>
        </Box>
        <Box sx={headerStyles.navContainer}>
          <Tooltip
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            <IconButton
              onClick={() => setDarkMode(!darkMode)}
              sx={headerStyles.iconButton}
            >
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="More options">
            <IconButton
              onClick={(e) => setMoreAnchorEl(e.currentTarget)}
              sx={headerStyles.iconButton}
            >
              <MoreVertIcon />
            </IconButton>
          </Tooltip>
          {isAuthenticated && (
            <Tooltip title="Account settings">
              <IconButton
                onClick={(e) => setAnchorEl(e.currentTarget)}
                sx={{
                  ...headerStyles.iconButton,
                  border: "2px solid #1976d2",
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    bgcolor: "transparent",
                  }}
                >
                  <AccountIcon />
                </Avatar>
              </IconButton>
            </Tooltip>
          )}
        </Box>
        {isAuthenticated && (
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            PaperProps={{
              sx: {
                backgroundColor: darkMode ? "#1A1A2E" : "#FFFFFF",
                borderRadius: "8px",
                mt: 1,
              },
            }}
          >
            <MenuItem onClick={handleLogout}>Log Out</MenuItem>
          </Menu>
        )}
        <Menu
          anchorEl={moreAnchorEl}
          open={Boolean(moreAnchorEl)}
          onClose={() => setMoreAnchorEl(null)}
          PaperProps={{
            sx: {
              backgroundColor: darkMode ? "#1A1A2E" : "#FFFFFF",
              borderRadius: "8px",
              mt: 1,
            },
          }}
        >
          <MenuItem onClick={() => setMoreAnchorEl(null)}>
            About BubbleMachine
          </MenuItem>
          <MenuItem onClick={() => setMoreAnchorEl(null)}>More</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;