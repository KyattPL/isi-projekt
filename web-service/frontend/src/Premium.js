import React, { useContext, useEffect } from "react";
import { Box, Button, Typography } from "@mui/material";
import Cookies from 'js-cookie';

import './Premium.css';
import AuthContext from "./AuthContext";

function Premium() {
    const { email } = useContext(AuthContext);

    useEffect(() => {
        const checkPaymentStatus = async () => {
            const response = await fetch(`http://localhost:8000/get_payment_url/${email}`);
            const data = await response.json();

            if (data !== 'NO_URL') {
                window.location.href = data;
            }
        };

        const intervalId = setInterval(checkPaymentStatus, 5000);
        return () => clearInterval(intervalId);
    });

    const sendPayuRequest = async () => {
        await fetch(`http://localhost:8000/buy_premium/${email}`);
    };

    return (
        <Box className="premium-page" height="calc(100vh - 60px)">
            <Box className="premium-container">
                <Typography variant="h4" component="div" className="premium-title">
                    Upgrade to Premium
                </Typography>
                <Typography variant="body1" component="div" className="premium-description">
                    By buying premium, you get a great in-depth analysis on demand, priority support, and more exclusive features.
                </Typography>
                <Button variant="contained" color="primary" className="premium-button" onClick={sendPayuRequest}>
                    Buy Premium
                </Button>
            </Box>
        </Box>
    );
}

export default Premium;