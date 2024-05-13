import React, { useEffect, useContext } from "react";
import { Box, Button, Typography } from "@mui/material";
import Cookies from 'js-cookie';

import './Login.css';
import AuthContext from "./AuthContext";

const Login = () => {
    const { setIsLoggedIn, setHasPremium, setEmail } = useContext(AuthContext);

    useEffect(() => {
        const handleMessage = (event) => {
            if (event.origin !== "http://127.0.0.1:8000") {
                return;
            }
            setEmail(event.data.email);
            setIsLoggedIn(true);
            setHasPremium(event.data.hasPremium === 'True');
            Cookies.set('isLoggedIn', true);
            Cookies.set('hasPremium', event.data.hasPremium === 'True');
            Cookies.set('email', event.data.email);
        };

        window.addEventListener("message", handleMessage);

        return () => {
            window.removeEventListener("message", handleMessage);
        };
    });

    async function initiateGoogleLogin() {
        try {
            const response = await fetch('http://localhost:8000/auth/google/login');
            const data = await response.json();
            const authenticationUrl = data.message;
            window.open(authenticationUrl, '_blank');
        } catch (error) {
            console.error('Error initiating Google login:', error);
        }
    }

    return (
        <Box className="login-page">
            <Box className="login-container">
                <Typography variant="h4" component="div" className="login-title">
                    Log in
                </Typography>
                <Button variant="contained" color="primary" onClick={initiateGoogleLogin} className="login-button">
                    Sign in with Google
                </Button>
            </Box>
        </Box>
    );
};

export default Login;