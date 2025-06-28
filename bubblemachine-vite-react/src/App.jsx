import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CssBaseline } from "@mui/material";
import HomePage from "./pages/HomePage";
import WaveformVis from "./components/waveform/WaveformVis";
import ErrorPage from "./pages/ErrorPage";
import SplashScreen from "./pages/SplashScreen";
import { ThemeProvider } from "./styles/context/ThemeContext";
import "./styles/App.css";
import MarketingPage from "./pages/marketing-page/MarketingPage";
import LoginPage from "./pages/sign-in/SignIn";
import RegisterPage from "./pages/sign-up/SignUp";
import ProtectedLayout from "./components/layout/ProtectedLayout";
import { useAuthStore } from "./stores/authStore";

const AuthInitializer = ({ onInitialized }) => {
  const initialize = useAuthStore((state) => state.initialize);
  useEffect(() => {
    initialize().then(() => {
      onInitialized();
    });
  }, [initialize, onInitialized]);
  return null;
};

function App() {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <ThemeProvider>
      <CssBaseline />
      {isLoading ? (
        <SplashScreen onLoadComplete={() => setIsLoading(false)} />
      ) : (
        <BrowserRouter>
          <AuthInitializer onInitialized={() => setIsLoading(false)} />
          <Routes>
            <Route path="/" element={<MarketingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/app" element={<ProtectedLayout />}>
              <Route index element={<HomePage />} />
              <Route path="waveform" element={<WaveformVis />} />
            </Route>
            <Route path="*" element={<ErrorPage />} />
          </Routes>
        </BrowserRouter>
      )}
    </ThemeProvider>
  );
}

export default App;