import React, { useState, useEffect } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Container } from '@mui/material';
import Cookies from 'js-cookie';

import './app.css';
import AuthContext from './AuthContext';
import Header from './Header';
import Home from './Home';
import Login from './Login';
import SearchResults from './SearchResults';
import Premium from './Premium';
import Toast from './Toast';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [hasPremium, setHasPremium] = useState(false);
    const [email, setEmail] = useState("");

    const [loginToastOpen, setLoginToastOpen] = useState(false);
    const [paymentToastOpen, setPaymentToastOpen] = useState(false);

    useEffect(() => {
        if (email) {
            fetch(`http://localhost:8000/is_user_premium/${email}`)
                .then(r => r.json())
                .then(r => {
                    Cookies.set('hasPremium', r);
                    setHasPremium(r);
                });
        }
    }, [email]);

    useEffect(() => {
        const lc = Cookies.get('isLoggedIn');
        const pc = Cookies.get('hasPremium');
        const ec = Cookies.get('email');
        const justLoggedIn = localStorage.getItem('justLoggedIn');

        if (lc && pc && ec) {
            setIsLoggedIn(lc === 'true');
            setHasPremium(pc === 'true');
            setEmail(ec);

            if (justLoggedIn) {
                setLoginToastOpen(true);
                localStorage.removeItem('justLoggedIn');
            }
        }
    }, []);

    return (
        <AuthContext.Provider value={{ isLoggedIn, hasPremium, email, setIsLoggedIn, setHasPremium, setEmail }}>
            <BrowserRouter>
                <Header />
                <div className='mainContent'>
                    <Container>
                        <Routes>
                            <Route path="/" exact element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/search-results/:gameName/:tagLine" element={<SearchResults />} />
                            <Route path="/premium" element={isLoggedIn ? <Premium /> : <Navigate to="/" replace={true} />} />
                        </Routes>
                    </Container>
                </div>
                <Toast message="Successfully logged in." isOpen={loginToastOpen} setIsOpen={setLoginToastOpen} />
                <Toast isOpen={paymentToastOpen} setIsOpen={setPaymentToastOpen} />
            </BrowserRouter>
        </AuthContext.Provider>
    );
}

export default App;