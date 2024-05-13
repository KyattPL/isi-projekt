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

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [hasPremium, setHasPremium] = useState(false);
    const [email, setEmail] = useState("");

    useEffect(() => {
        const lc = Cookies.get('isLoggedIn');
        const pc = Cookies.get('hasPremium');
        const ec = Cookies.get('email');

        if (lc && pc && ec) {
            setIsLoggedIn(lc === 'true');
            setHasPremium(pc === 'true');
            setEmail(ec);
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
            </BrowserRouter>
        </AuthContext.Provider>
    );
}

export default App;