import React, { useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Container } from '@mui/material';

import './app.css';
import AuthContext from './AuthContext';
import Header from './Header';
import Home from './Home';
import Login from './Login';
import SearchResults from './SearchResults';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // Example function to simulate login
    const handleLogin = () => {
        setIsLoggedIn(true);
    };

    return (
        <AuthContext.Provider value={{ isLoggedIn, handleLogin }}>
            <BrowserRouter>
                <Header />
                <div className='mainContent'>
                    <Container>
                        <Routes>
                            <Route path="/" exact element={<Home />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/search-results/:gameName/:tagLine" element={<SearchResults />} />
                        </Routes>
                    </Container>
                </div>
            </BrowserRouter>
        </AuthContext.Provider>
    );
}

export default App;