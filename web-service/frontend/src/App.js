import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Container } from '@mui/material';

import Header from './Header';
import Home from './Home';
import Login from './Login';
import SearchResults from './SearchResults';

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Container>
        <Routes>
          <Route path="/" exact element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/search-results/:gameName/:tagLine" element={<SearchResults />} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
}

export default App;